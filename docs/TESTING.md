# Testes e evidências

Consulte também o [escopo e os limites do harness](HARNESS.md).

## Comandos locais

Na raiz do worktree candidato:

```bash
python scripts/harness.py
python -m pytest -q
python -m pytest -q evidence-repo-template/tests/test_harness.py
(cd src/web && npm test && npm run build)
```

`pytest.ini` limita a descoberta padrão aos testes do projeto em `tests/` e `src/web/tests/`; o template em `evidence-repo-template/` é executado separadamente para evitar colisão entre módulos chamados `test_harness`.

Os testes web cobrem funções de domínio Python e helpers JavaScript puros. Eles não cobrem fluxos completos da API, componentes React, segurança de autenticação/CORS nem qualidade de localização. O validador de catálogos localizados continua fora do candidato enquanto proveniência, recuperação e qualidade linguística estiverem pendentes.

Um comando só pode ser relatado como aprovado se tiver sido executado na árvore de trabalho atual. Testes de estrutura não atestam qualidade de tradução, segurança clínica ou equivalência de recuperação.

## Estados

- `PASS`: verificação local executada ou evidência local observada e satisfez o critério específico.
- `GAP`: critério local aplicável não satisfeito.
- `UNKNOWN_EXTERNAL`: depende de estado externo não consultado ou não verificável localmente.
- `NOT_APPLICABLE`: gatilho documentado não está ativo.
- `NOT_RUN`: verificação aplicável não foi executada.

## Escopo

O harness não executa a suíte completa nem valida configurações hospedadas. Consulte o relatório de cada execução; não interprete a existência de testes ou workflows como evidência de execução bem-sucedida.
