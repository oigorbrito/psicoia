# Testes e evidências

Consulte também o [escopo e os limites do harness](HARNESS.md).

## Comandos locais

Na raiz:

```bash
python scripts/harness.py
python -m pytest -q
```

Para os testes da interface web:

```bash
cd src/web
node --test tests/*.test.js
```

Os validadores de catálogo, quando aplicável:

```bash
python scripts/validate_skill_catalog_locales.py --locale en --allow-missing
python scripts/validate_skill_catalog_locales.py --locale pt-BR --allow-missing
```

Um comando só pode ser relatado como aprovado se tiver sido executado na árvore de trabalho atual. Testes de estrutura não atestam qualidade de tradução, segurança clínica ou equivalência de recuperação.

## Estados

- `PASS`: verificação local executada ou evidência local observada e satisfez o critério específico.
- `GAP`: critério local aplicável não satisfeito.
- `UNKNOWN_EXTERNAL`: depende de estado externo não consultado ou não verificável localmente.
- `NOT_APPLICABLE`: gatilho documentado não está ativo.
- `NOT_RUN`: verificação aplicável não foi executada.

## Escopo

O harness não executa a suíte completa nem valida configurações hospedadas. Consulte o relatório de cada execução; não interprete a existência de testes ou workflows como evidência de execução bem-sucedida.
