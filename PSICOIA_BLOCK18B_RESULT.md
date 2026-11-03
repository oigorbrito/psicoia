# PsicoIA — Bloco 18B: resultado técnico e de localização

**Estado: PARTIAL; gate CLOSED não atendido.** O erro de importação foi corrigido por configuração de pytest, e os testes confirmam as localizações PT-BR/EN já existentes. Este bloco não acrescentou traduções de interface, catálogos, prompts ou textos de domínio: não foi possível provar, no inventário versionado disponível, uma superfície nova ainda não localizada que fosse simultaneamente de titularidade própria e independente do conteúdo upstream. Não se tratou a falta de licença como autorização.

## Base e alteração

- Branch: `reconciliation/psicoia-block18-translation`.
- SHA inicial: `fc1106a27a3929908fc0dc75a7469a0a96b6c774`.
- Alteração: `pytest.ini` agora declara `pythonpath = src` para os imports top-level `sample` e `web` usados pelos testes.
- Nenhum contrato de API, código de aplicação, dado clínico ou arquivo upstream foi alterado.
- As localizações operacionais herdadas estão documentadas em `PSICOIA_BLOCK16_RESULT.md` e nos resultados anteriores. A alteração de configuração deste bloco não muda sua cobertura.

## Causa do `ModuleNotFoundError: sample`

O pytest era executado na raiz e encontrava `pytest.ini`, mas a configuração só declarava `testpaths`; o diretório `src` não estava no caminho de importação do Python. Os testes importam `sample.*` (e `web.*`) como pacotes top-level, embora estejam sob `src/`. Portanto, a causa reproduzida era configuração de caminho de importação, não dependências ausentes nem diretório de execução. A configuração pytest `pythonpath = src` resolve o import sem mudar os módulos/contratos e permite executar sem variável de ambiente manual.

## Direitos e proveniência — gates distintos

- **Redistribuição:** permanece sem autorização comprovada; `python scripts/harness.py` continua reportando `GAP` para arquivo de licença. Isso é evidência local de ausência de arquivo reconhecido, não uma conclusão jurídica nem um defeito de execução.
- **Produção/adaptação de traduções locais:** não se presume autorizada pela ausência de licença. A autorização desta tarefa delimita o trabalho, mas não prova titularidade ou direitos sobre texto upstream derivado.
- **Componentes PsicoIA:** a análise do Bloco 17 registra sinais de autoria Git para adições locais, mas não prova titularidade/cessão de direitos por componente. Não rotulei conteúdo como próprio apenas por estar em diretório local ou ter sido editado localmente.
- **Conteúdo clínico e terceiros:** instrumentos, escalas, dados, prompts comportamentais e catálogos permanecem excluídos deste bloco; não foram modificados nem traduzidos. Materiais de terceiros seguem pendentes de análise específica.

## Tradução e cobertura

- **Novos textos traduzidos neste bloco:** nenhum.
- **UI, mensagens operacionais, guias e textos de identidade já localizados:** preservados como herdados dos blocos anteriores; os testes abaixo verificam seleção e contratos em ambos os idiomas, sem alegar validação clínica ou linguística dos modelos.
- **Catálogos (sem alteração):** PT-BR 16/30 arquivos e 1.233/5.158 registros; EN 8/30 e 141/5.158.
- Não houve revisão de todos os textos próprios em potencial; a proveniência incerta impede declarar cobertura total do escopo próprio.

## Verificações executadas

- `python -m pytest -q tests/test_localized_documentation.py tests/test_output_language_localization.py tests/test_skill_catalog_locale_loading.py tests/test_skill_catalog_localization_validation.py tests/test_skill_manager_locale_retrieval.py tests/test_web_output_language.py` — **30 passed**, sem `PYTHONPATH` manual.
- `python -m pytest -q` — **56 passed**.
- `cd src/web && npm test` — **6 passed**.
- `cd src/web && npm run build` — **falhou**: `vite` não foi reconhecido. A dependência local do build não está disponível neste worktree; não houve instalação de dependências.
- `python scripts/harness.py` — checks locais de arquivos passaram; licença reconhecida `GAP`; controles externos `UNKNOWN_EXTERNAL`. Não é auditoria e não executa os testes.
- Validadores com `--allow-missing`: PT-BR 16/30, 1.233/5.158; EN 8/30, 141/5.158.
- `git diff --check` — passou.
- Navegador e fluxo HTTP/API ao vivo: não executados neste bloco. Os resultados históricos do Bloco 16 registram validações direcionadas; não são apresentados como execução atual.

## Pendências e fechamento

`CLOSED` não é apropriado: embora a coleta de testes funcione e a suíte passe, este bloco não demonstrou que todos os textos do escopo próprio estejam cobertos, não acrescentou novas traduções e não executou build/navegador/API ao vivo nesta árvore. Permanecem pendentes a confirmação de titularidade/proveniência por componente, conteúdo upstream e de terceiros, catálogos/prompts protegidos e disponibilidade de Vite para build. Nenhum push, PR, merge ou publicação foi feito.
