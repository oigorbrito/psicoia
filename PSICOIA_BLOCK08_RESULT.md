# PsicoIA Block 08 — resultado de reconciliação local

**Data da verificação:** 2026-10-29

**Estado:** candidato local auditável, ainda bloqueado para distribuição. Nenhum push, PR ou publicação foi feito; `main` não foi alterada.

## 1. Árvore e proveniência

- Candidato: branch `reconciliation/psicoia-block08`, criada em `4e845dd0b22990b143cb79cbe7867d66936cbd06` sobre `integration/psicoia`. A história de integração existente foi preservada; esta reconciliação acrescenta um commit local, sem reescrever commits anteriores.
- Fonte local: `master` em `e13c895850dc074fd5618322c5e7c1cfda34a29c`; contém `.gitattributes` rastreado e alterações de trabalho em sua maioria não rastreadas. Nenhum arquivo foi removido ou alterado nessa árvore fonte.
- Referência upstream: `ECNU-ICALK/PsychAgent`, snapshot `469f45ef468b968b3fccd1936d7e6a0a574e4c5c`. Destino remoto: `oigorbrito/psicoia`, `origin/main` observado em `0ca22eb238828a84034535494d00c66396e12110`.
- A comparação de 1.393 caminhos upstream com a árvore fonte, usando blobs Git/filtros de normalização, resultou em **1.289 iguais, 104 diferentes e 0 ausentes**. A árvore candidata antes deste bloco tinha 1.384 blobs iguais, 9 diferenças de apresentação/documentação e 0 ausentes. Diferenças CRLF do checkout Windows foram excluídas da contagem de conteúdo.
- A fonte local contém 74 adições fora dos caminhos upstream. O índice candidato reconciliado contém **1.460 caminhos**: todos os 1.393 upstream presentes, **1.379 blobs upstream idênticos, 14 diferentes e 67 caminhos adicionais**. Os 14 caminhos diferentes são `.gitignore`, os oito READMEs ingleses listados no inventário, `src/sample/main.py`, `src/web/index.html`, `src/web/main.py` e os dois metadados do pacote. O candidato mantém a história de integração existente e acrescenta evidências/testes; `docs/INVENTARIO-DIFERENCAS-UPSTREAM.pt-BR.md` registra os grupos e caminhos. Dois catálogos permanecem marcados `.partial` e fora do candidato.
- Backups preservados: `../psicoia-worktree-before-integration.tar.gz` SHA-256 `bf5ea3b95581ded2e29ff1a97243a23d63759f7a65c0086d097f6fc18b597bc0`; `../psicoia-git-refs-before-integration.bundle` SHA-256 `0fef368c5132d1bba52e8b8b08905f47df510ae837999adce8cc6150276ec939` (verificação do bundle aprovada); arquivo pós-auditoria `../psicoia-final-audit-worktree-2026-10-29.tar.gz` SHA-256 `0abd4cc6f6931d7d8e0e5440fd58aa2d30866f810b48ff44aa7be960529f9a1d`.

### Gate obrigatório de direitos

Não foi encontrada licença `LICENSE`/`COPYING` local ou upstream. A API do GitHub para `ECNU-ICALK/PsychAgent` retornou `license: null`; o endpoint de licença retornou 404. O artigo e a lista de autores identificam a publicação, mas **não** provam titularidade do código, de modelos, dados, perfis, imagens, prompts ou autorização para redistribuí-los. Nenhuma licença foi criada e a preferência por MIT não substitui autorização. **Push, PR público e distribuição continuam bloqueados** até confirmação escrita de direitos e proveniência por componente. Não há PR aberto observado em 2026-10-29.

## 2. Classificação dos 104 diffs e decisão

A classificação por arquivo é consolidada no inventário. O resultado agregado é:

| Classe | Qtde. | Conteúdo e decisão |
|---|---:|---|
| **A — apresentação/identidade** | 12 | Oito READMEs, dois metadados do pacote privado, texto de ajuda da CLI e título HTML. Mantidos como apresentação; revisão semântica completa dos READMEs ainda é pendente. |
| **B — adaptação funcional intencional** | 17 | Locale/domínio e UI da implementação local. A intenção de localização é reconhecida, mas o wiring/runtime não foi incorporado: exige validação de interface, locale e persistência. |
| **C — configuração local do destino** | 1 | `.gitignore`; mantido com regras para segredos, caches e artefatos, preservando `.env.example` e `.env.template`. |
| **D — mudança comportamental ou não validada** | 74 | Um default YAML, 33 prompts, 25 módulos de avaliação, sete arquivos de geração/recuperação e oito arquivos web com contrato/propagação de idioma. Mantidos fora do candidato. |

Mapeamento primário dos 26 arquivos web: **A** — `src/web/index.html`; **B** — `src/web/backend/domain.py`, `src/web/src/App.jsx`, `src/web/src/components/chat/{ChatInput,ChatMessages}.jsx`, `src/web/src/components/common/{FeedbackBanner,StageBadge}.jsx`, `src/web/src/components/common/{schoolText,statusText}.js`, `src/web/src/components/layout/{HeaderBar,MobileBottomSheet,RightPanel,Sidebar,VisitTimeline}.jsx` e `src/web/src/components/modals/{AuthModal,CompleteCourseModal,CreateCourseModal,SchoolModal}.jsx`; **D** — `src/web/backend/psychagent_engine.py`, `src/web/backend/routes/{courses,visits}.py`, `src/web/backend/schemas.py`, `src/web/backend/services/{course_service,visit_service}.py`, `src/web/main.py` e `src/web/src/hooks/useMindCareApp.js`. `main.py` contém também um título de API de classe A isolado, aplicado sem propagar o comportamento D.

Não se tratou tradução de prompts, mensagens de reparo, conteúdo de avaliação, defaults ou catálogo como mera apresentação. As 25 alterações de `src/eval/` são AST-equivalentes após mascarar strings, mas as instruções de reparo enviadas ao modelo mudaram; 33 templates Jinja foram parseados, sem benchmark semântico. `prompts/eval/SCL_90/SCL_90.txt` mantém o blob upstream; essa verificação não valida adequação clínica nem direitos.

### As 12 diferenças Python estruturais

A comparação AST das 41 diferenças Python encontrou 29 equivalentes após mascarar strings/bytes e estas 12 diferenças estruturais:

1. `src/sample/backends/dummy_backend.py` — saída simulada/defaults por idioma.
2. `src/sample/client/simulator.py` — fallback e heurísticas de idioma/humor.
3. `src/sample/core/prompt_manager.py` — templates/fallbacks e instruções de abertura.
4. `src/sample/prompt_manager.py` — comportamento de renderização de fallback.
5. `src/sample/runner.py` — foco da sessão e propagação de idioma aos prompts.
6. `src/sample/skill_manager.py` — seleção de catálogos e caches por idioma.
7. `src/web/backend/psychagent_engine.py` — parâmetros de idioma em geração e artefatos.
8. `src/web/backend/routes/courses.py` — propagação do novo campo de request.
9. `src/web/backend/routes/visits.py` — propagação do idioma em ações da sessão.
10. `src/web/backend/schemas.py` — novo tipo/campos `output_language` no contrato.
11. `src/web/backend/services/visit_service.py` — callbacks, defaults e valores persistidos por idioma.
12. `src/web/main.py` — propagação de idioma do endpoint para o backend.

Essas diferenças não são aceitas como equivalentes por terem passado testes estruturais. O estado local de `master` e o arquivo de inventário preservam os diffs não incorporados para revisão posterior.

## 3. Mudanças aplicadas neste candidato

- Aplicado o nome PsicoIA à descrição/help da CLI, ao título do OpenAPI, ao título HTML e ao nome do pacote privado (`psicoia-web`), mantendo `private: true`, `--mode psychagent`, rotas, modelos, chaves técnicas e atribuição PsychAgent. O `lang="zh-CN"` estático foi mantido, pois a UI ainda não possui locale dinâmico.
- `.gitignore` reforçado para `.env`, `.env.*`, logs, IDE e artefatos, com exceções para templates de ambiente; `.gitattributes` com `* text=auto` estabiliza normalização de EOL.
- Colisão do pytest resolvida sem apagar o teste do template: `pytest.ini` limita a coleta padrão a `tests/` e `src/web/tests/`; o teste em `evidence-repo-template/` é executado separadamente.
- Adicionados testes mínimos de domínio web Python e helpers JavaScript puros, mais teste de identidade/compatibilidade. Isso não é cobertura de fluxo API, React ou segurança.
- Nenhuma alteração de autenticação, CORS, armazenamento de token, modelo, catálogo, instrumento clínico ou comportamento de prompts foi aplicada.

## 4. Testes e evidências executados

| Comando/verificação | Resultado |
|---|---|
| `python -m pytest -q` | **17 passed**; coleta padrão sem colisão. |
| `python -m pytest -q evidence-repo-template/tests/test_harness.py` | **4 passed**, executados separadamente. |
| `cd src/web && npm ci --ignore-scripts` | Concluído; auditoria npm reportou as vulnerabilidades abaixo. |
| `cd src/web && npm test` | **2 passed** (Node test runner). |
| `cd src/web && npm run build` | Vite build aprovado. |
| Backend smoke no ambiente isolado, import de `main.app` | Título `PsicoIA Web API`; **20 rotas** importadas. |
| `python -m compileall -q src` com `PYTHONPYCACHEPREFIX` externo | Aprovado sem reescrever bytecode versionado. |
| `pip check` no ambiente isolado de auditoria | Nenhum requisito quebrado. |
| `python scripts/harness.py` | Exit 0; `PASS` para testes/web, `GAP` para licença, `UNKNOWN_EXTERNAL` para controles hospedados/implantação. Exit 0 não significa conformidade. |
| `gitleaks detect --source .` / `gitleaks protect --staged` | **0 findings** na história (32 commits, ~14,73 MB) e **0 findings** nas mudanças staged. |
| `git diff --check` | Aprovado; Git avisou que `.gitignore` será convertido de LF para CRLF no checkout Windows, conforme configuração local. |

A validação não executou modelo nem avaliação clínica. Os 88 casos sintéticos do experimento de continuidade permanecem em worktree isolada, com rótulos provisórios; não houve execução de modelo nem revisão humana independente concluída.

## 5. Segurança e dependências — bloqueadores

- `npm audit`: **9 advisories** (6 high, 2 moderate, 1 low) na árvore do lockfile; a correção indicada para Vite exige upgrade major para Vite 8. Nenhuma atualização foi aplicada sem revisão de compatibilidade.
- `pip-audit -r src/web/requirements.txt`: **14 registros de advisory para Starlette 0.37.2**. `fastapi==0.110.2` restringe a faixa atual; atualização requer revisão e testes de compatibilidade. A resolução isolada escolheu `openai 3.41.0` por `openai>=1.0.0`; compatibilidade com o código não está comprovada.
- Defaults herdados ainda inseguros para produção: hash de senha SHA-256 rápido e sem salt, token sem checagem de expiração, CORS com wildcard e credenciais, exemplo de servidor em `0.0.0.0` com `--reload`, token bearer em `localStorage`. Nenhuma mitigação foi feita incidentalmente nesta reconciliação. **Não implantar como produção.**
- Configurações GitHub, MFA, regras de branch, canal privado de reporte, releases e implantação não foram verificados autoritativamente; permanecem `UNKNOWN_EXTERNAL`.

## 6. Próxima ação

1. Obter do titular/rights holder confirmação escrita de proveniência e autorização de redistribuição por código, modelos, datasets/perfis, imagens e prompts; só então decidir licença e publicação.
2. Preservar os trabalhos não incorporados em `master`; revisar/validar separadamente as mudanças B/D de idioma, API, prompts, avaliação e recuperação. Não habilitar catálogo localizado sem validação de conteúdo, cache e retrieval.
3. Revisar compatibilidade e correções para Starlette/Vite e substituir os defaults de autenticação/CORS/token por desenho seguro com testes próprios antes de qualquer release.
4. Revalidar o hash de `origin/main`, os controles externos e todos os gates antes de qualquer publicação. Não fazer push/PR nem alterar `main` sem revisão e autorização explícitas.
