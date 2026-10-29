# PSICOIA — resultado do Bloco 13: motor de recuperação

**Estado: PARTIAL (não CLOSED).** Nenhuma configuração passou todos os gates: ambas inseriram contexto irrelevante nas consultas sem resposta; Phi falhou os mínimos de ranking EN; Qwen teve bom ranking sintético e p95 abaixo de 2 s na repetição, mas a integração HTTP real não concluiu em 180 s devido à geração Qwen/OpenAI-compatível. Uma execução anterior registrou p95 PT-BR Qwen de 2,75 s com 1,72 GiB de RAM disponível; a repetição mediu 1,77 s com 2,89 GiB disponíveis. Nenhuma amostra registrou um modelo Ollama carregado, e essa diferença não demonstra causalidade. O fallback Phi é preservado; não há novo vencedor operacional.

## Proveniência, branch e baseline

- Worktree: `D:/projetos/psicoia-reconciliation`, branch local `reconciliation/psicoia-block13-retrieval`.
- Baseline funcional Block 12: `16f3baf40039fa943708bbe8b69e18ab53e4886d`. HEAD do worktree no início deste trabalho: `cfbac98`, descendente do baseline, na branch local `reconciliation/psicoia-block13-retrieval`.
- A repetição isolada corrigida foi executada no commit `2c08740` (`docs: record block13 recovery evaluation`); os artefatos desta atualização documentam essa execução sem alterar código de produto.
- Commits locais relevantes: `cfbac98` (fixture/critérios pré-registrados), `74a75eb` (atalho para categoria singleton), `d794c7a` (diagnóstico e benchmark), `2c08740` (relatório e rastros iniciais), além deste commit de evidência.
- `tests/backend_block12_local_pipeline_e2e.py`, fixture Block 12 e `PSICOIA_BLOCK12_RESULT.md` permanecem idênticos ao baseline `16f3baf` (comparação pontual verificada). Nenhum push, PR, merge ou alteração em `main`.

## Critérios definidos antes da execução

A fixture e `criteria_v1.json` foram versionados no commit `cfbac98`, antes dos ensaios dos modelos. SHA-256:

- Fixture `tests/fixtures/block13/retrieval_eval_v1.json`: `4adc0e7174c35ebf2d3d76605cb77cbd69c446f7f8676cf586d351a8165a7656`.
- Critérios `tests/fixtures/block13/criteria_v1.json`: `4ad61092a03235ca7c7782302e8bc1e51a98e97a6fbbc59ed1b1bc36d2ea8ed4`.

Conjunto novo, sintético e não clínico, criado para este bloco: 12 documentos por idioma e 32 consultas — **12 teste + 4 calibração por idioma**. As dez consultas respondíveis de cada teste incluem perguntas diretas, paráfrases, uma consulta ambígua, distratores lexicais e semânticos e contexto longo; duas não têm resposta relevante. As strings de consulta e rótulos Block 11/12 não foram reutilizados. A relevância graduada é 3 para alvo, 2 para alternativas aceitáveis ambíguas e 1 para documento semanticamente próximo/secundário; documento não rotulado tem grau 0.

Gates experimentais pré-fixados por idioma: Recall@5 ≥0,90, nDCG@5 ≥0,80, contexto útil no prompt ≥0,90 e taxa de falso contexto em consultas sem resposta ≤0,10. Limiares de abstinência só podem ser escolhidos no split de calibração (grade 0,10–0,70) e avaliados no teste bloqueado. Orçamentos locais experimentais, **não SLOs do produto**: embedding de consulta p95 ≤2 s; indexação de 12 skills/idioma ≤120 s; cold start ≤120 s; chamada integrada ≤180 s por turno observado.

## Configuração e hardware medidos

- Candidatos disponíveis e efetivamente testados: `phi4-mini:3.8b` e `qwen3.5:4b`, ambos com mean pooling por `llama-server`, `-ngl 0` (CPU), contexto 512; lotes do indexador com 12 entradas. Dimensões: 3.072 (Phi) e 2.560 (Qwen).
- `ollama list` e o cache local visível do Hugging Face não mostraram candidato dedicado a embeddings compatível; havia apenas modelos generativos locais. Nenhum modelo foi baixado. Nenhum serviço pago, chave real ou dado clínico foi usado.
- Máquina observada: 8 CPUs lógicas, 15,87 GiB RAM, NVIDIA GeForce GTX 1650 com 4.096 MiB VRAM.
- Diagnóstico Qwen: primeira prontidão observada de `llama-server` 76,7 s; a repetição isolada, após execuções anteriores terem aquecido os arquivos, mediu 10,84 s Phi e 16,07 s Qwen. O servidor Qwen sozinho atingiu ~4,04 GiB working set e 0,88 GiB de RAM disponível (94% em uso). Com o chat Qwen carregado, dois processos `llama-server.exe` coexistiram; o processo de embedding chegou a 3,37 GiB, o runner reportou 1,82 GB de VRAM e `nvidia-smi` observou 2.555 MiB usados/1.381 MiB livres. São sinais de pressão de recursos, não prova de paginação ou OOM.
- Embedding usa CPU; geração Qwen usa Ollama/GPU-CPU. O fluxo normal aguarda retrieval antes da geração. Um ensaio de estresse separado mediu 1,285 s para embedding e 31,64 s para chat aquecido (parede 31,65 s); isso não demonstra contenção como causa única. GPU foi amostrada; não houve série temporal de CPU.

## Timeout Qwen: diagnóstico e correção limitada

O timeout observado não corresponde a uma única consulta de embedding de 300 s. Na repetição, p95 de query foi 1,40/1,41 s Phi e 1,51/1,77 s Qwen (EN/PT-BR); indexação completa foi 40,61/46,50 s Phi e 49,66/56,33 s Qwen. O primeiro servidor Qwen iniciou em 76,7 s, mas embeddings individuais ficaram na faixa de segundos. Uma execução anterior registrou p95 PT-BR Qwen de 2,75 s com 1,72 GiB disponíveis; a repetição registrou 1,77 s com 2,89 GiB. Os snapshots de ambas mostram `ollama_loaded_models=[]`; a diferença sugere variabilidade local, mas não permite atribuir causa à RAM ou à concorrência.

O bloqueio E2E observado foi a etapa de geração no endpoint OpenAI-compatível: Qwen retornou `content` público vazio e texto apenas no campo de raciocínio; o extrator correto do `OpenAIAPIBackend` recusou publicar raciocínio e o fluxo tentou novamente. Na tentativa Qwen/Qwen, houve 180 s de orçamento, lotes de indexação de 54,69 + 15,02 s, embedding de consulta 0,318 s e primeira chamada de chat de 54,07 s (345 tokens, `stop`, 0 caracteres públicos, 649 de raciocínio); outra chamada estava em andamento no timeout. Na tentativa Phi/Qwen fria, a chamada de chat permaneceu em andamento até o limite. Uma tentativa Phi/Qwen com chat previamente aquecido registrou 66,82 + 19,54 s de indexação, 0,535 s de query e chat de 93,69 s, sem conteúdo público, total observado de componentes 180,58 s.

Em uma repetição adicional Phi/Qwen, com chat aquecido por uma chamada local de 1 token, o benchmark offline também foi executado: a rota de primeira visita atingiu 180,0 s após lotes de embedding de 68,42 + 21,41 s e query de 0,757 s. A primeira chamada Qwen levou 66,28 s, completou com 374 tokens e `stop`, mas tinha 0 caracteres públicos e 1.738 caracteres de raciocínio; uma segunda chamada ainda estava em andamento quando o cliente excedeu 180 s. Isso reforça que o resultado não foi resolvido pelo warm-up e que o caminho de resposta pública é o gargalo integrado observado; não prova que o embedding cause o atraso. O diagnóstico separado mediu cold chat Qwen de 124,0 s/256 tokens com `finish_reason=length`, texto público vazio e 879 caracteres de raciocínio. `think:false` em requisição sintética não suprimiu esse campo. Não se aumentou timeout; as causas são evidência local, não generalização a todos os servidores Qwen.

Correção funcional estritamente limitada em `src/sample/skill_manager.py`: quando há exatamente uma categoria coarse e `n >= 1`, a chamada ao seletor é omitida, pois ela não pode alterar o único conjunto candidato que o fallback já retornaria. Com mais de uma categoria, o caminho anterior continua. Dois testes verificam ausência da chamada redundante e preservação da seleção coarse concorrente. Essa é uma exceção funcional à regra de cópia literal, autorizada pelo pedido do Bloco 13 e restrita à categoria singleton; não altera prompts, conteúdo clínico, dados nem o conjunto de skills selecionado. A otimização removeu a etapa redundante, mas não resolveu a saída vazia/latência da geração, portanto não é apresentada como solução do timeout integral.

Veja `reports/block13/qwen_timeout_diagnostic.json` e `reports/block13/pipeline_timeout_trace.json` para os rastros agregados; os logs detalhados de servidor temporários ficaram fora do repositório.

## Benchmark de recuperação

Execução isolada reproduzível no ambiente local já provisionado (modelo de chat Qwen descarregado antes de iniciar os candidatos):

```text
PSICOIA_BLOCK13_RUN_ID=block13-isolated-20261029T184215 D:/temp/psicoia-block10-venv/Scripts/python.exe tests/block13/benchmark_retrieval.py
```

O artefato primário é `reports/block13/retrieval_benchmark_local_prompt_checked.json` (SHA-256 `ea854674d8200c44cf79fc1313de95f3ca58afacbd546eb4ede8fc2b9dec2606`). Run ID `block13-isolated-20261029T184215`, código em `2c087406737aaf835a061c9fc522c36bbaa8262a`, runner SHA-256 `98ea93cd06b4b3b37f5fccbbffe3e26d9100c5912eb151b5950d0ebb513511b8`; fixture SHA `4adc0e…a7656`, critérios SHA `4ad610…a8ed4`. Blobs: Phi `3c168af1…f0a5db`, Qwen `a9d0a3e1…e2ac50`. O arquivo `retrieval_benchmark_local.json` anterior é preservado como execução preliminar; sua métrica de prompt era menos estrita. Seu p95 Qwen PT-BR de 2,75 s ocorreu com 1,72 GiB de RAM disponível; a repetição atual mediu 1,77 s com 2,89 GiB, sem modelo Ollama reportado como carregado em nenhum dos snapshots. Essa variação é observação, não prova de relação causal. A repetição corrigida verifica nome e descrição de cada skill no prompt efetivamente renderizado. O runner mede tokenização, embeddings, indexação/retrieval real, ranking, renderização, memória e VRAM. Fixture: 10 consultas respondíveis + 2 sem resposta por idioma no teste; calibração: 3 respondíveis + 1 sem resposta. IC Wilson 95%; diferenças pareadas por consulta em 10.000 bootstraps, seed 13013. Amostra pequena: intervalos descritivos.

| Modelo | Idioma | Recall@1 | Recall@5 | MRR | nDCG@5 | útil no prompt | p95 consulta | p95/doc | index/locale |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Phi mean | EN | 0,70 | 0,80 | 0,75 | 0,7251 | 0,80 | 1.395 ms | 1.072 ms | 40,61 s |
| Phi mean | PT-BR | 1,00 | 1,00 | 1,00 | 0,9196 | 1,00 | 1.413 ms | 1.238 ms | 46,50 s |
| Qwen mean | EN | 1,00 | 1,00 | 1,00 | 0,9710 | 1,00 | 1.509 ms | 1.434 ms | 49,66 s |
| Qwen mean | PT-BR | 0,90 | 1,00 | 0,95 | 0,9605 | 1,00 | 1.773 ms | 1.593 ms | 56,33 s |

Todas as p95 de query no ensaio isolado ficaram abaixo de 2 s. Cold-process ready no mesmo run: 10,84 s Phi e 16,07 s Qwen; a primeira inicialização Qwen observada anteriormente foi 76,7 s. Recall@5: Phi EN IC Wilson 95% [0,4902; 0,9433], Phi PT-BR e ambos Qwen [0,7225; 1,0000]. Falso contexto 2/2 sem resposta teve IC [0,3424; 1,0000] em cada modelo/idioma. Throughput de indexação (24 entradas-vetor/locale, merge + retrieval): Phi 0,591/0,516 e Qwen 0,483/0,426 entradas/s (EN/PT-BR); throughput de query: Phi 1,458/1,375 e Qwen 1,453/1,380 consultas/s.
Diferença pareada Qwen−Phi (10 consultas respondíveis por idioma; bootstrap 95%, seed 13013):

- EN: Recall@1 **+0,30** [0,00; 0,60], Recall@5 **+0,20** [0,00; 0,50], MRR **+0,25** [0,00; 0,50], nDCG@5 **+0,2459** [0,0000; 0,5000].
- PT-BR: Recall@1 **−0,10** [−0,30; 0,00], Recall@5 **0,00** [0,00; 0,00], MRR **−0,05** [−0,15; 0,00], nDCG@5 **+0,0409** [−0,0817; 0,1754].

Qwen sem limiar passa os gates de ranking/utilidade neste fixture e, nesta execução isolada, também o orçamento p95 de query. Phi falha Recall@5/nDCG@5 EN. Ambos candidatos inseriram contexto no prompt em 2/2 consultas sem resposta por idioma: **100% falso contexto**, acima do gate 10%. Um limiar 0,70 calibrado em apenas 3 positivos/1 negativo por idioma zerou falso contexto Qwen EN no teste, mas reduziu Qwen EN a Recall@5 0,80/nDCG@5 0,771/utilidade 0,80; em PT-BR permaneceu 100%. Phi teve especificidade zero na calibração. Nenhum threshold foi adicionado ao app: o split pequeno não sustenta essa decisão.

## Seleção e fluxo integrado

- **Não há vencedor que passe a regra de seleção completa.** Qwen é melhor no ranking desta fixture, especialmente EN, e passou p95 na repetição isolada; contudo, nenhuma configuração passou o gate de abstinência e o fluxo real com geração Qwen não concluiu em 180 s. O ensaio Qwen+Qwen também excedeu o orçamento. Ranking sintético não aprova sozinho a configuração.
- **Phi é preservado como fallback operacional** por ser a configuração de embeddings do E2E completo aprovado no relatório/commit do Bloco 12. Isso é preservação do baseline, não uma validação nova nem fechamento Block 13.
- Reexecuções Block 13 com chat Qwen e embedding Phi excederam 180 s na primeira visita. As tentativas, incluindo uma com o modelo aquecido, registraram respostas sem conteúdo público e/ou uma chamada subsequente ainda em andamento (detalhes em `pipeline_timeout_trace.json`). A criação da visita pode ter iniciado gravações antes do timeout; persistência e estado após restart não foram verificados. Não houve novo PASS para `entrada → embedding → recuperação → prompt → geração → persistência → reinicialização → leitura`; alternância e falhas/recovery do Block 13 tampouco foram validadas. A execução Block 12 (659,699 s, Phi embeddings, Qwen chat aquecido, fixtures antigas) permanece evidência de baseline e não substitui a tentativa Block 13.
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

**PARTIAL.** O gate de abstinência falhou para ambos; Phi também falhou ranking EN, enquanto Qwen passou latência p95 nesta repetição isolada, mas não em todas as medições locais. A integração completa com a fixture Block 13 continua sem PASS e não chegou à verificação pós-restart. Phi é mantido como fallback do baseline, sem declarar novo modelo vencedor. Próximos passos: corrigir e validar a resposta pública/latência do provedor local, testar abstinência em dados independentes maiores e repetir a integração completa. Não se ampliou timeout nem se alegou prontidão clínica ou eficácia.
