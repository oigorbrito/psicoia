# PSICOIA — resultado do Bloco 13: motor de recuperação

**Estado: PARTIAL (não CLOSED).** A avaliação independente dá vantagem ao Qwen em ranking neste conjunto sintético, mas não há configuração que passe todos os gates previamente fixados: nenhuma das duas recuperações atuais abstém nas consultas sem resposta, o Phi falha os mínimos EN, o Qwen excede o orçamento de p95 PT-BR e a integração real não concluiu no orçamento de 180 s por turno devido à etapa de geração Qwen/OpenAI-compatível. O fallback de embeddings Phi é preservado; não foi declarado um vencedor operacional novo.

## Proveniência, branch e baseline

- Worktree: `D:/projetos/psicoia-reconciliation`, branch local `reconciliation/psicoia-block13-retrieval`.
- HEAD inicial: `16f3baf40039fa943708bbe8b69e18ab53e4886d` (commit do Bloco 12 informado pelo usuário).
- HEAD técnico final, antes do commit deste relatório: `d794c7a` (`test(retrieval): add block13 local recovery benchmark`). O commit de entrega deste relatório é posterior e altera apenas documentação/evidência.
- Commits locais do Bloco 13: `cfbac98` (fixture e critérios pré-registrados), `74a75eb` (otimização para categoria única) e `d794c7a` (diagnóstico e benchmark reproduzíveis).
- O arquivo `tests/backend_block12_local_pipeline_e2e.py`, a fixture Block 12 e `PSICOIA_BLOCK12_RESULT.md` são idênticos ao HEAD inicial (`git diff --exit-code 16f3baf... -- ...` passou). O baseline não foi reescrito nem usado como substituto dos testes Block 13. Nenhum push, PR, merge ou alteração em `main`.

## Critérios definidos antes da execução

A fixture e `criteria_v1.json` foram versionados no commit `cfbac98`, antes dos ensaios dos modelos. SHA-256:

- Fixture `tests/fixtures/block13/retrieval_eval_v1.json`: `4adc0e7174c35ebf2d3d76605cb77cbd69c446f7f8676cf586d351a8165a7656`.
- Critérios `tests/fixtures/block13/criteria_v1.json`: `4ad61092a03235ca7c7782302e8bc1e51a98e97a6fbbc59ed1b1bc36d2ea8ed4`.

Conjunto novo, sintético e não clínico, criado para este bloco: 12 documentos por idioma e 32 consultas — **12 teste + 4 calibração por idioma**. As dez consultas respondíveis de cada teste incluem perguntas diretas, paráfrases, uma consulta ambígua, distratores lexicais e semânticos e contexto longo; duas não têm resposta relevante. As strings de consulta e rótulos Block 11/12 não foram reutilizados. A relevância graduada é 3 para alvo, 2 para alternativas aceitáveis ambíguas e 1 para documento semanticamente próximo/secundário; documento não rotulado tem grau 0.

Gates experimentais pré-fixados por idioma: Recall@5 ≥0,90, nDCG@5 ≥0,80, contexto útil no prompt ≥0,90 e taxa de falso contexto em consultas sem resposta ≤0,10. Limiares de abstinência só podem ser escolhidos no split de calibração (grade 0,10–0,70) e avaliados no teste bloqueado. Orçamentos locais experimentais, **não SLOs do produto**: embedding de consulta p95 ≤2 s; indexação de 12 skills/idioma ≤120 s; cold start ≤120 s; chamada integrada ≤180 s por turno observado.

## Configuração e hardware medidos

- Candidatos disponíveis e efetivamente testados: `phi4-mini:3.8b` e `qwen3.5:4b`, ambos com mean pooling por `llama-server`, `-ngl 0` (CPU), contexto 512; lotes do indexador com 12 entradas. Dimensões: 3.072 (Phi) e 2.560 (Qwen).
- `ollama list` não mostrou modelo local dedicado a embeddings compatível. Nenhum modelo foi baixado. Nenhum serviço pago, chave real ou dado clínico foi usado.
- Máquina observada: 8 CPUs lógicas, 15,87 GiB RAM, NVIDIA GeForce GTX 1650 com 4.096 MiB VRAM.
- Diagnóstico Qwen: primeiro cold start observado de `llama-server` **76,7 s**; nova inicialização com cache de arquivos aquecido **17,0 s** no benchmark. O Qwen embedding server sozinho atingiu aproximadamente **4,04 GiB working set** e apenas **0,88 GiB de RAM disponível (94% em uso)**. Com a cópia Qwen do Ollama carregada simultaneamente, havia dois processos `llama-server.exe` (embedding e chat), o embedding estava em 3,37 GiB working set, o runner reportava 1,82 GB de VRAM e `nvidia-smi` observou 2.555 MiB usados/1.381 MiB livres. Esses snapshots indicam pressão de recursos; não provam paginação nem OOM.
- O servidor de embeddings usa CPU; a geração Qwen usa o runner Ollama e GPU/CPU. O fluxo web espera recuperação antes da geração; as inferências não são concorrentes no caminho normal. O ensaio de estresse simultâneo mediu 1,285 s para embedding e 31,64 s para chat aquecido (parede 31,65 s), sem evidência de que contenção seja a causa única do timeout. Utilização GPU foi amostrada; não foi coletada série temporal de utilização CPU.

## Timeout Qwen: diagnóstico e correção limitada

O timeout não foi causado por uma única consulta de embedding que levasse 300 s. No teste medido, embeddings de consulta individuais foram de aproximadamente 0,6–3,8 s; a tokenização individual ficou em milissegundos. Indexação Qwen (dois lotes de 12 vetores, merge + retrieval) levou 56,4 s EN e 74,4 s PT-BR no benchmark, abaixo do limite de 120 s/idioma.

A causa dominante observada na integração foi a geração Qwen pelo endpoint OpenAI-compatível: respostas com `content` público vazio e texto apenas no campo de raciocínio separado, seguido de nova tentativa. `OpenAIAPIBackend` corretamente não converte raciocínio interno em resposta pública. Na tentativa Qwen/Qwen pós-otimização, a rota de abertura levou 180,0 s: indexação PT-BR 54,69 s + 15,02 s, embedding da consulta 0,318 s; uma chamada de chat levou 54,07 s, terminou `stop` com 345 tokens, mas teve 0 caracteres públicos e 649 caracteres no campo de raciocínio. Outra chamada de chat ainda estava em andamento ao atingir o orçamento. A tentativa Phi/Qwen também excedeu 180 s com uma chamada de chat ainda em andamento.

O diagnóstico separado registrou cold chat Qwen de 124,0 s para 256 tokens, `finish_reason=length`, conteúdo público vazio e 879 caracteres de raciocínio. Na tentativa Phi/Qwen com modelo de chat previamente aquecido e sem repetir o benchmark offline, o caminho da primeira visita mediu 66,82 + 19,54 s de indexação, 0,535 s de embedding de consulta e 93,69 s no provedor de chat: soma observada **180,58 s**, ligeiramente além do orçamento de 180 s, antes de overhead de rota/DB. A resposta do chat tinha `finish_reason=stop`, mas zero texto público e 1.738 caracteres no campo de raciocínio. Na tentativa Qwen/Qwen, os componentes concluídos somaram 124,10 s antes de outra chamada de chat continuar até o limite. Isso distingue latência de indexação fria de geração, sem evidência de uma requisição individual de embedding de 300 s. `think:false` em uma requisição sintética ao endpoint `/v1/chat/completions` não suprimiu o raciocínio; a API usada pelo produto não ofereceu uma configuração compatível demonstrada para resolver a saída. Não se aumentou o timeout. Os valores foram coletados em uma máquina local e não provam comportamento de todos os servidores/configurações Qwen.

Correção funcional estritamente limitada em `src/sample/skill_manager.py`: quando há exatamente uma categoria coarse e `n >= 1`, a chamada ao seletor é omitida, pois ela não pode alterar o único conjunto candidato que o fallback já retornaria. Com mais de uma categoria, o caminho anterior continua. Dois testes verificam ausência da chamada redundante e preservação da seleção coarse concorrente. Essa é uma exceção funcional à regra de cópia literal, autorizada pelo pedido do Bloco 13 e restrita à categoria singleton; não altera prompts, conteúdo clínico, dados nem o conjunto de skills selecionado. A otimização removeu a etapa redundante, mas não resolveu a saída vazia/latência da geração, portanto não é apresentada como solução do timeout integral.

Veja `reports/block13/qwen_timeout_diagnostic.json` e `reports/block13/pipeline_timeout_trace.json` para os rastros agregados; os logs detalhados de servidor temporários ficaram fora do repositório.

## Benchmark de recuperação

Comando reproduzível no ambiente local já provisionado:

```text
D:/temp/psicoia-block10-venv/Scripts/python.exe tests/block13/benchmark_retrieval.py
```

O script carrega a fixture/critérios versionados, inicia cada modelo instalado isoladamente, mede tokenização por texto, embedding individual de cada documento e consulta, lotes de indexação, retrieval real do `SkillManager`, ordenação cosseno, renderização do prompt, memória e VRAM. `reports/block13/retrieval_benchmark_local.json` contém traços e métricas completos (SHA-256 `356b70e4c0770d1909e316f830ea0efa43524d61ed7be67b1f034c95b90b21d9`). Foram 10 consultas respondíveis + 2 sem resposta por idioma no teste; o conjunto de calibração teve 3 respondíveis + 1 sem resposta por idioma. Intervalos de 95% Wilson são apresentados para taxas binárias; diferenças são pareadas por query em 10.000 bootstraps, seed 13013. Amostra pequena: intervalos apenas descritivos.

| Modelo | Idioma | Recall@1 | Recall@5 | MRR | nDCG@5 | útil no prompt | p95 consulta | p95/doc | index 12 skills |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Phi mean | EN | 0,70 | 0,80 | 0,75 | 0,7251 | 0,80 | 1.523 ms | 1.100 ms | 40,1 s |
| Phi mean | PT-BR | 1,00 | 1,00 | 1,00 | 0,9196 | 1,00 | 1.392 ms | 1.302 ms | 47,1 s |
| Qwen mean | EN | 1,00 | 1,00 | 1,00 | 0,9710 | 1,00 | 1.840 ms | 1.216 ms | 56,4 s |
| Qwen mean | PT-BR | 0,90 | 1,00 | 0,95 | 0,9605 | 1,00 | 2.748 ms | 3.799 ms | 74,4 s |

As taxas Recall@5 têm IC Wilson 95% [0,4902; 0,9433] para Phi EN e [0,7225; 1,0000] para Phi PT-BR e ambos Qwen; falso contexto 2/2 sem resposta tem IC [0,3424; 1,0000] em cada idioma/modelo. Throughput observado de indexação (24 entradas-vetor por idioma: merge + retrieval) foi 0,598/0,510 entradas/s Phi EN/PT-BR e 0,425/0,322 Qwen EN/PT-BR; consultas isoladas, 1,544/1,423 e 1,225/0,806 consultas/s, respectivamente. Overhead não-embedding do retrieval teve p95 de 39/39 ms Phi e 38/42 ms Qwen; renderização do prompt teve p95 abaixo de 2,1 ms. Tokenização individual teve p95 entre 1,1 e 5,1 ms, dependendo do modelo/idioma.

Diferença pareada Qwen−Phi (10 consultas respondíveis por idioma; bootstrap 95%, seed 13013):

- EN: Recall@5 **+0,20** [0,00; 0,50], MRR **+0,25** [0,00; 0,50], nDCG@5 **+0,2459** [0,0000; 0,5000].
- PT-BR: Recall@5 **0,00** [0,00; 0,00], MRR **−0,05** [−0,15; 0,00], nDCG@5 **+0,0409** [−0,0817; 0,1754].

Qwen sem limiar passa os gates de ranking/utilidade neste fixture, mas não o orçamento p95 PT-BR. Phi falha Recall@5 e nDCG@5 EN. Mais importante, o fluxo atual sempre insere top-5; portanto as duas consultas sem resposta por idioma resultaram em **100% de falso contexto** em ambos candidatos, acima do limite pré-registrado. Um limiar de 0,70, calibrado somente no split de calibração, zerou falso contexto Qwen EN no teste, mas reduziu Qwen EN para Recall@5 0,80/nDCG@5 0,771/útil 0,80; em PT-BR continuou falso contexto 1,00. Phi teve especificidade zero no split de calibração e falso contexto 1,00. Não se introduziu threshold no app: o split pequeno não justifica configurá-lo operacionalmente.

## Seleção e fluxo integrado

- **Não há vencedor que passe a regra de seleção completa.** Qwen é melhor no ranking desta fixture, especialmente EN, mas excede p95 PT-BR, não passa a abstinência em PT-BR e não concluiu integração real com Qwen como chat. O ensaio Qwen+Qwen excedeu 180 s. Não é aprovado só pelo Recall.
- **Phi é preservado como fallback operacional** por ser a configuração de embeddings do E2E completo aprovado no relatório/commit do Bloco 12. Isso é preservação do baseline, não uma validação nova nem fechamento Block 13.
- Reexecuções Block 13 com fixture nova, chat Qwen e embedding Phi excederam o orçamento de 180 s na criação sintética da primeira visita. Uma tentativa com Qwen previamente aquecido e benchmark offline separado mostrou indexação local de 66,82 s + 19,54 s, embedding de consulta 0,535 s e geração de 93,69 s; o provedor terminou sem texto público (0 caracteres, 1.738 caracteres no campo de raciocínio) no limite da rota. Outra tentativa terminou com a chamada de chat ainda em andamento. A criação da visita pode ter iniciado gravações antes do timeout; persistência e estado após restart não foram verificados nessa falha. Portanto não houve novo PASS para `entrada → embedding → recuperação → prompt → geração → persistência → reinicialização → leitura`; alternância e rollback/recovery com a configuração Block 13 também não foram validados após o estágio de abertura. A execução anterior do Bloco 12 (659,699 s, Phi embeddings, Qwen chat aquecido, fixtures Block 12) continua como evidência de baseline, não substitui essa falha com a fixture independente.
- O E2E novo não persistiu resposta e não chegou aos testes de restart nem à injeção de falhas; eles não são reivindicados como aprovados no Bloco 13. A suíte sintética de API do projeto passou separadamente.
- Não foram substituídos índices existentes nem alterada configuração de runtime. Uma troca futura exige versão explícita de índice/cache e estratégia de reindexação; não foi necessária para manter o fallback atual.

## Regressões e comandos

| Comando | Resultado |
|---|---|
| `PYTHONPATH=src python -m pytest -q` | **47 passed** |
| `D:/temp/psicoia-block10-venv/Scripts/python.exe tests/backend_e2e.py` | **PASS**: 16 rotas sintéticas, persistência/ownership e rollback |
| `python -m pytest -q evidence-repo-template/tests/test_harness.py` | **4 passed** |
| `python scripts/harness.py` | arquivos/testes locais **PASS**; licença **GAP**; controles externos **UNKNOWN_EXTERNAL** |
| `D:/temp/psicoia-block10-venv/Scripts/python.exe -m py_compile ...` | **PASS** para arquivos alterados do Bloco 13 |
| `git diff --check` | **PASS** |
| E2E local via `tests/block13/trace_qwen_e2e_timeout.py`, Qwen/Qwen e Phi/Qwen, orçamento 180 s | **GAP**: timeout na geração da abertura; rastros em `pipeline_timeout_trace.json` |

Harness continua limitado e não é auditoria/conformidade. Build/frontend não foi reexecutado; não houve mudança frontend. Não houve avaliação clínica, catálogo completo, revisão linguística independente ou ensaio em produção. Mean pooling de modelos generativos e fixture sintética não comprovam qualidade em catálogo clínico ou eficácia clínica.

## Fechamento

**PARTIAL.** Os critérios de recuperação e latência integrada não foram todos satisfeitos; o fluxo completo com a configuração selecionada não foi revalidado após restart. O fallback Phi permanece sem troca de configuração. Para avançar, é necessário resolver a emissão de resposta pública/latência do provedor local Qwen sem expor raciocínio, avaliar abstinência em corpus independente maior, manter p95 PT-BR dentro do orçamento e repetir todo o ciclo integrado. Não se ampliou timeout nem se alegou prontidão clínica ou de produção.
