# Instruções para agentes

Estas instruções são regras locais de trabalho; não representam certificação ou conformidade externa.

## Antes de alterar

1. Leia `policy/project-state.json`, `docs/MATURITY.md`, `docs/ARCHITECTURE.md`, `docs/TESTING.md`, `docs/HARNESS.md` e `docs/MIGRATION-POLICY.pt-BR.md`.
2. Confira `docs/SOURCES.md` antes de fazer afirmações factuais sobre o projeto ou citar padrões externos.
3. Não transforme evidência ausente, desatualizada ou não executada em aprovação.
4. Use os estados `PASS`, `GAP`, `UNKNOWN_EXTERNAL`, `NOT_APPLICABLE` e `NOT_RUN` somente com os significados descritos em `docs/TESTING.md`.
5. Não declare conformidade, maturidade, segurança, prontidão de produção ou equivalência clínica sem evidência verificável.
6. Para a migração PsychAgent → PsicoIA, copie o código literalmente: não faça refatorações, correções, melhorias, atualizações ou mudanças funcionais. A única alteração de marca permitida é em texto de apresentação voltado a pessoas; preserve identificadores, APIs, caminhos, dados e atribuição acadêmica.
7. Traduza somente prosa e conteúdo de apresentação no escopo aprovado para PT-BR (principal) e inglês (secundário). Prompts, benchmarks e catálogos exigem autorização/validação específica conforme `docs/MIGRATION-POLICY.pt-BR.md`.
8. Preserve os documentos existentes e faça alterações pequenas. Não adicione controles apenas para aparentar maturidade; registre separadamente qualquer exceção autorizada à cópia literal.

## Verificação

Execute `python scripts/harness.py` e os testes relevantes antes de concluir. O harness é um adaptador local limitado; não é uma auditoria OSPS/NIST/DORA. Informe comandos executados, resultados, limitações e verificações não executadas.

Quando uma alteração material afetar arquitetura, segurança ou release, atualize os documentos correspondentes.
