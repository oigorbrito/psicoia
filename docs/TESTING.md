# Testes e evidências

Consulte também o [escopo e os limites do harness](HARNESS.md).

## Comandos locais

Na raiz do worktree candidato:

```bash
python scripts/harness.py
python -m pytest -q --import-mode=importlib
python -m pytest -q tests/test_harness.py tests/test_localized_documentation.py
```

A opção `--import-mode=importlib` evita colisão de importação entre `evidence-repo-template/tests/test_harness.py` e `tests/test_harness.py`. Sem ela, `python -m pytest -q` falha na coleta com `import file mismatch` para o módulo `test_harness`; essa falha de coleta está registrada, não corrigida.

A suíte de testes web e o validador de catálogos localizados não foram incluídos porque pertencem a alterações de localização ainda pendentes. Não execute seus comandos como se esses recursos estivessem ativos neste candidato.

Um comando só pode ser relatado como aprovado se tiver sido executado na árvore de trabalho atual. Testes de estrutura não atestam qualidade de tradução, segurança clínica ou equivalência de recuperação.

## Estados

- `PASS`: verificação local executada ou evidência local observada e satisfez o critério específico.
- `GAP`: critério local aplicável não satisfeito.
- `UNKNOWN_EXTERNAL`: depende de estado externo não consultado ou não verificável localmente.
- `NOT_APPLICABLE`: gatilho documentado não está ativo.
- `NOT_RUN`: verificação aplicável não foi executada.

## Escopo

O harness não executa a suíte completa nem valida configurações hospedadas. Consulte o relatório de cada execução; não interprete a existência de testes ou workflows como evidência de execução bem-sucedida.
