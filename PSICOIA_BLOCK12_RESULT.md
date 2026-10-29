# Resultado do Bloco 12 — pipeline local PT-BR/EN

**Estado: PARTIAL.** As verificações técnicas de geração, recuperação de fixture, isolamento PT-BR/EN, persistência, rollback, frontend e regressões passaram no escopo abaixo. O bloco não é declarado CLOSED porque o benchmark sintético ainda registra perdas de contexto, os embeddings são mean pooling de modelos generativos gerais, os catálogos traduzidos estão incompletos e a configuração Qwen de embeddings não completou o E2E HTTP dentro do timeout local. Não há alegação de adequação clínica, equivalência, segurança ou prontidão de produção.

## Escopo e alterações

- Mantido o contrato de idioma por requisição, com `SkillManager` separado por idioma; catálogos localizados não passam pelo rewriter de consulta chinês.
- A extração da resposta pública ignora campos tipados/separados de raciocínio e reconhece marcadores estruturais, falhando fechado em raciocínio incompleto. O raciocínio bruto não é persistido como resposta pública.
- Dimensão, cardinalidade e finitude dos vetores são verificadas antes de comparações de recuperação.
- Falha ao carregar/recuperar contexto de skills interrompe a geração sem contexto e permite rollback. Mensagens de status de abertura/encerramento e o fallback estático genérico de abertura agora têm versões em inglês e PT-BR; o texto do seed interno também segue o idioma solicitado.
- O orçamento da chamada de seleção coarse foi limitado a 256 tokens. A resposta local ainda foi vazia em alguns casos; o seletor existente recorreu à lista padrão. No fixture há apenas uma categoria raiz, portanto isso não exercita seleção entre categorias concorrentes.
- Não foram alterados prompts clínicos, critérios diagnósticos, recomendações terapêuticas nem conteúdo dos catálogos. Os dados de benchmark, catálogos e visitas usados aqui são sintéticos.

## Evidência E2E com modelos locais

Comando completo executado:

```text
PSICOIA_LOCAL_CHAT_MODEL=qwen3.5:4b D:/temp/psicoia-block10-venv/Scripts/python.exe tests/backend_block12_local_pipeline_e2e.py
```

Resultado da execução completa no código final: **PASS**, 659.699 ms (aprox. 11 min), com `qwen3.5:4b` para geração e `phi4-mini:3.8b` para vetores. O modelo de chat já estava carregado no início desta execução. Uma execução fria anterior também passou em 940.183 ms. Configuração de geração: temperatura 0, limite 1.024 tokens, timeout 300 s. O servidor de embeddings local foi `llama-server --embedding --pooling mean`, CPU-only.

- Abertura real PT-BR: canário de idioma passou; 1.385 tokens de entrada, 403 de saída, término `stop`.
- Sequência na mesma instância: **PT-BR → EN → PT-BR**. As três respostas passaram os canários lexicais de idioma e os marcadores de raciocínio interno não apareceram no texto persistido.
- Em cada idioma, o skill sintético esperado estava no prompt final real. Cada troca carregou os lotes de merge/retrieval do catálogo localizado uma vez; o retorno a PT-BR reutilizou seu gerenciador em memória.
- Latências HTTP das três respostas: 85,2 s, 91,4 s e 95,8 s. Os completions terminaram com `stop`, não com limite de tokens. A inicialização da API mediu 26,6 s e a do servidor de embeddings 10,5 s nesta execução.
- Após reinicialização do backend, as quatro respostas do primeiro atendimento continuaram disponíveis. Também foi injetada falha nas quatro tentativas de geração da abertura em inglês: o fallback genérico em inglês foi persistido e recuperado depois do restart.
- Falha de embeddings: três respostas 503 do endpoint local; a geração sem contexto foi recusada, a rota respondeu 502 e a transação não persistiu a mensagem. Nenhuma chamada de geração contendo o texto desse teste ocorreu.
- Falha de geração: injeção na chamada de resposta, HTTP 502 e `message_count` sem alteração.

A classificação de idioma é um canário lexical simples e ausência de caracteres CJK, não um detector independente nem avaliação linguística abrangente. As respostas demonstram funcionamento técnico em entradas sintéticas, não qualidade clínica.

## Benchmark determinístico de recuperação

Arquivo de referência: `tests/fixtures/block12/retrieval_benchmark.json` — 32 consultas sintéticas rotuladas, 16 por idioma, contra 8 documentos sintéticos por idioma; `top_k=5`. As métricas são calculadas sobre a ordenação real de similaridade cosseno retornada pelo código da aplicação, e a presença do documento relevante é verificada no prompt renderizado. Não representam avaliação do catálogo clínico completo.

| Embedding local mean pooling | Idioma | Dimensão | Recall@1 | Recall@3 | Recall@5 | MRR | Relevante no prompt (top 5) | Latência média da chamada de embedding |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `phi4-mini:3.8b` | PT-BR | 3.072 | 0,2500 | 0,8125 | 0,8750 | 0,5350 | 0,8750 | 589,7 ms |
| `phi4-mini:3.8b` | EN | 3.072 | 0,1250 | 0,5000 | 0,7500 | 0,3543 | 0,7500 | 563,5 ms |
| `qwen3.5:4b` | PT-BR | 2.560 | 0,5000 | 0,9375 | 0,9375 | 0,7068 | 0,9375 | 601,6 ms |
| `qwen3.5:4b` | EN | 2.560 | 0,5000 | 0,7500 | 1,0000 | 0,6604 | 1,0000 | 564,7 ms |

Indexação por idioma: `phi4-mini:3.8b` — 22.874 ms PT-BR / 18.149 ms EN na execução completa; no ensaio isolado, `qwen3.5:4b` — 29.662 ms PT-BR / 22.183 ms EN. O Phi perdeu contexto no top 5 em 2/16 consultas PT-BR e 4/16 EN; o Qwen perdeu em 1/16 PT-BR e 0/16 EN. `qwen3.5:4b` teve melhores resultados nesta fixture, mas é um modelo generativo geral, não um modelo dedicado a embeddings.

Comando do ensaio de embeddings alternativo (somente benchmark; não é E2E do backend):

```text
PSICOIA_RETRIEVAL_ONLY=1 PSICOIA_LOCAL_CHAT_MODEL=phi4-mini:3.8b PSICOIA_LOCAL_EMBED_MODEL=qwen3.5:4b D:/temp/psicoia-block10-venv/Scripts/python.exe tests/backend_block12_local_pipeline_e2e.py
```

A tentativa separada de usar Qwen para embeddings junto com Qwen para chat completions no E2E HTTP foi:

```text
PSICOIA_LOCAL_CHAT_MODEL=qwen3.5:4b PSICOIA_LOCAL_EMBED_MODEL=qwen3.5:4b D:/temp/psicoia-block10-venv/Scripts/python.exe tests/backend_block12_local_pipeline_e2e.py
```

Ela terminou com `httpx.ReadTimeout` numa chamada de mensagem após 300 s; não é contabilizada como PASS. O E2E completo aprovado usou Phi para embeddings; os resultados Qwen acima são apenas do benchmark de recuperação.

## Regressões, build e harness

| Comando | Resultado |
|---|---|
| `python -m pytest -q` | **45 passed** |
| `D:/temp/psicoia-block10-venv/Scripts/python.exe tests/backend_e2e.py` | **PASS**: 16 rotas locais sintéticas, autenticação/ownership, validação, ciclo de vida, rollback e persistência após restart |
| `PSICOIA_OPENING_FALLBACK_ONLY=1 PSICOIA_LOCAL_CHAT_MODEL=qwen3.5:4b PSICOIA_LOCAL_EMBED_MODEL=phi4-mini:3.8b D:/temp/psicoia-block10-venv/Scripts/python.exe tests/backend_block12_local_pipeline_e2e.py` | **PASS**: fallback genérico inglês após 4 falhas injetadas, persistido após restart |
| `python -m pytest -q evidence-repo-template/tests/test_harness.py` | **4 passed** |
| `D:/temp/psicoia-block10-venv/Scripts/python.exe -m py_compile src/sample/backends/openai_api.py src/sample/skill_manager.py src/sample/utils.py src/web/backend/psychagent_engine.py src/web/backend/services/visit_service.py tests/backend_block12_local_pipeline_e2e.py` | **PASS** |
| `cd src/web && npm ci` | **PASS** usando `package-lock.json`; npm reportou 9 vulnerabilidades |
| `cd src/web && npm test` | **2 passed** |
| `cd src/web && npm run build` | **PASS**: Vite 5.4.21, 1.600 módulos |
| `python scripts/harness.py` | PASS local para existência de CONTRIBUTING/testes; **GAP** de arquivo de licença; **UNKNOWN_EXTERNAL** para controles da plataforma. O harness não executa testes nem é auditoria/conformidade. |
| `python scripts/validate_skill_catalog_locales.py --locale en --allow-missing` | EN: 8/30 catálogos e 141/5.158 registros localizados |
| `python scripts/validate_skill_catalog_locales.py --locale pt-BR --allow-missing` | PT-BR: 16/30 catálogos e 1.233/5.158 registros localizados |
| `git diff --check` | **PASS** |

`npm ci` foi executado com o lockfile existente antes do build. O npm reportou 9 vulnerabilidades; não foram aplicadas atualizações de dependências. Uma primeira tentativa de `python tests/backend_e2e.py` no Python global falhou porque esse ambiente não tinha `sqlmodel`; a execução seguinte no venv da aplicação passou. Não foi usado serviço pago, chave real, publicação, push ou PR.

## Limitações e decisão

- Recall do Phi no top 5 foi 0,75 em EN e 0,875 em PT-BR; mesmo o Qwen teve uma consulta PT-BR sem o alvo no top 5. A evidência é pequena, sintética e não estabelece um limiar de qualidade para uso real.
- Nenhum modelo dedicado de embeddings estava instalado; mean pooling de hidden states de modelos generativos não demonstra uma representação semântica adequada.
- Catálogos localizados incompletos; há apenas oito documentos sintéticos por idioma neste benchmark. Seleção coarse com múltiplas categorias, comportamento em corpus completo e atualização simultânea de catálogos não foram demonstrados.
- A combinação Qwen embeddings + Qwen chat não passou o timeout do E2E HTTP. Benchmarks separados não substituem integração completa.
- A instalação frontend acusou 9 vulnerabilidades; o harness indicou lacuna de licença e estados externos desconhecidos.
- Não foram feitos benchmark contra upstream, avaliação clínica, revisão independente de idioma, análise de segurança ou teste de produção.

Por esses limites, **PARTIAL** é o estado final. O pipeline técnico local aprovado está demonstrado nas condições e fixtures declaradas; a recuperação generalizável e o uso clínico permanecem fora da evidência. Consulte `docs/TESTING.md` para o significado dos estados de verificação.
