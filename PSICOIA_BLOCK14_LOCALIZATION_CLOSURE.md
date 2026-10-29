# PsicoIA Block 14 — encerramento da localização

**Resultado geral: PARTIAL.** A identidade canônica e os fluxos principais de apresentação foram ajustados e exercitados em uma integração local com navegador real. A localização não é completa: conteúdo de foco/legado permanece no idioma de origem, a maioria dos catálogos continua ausente e não houve validação de qualidade com modelo nem validação clínica.

## Identificação e limites da execução

- Worktree: `D:/projetos/psicoia-reconciliation`
- Branch: `reconciliation/psicoia-block14-localization`
- Revisão funcional (código, testes e documentação de localização): `b805a4945c50ecfd4d97213217f616b4de95f6da`
- A referência acima é o commit funcional ao qual este relatório se refere. Este documento é acrescentado em um commit local somente de documentação imediatamente após essa revisão; o HEAD final após esse commit é informado na conclusão da tarefa.
- HEAD inicial do Block 14: `60d390c5d354650792609fd374bc34849f45440b`.
- Não houve push, PR, merge, rebase destrutivo, publicação ou alteração da branch `main`.
- Permaneceram sem staging e sem alteração os artefatos de recuperação já não rastreados: `reports/block13/retrieval_analysis.json`, `reports/block13/retrieval_phi4-mini_3.8b.json` e `reports/block13/retrieval_qwen3.5_4b.json`.

## Escopo implementado

- **Identidade:** PsicoIA é o nome de apresentação nos entrypoints sample/eval/RFT, no título OpenAPI, na interface e nos exemplos de inicialização. Referências PsychAgent necessárias à proveniência, pesquisa, atribuição e compatibilidade foram mantidas. `README_CN.md` continua no mesmo caminho legado e agora aponta para os guias mantidos.
- **Interface web:** o seletor PT-BR/inglês permanece salvo no navegador, foi movido para o cabeçalho para não encobrir a ação principal e continua usando o campo existente `output_language`. Rótulos de etapa conhecidos e nomes de abordagem são apresentados por IDs estáveis; autenticação, percurso, status, mensagens de erro mapeadas e ajuda principal têm texto PT-BR/inglês.
- **API:** mensagens operacionais de autenticação, domínio, ciclo de percurso/sessão e validação foram localizadas em PT-BR. A interface apresenta em inglês as mensagens PT-BR mapeadas. Título/descrições OpenAPI foram localizados. Rotas, status HTTP, nomes de propriedades, enum `output_language`, IDs de etapa/abordagem e formato de resposta de validação foram preservados.
- **Idioma de geração:** PT-BR é o padrão do runtime de demonstração e quando uma chamada web não informa idioma; a escolha explícita em inglês continua suportada. Instruções finais de idioma para respostas/valores textuais foram acrescentadas ou ajustadas em caminhos autorizados, preservando chaves, marcadores e instruções clínicas existentes. Respostas sintéticas do backend de demonstração e do simulador agora cobrem PT-BR; valores de idioma existentes continuam aceitos.
- **CLI e operação:** textos de ajuda e resumos dos entrypoints sample, eval e RFT foram localizados. Flags, nomes de opções, módulos, variáveis de ambiente e identificadores compatíveis não foram renomeados.
- **Documentação:** os retratos de localização em inglês e PT-BR e a seção pertinente de arquitetura foram atualizados com limites e evidências.

### Conteúdo preservado deliberadamente

Não foram traduzidos os prompts clínicos de `prompts/psychagent/`, orientações/recomendações clínicas, instrumentos/escalas, prompts de avaliação, benchmarks nem catálogos de skills. O ajuste no prompt público restringiu-se à remoção de uma instrução final conflitante que exigia resposta em chinês; a instrução de idioma é anexada dinamicamente. No prompt de fallback do simulador, removeu-se apenas a restrição linguística fixa e acrescentou-se a instrução dinâmica. Regras clínicas, conteúdo restante e formato não foram traduzidos.

## Verificações executadas

| Estado | Comando/atividade | Resultado e escopo |
|---|---|---|
| PASS | `PYTHONPATH="src;$(cygpath -w /d/temp/psicoia-block14-venv/Lib/site-packages)" python -m pytest -q` | 52 testes passaram. O Python do sistema executou pytest e usou dependências web instaladas em ambiente virtual isolado. Houve um aviso `PendingDeprecationWarning` do Starlette sobre `python_multipart`; nenhum pacote/dependência do projeto foi alterado. |
| PASS | `cd src/web && npm test` | 5 testes Node passaram: status, rótulos de abordagem/etapa e mapeamento de locale para os valores existentes do enum. |
| PASS | `cd src/web && npm run build` | Build Vite concluído. |
| PASS | `D:/temp/psicoia-block14-venv/Scripts/python.exe tests/backend_e2e.py` | 16 rotas de negócio exercitadas por HTTP loopback; autenticação/SQLite sobreviveram a reinicialização; validação, autorização, ciclo de vida e rollback de falha de geração verificados. Mensagens PT-BR foram afirmadas explicitamente. Provedor OpenAI-compatible e catálogos eram sintéticos/vazios; não houve modelo ou embeddings reais. |
| PASS | `python D:/temp/psicoia-block14-browser-validation.py` | Chromium real percorreu seleção e persistência do idioma após reload, cadastro, erro de autenticação exibido em inglês, criação de percurso e envio de mensagem contra frontend e backend locais. A captura de requisições confirmou `output_language` existente com valores PT-BR e inglês. Também foi verificado o limite horizontal do seletor em viewport de 390 px. O script temporário não foi adicionado ao repositório. |
| PASS | `python -m src.sample.main --help`, `python -m src.eval.main --help`, `python -m src.rft.main --help` | Os três entrypoints retornaram ajuda PT-BR; opções técnicas foram mantidas. |
| PASS | `python -m compileall -q src/web/backend src/sample src/eval src/rft`; `bash -n run_backend.sh run_frontend.sh`; `git diff --check` | Concluídos sem erros. `git diff --check` emitiu somente avisos de conversão LF/CRLF do Git para arquivos existentes/novos. |
| GAP | `python scripts/validate_skill_catalog_locales.py --locale pt-BR` e `--locale en` | A execução estrita terminou com código 1 por catálogos ausentes. Cobertura observada: PT-BR 16/30 catálogos, 1.233/5.158 registros; inglês 8/30, 141/5.158. As versões com `--allow-missing` terminaram sem outros erros, mas não satisfazem cobertura integral. Conteúdo protegido não foi criado nem alterado. |
| GAP / UNKNOWN_EXTERNAL | `python scripts/harness.py` | Harness local registrou `GAP` para arquivo de licença reconhecido e `UNKNOWN_EXTERNAL` para regras GitHub, MFA, usuários ativos, releases, canal de segurança privado e implantação. Também informou que não executa os testes nem verifica controles hospedados; não é auditoria nem declaração de conformidade. |
| NOT_RUN | Validação de respostas com modelo real, revisão linguística/profissional, equivalência clínica, navegador além de Chromium, testes visuais/acessibilidade completos e implantação | Não executados. O provedor do teste de navegador foi programado para respostas sintéticas e não demonstra qualidade de idioma ou comportamento de modelo. |

## Lacunas e limites

- Valores de foco da sessão, contexto/descrições de domínio, aliases legados e strings desconhecidas podem continuar em chinês na interface/API. Em particular, o fallback `SESSION_FOCUS_DEFAULT` foi preservado por conter conteúdo operacional potencialmente clínico; sua localização requer autorização/revisão própria.
- Os catálogos localizados existentes não foram incluídos nem validados quanto a qualidade, proveniência, recuperação ou embeddings. Contagens são apenas cobertura estrutural.
- A instrução de idioma no prompt não garante que um modelo produza o idioma pedido. O fluxo sintético confirma encaminhamento do campo, não qualidade linguística.
- O teste de Chromium verificou as interações descritas e o seletor em viewport estreito; não equivale a revisão visual integral, teste de acessibilidade, compatibilidade entre navegadores ou validação clínica.
- A execução não demonstra segurança, maturidade, prontidão de produção, eficácia ou equivalência clínica. Nenhum serviço pago, chave real, modelo baixado ou dado clínico foi usado.

## Arquivos alterados neste commit funcional

- `LOCALIZATION.md`
- `LOCALIZATION.pt-BR.md`
- `README_CN.md`
- `configs/runtime/psychagent_sglang_local.yaml`
- `docs/ARCHITECTURE.md`
- `prompts/public/counselor_system.jinja2`
- `run_backend.sh`
- `run_frontend.sh`
- `src/eval/main.py`
- `src/rft/main.py`
- `src/sample/backends/dummy_backend.py`
- `src/sample/client/simulator.py`
- `src/sample/core/language.py` (novo)
- `src/sample/core/prompt_manager.py`
- `src/sample/core/schemas.py`
- `src/sample/main.py`
- `src/web/backend/domain.py`
- `src/web/backend/localization.py` (novo)
- `src/web/backend/psychagent_engine.py`
- `src/web/backend/schemas.py`
- `src/web/backend/services/course_service.py`
- `src/web/backend/services/visit_service.py`
- `src/web/main.py`
- `src/web/src/App.jsx`
- `src/web/src/components/common/StageBadge.jsx`
- `src/web/src/components/common/stageText.js` (novo)
- `src/web/src/components/layout/HeaderBar.jsx`
- `src/web/src/components/layout/RightPanel.jsx`
- `src/web/src/components/layout/Sidebar.jsx`
- `src/web/src/components/layout/VisitTimeline.jsx`
- `src/web/src/i18n.jsx`
- `src/web/src/services/http.js`
- `src/web/tests/statusText.test.js`
- `tests/backend_e2e.py`
- `tests/test_output_language_localization.py` (novo)
- `tests/test_project_identity.py`

O relatório não altera os três artefatos Block 13 listados acima. A revisão funcional é local; nenhuma publicação ou operação remota foi realizada.
