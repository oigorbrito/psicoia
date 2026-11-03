# Instruções para agentes

Estas instruções são regras locais de trabalho; não representam certificação ou conformidade externa.

## Antes de alterar

1. Leia `policy/project-state.json`, `docs/MATURITY.md`, `docs/ARCHITECTURE.md`, `docs/TESTING.md`, `docs/HARNESS.md` e `docs/MIGRATION-POLICY.pt-BR.md`.
2. Confira `docs/SOURCES.md` antes de fazer afirmações factuais sobre o projeto ou citar padrões externos.
3. Não transforme evidência ausente, desatualizada ou não executada em aprovação.
4. Use os estados `PASS`, `GAP`, `UNKNOWN_EXTERNAL`, `NOT_APPLICABLE` e `NOT_RUN` somente com os significados descritos em `docs/TESTING.md`.
5. Não declare conformidade, maturidade, segurança, prontidão de produção ou equivalência clínica sem evidência verificável.
6. Para a migração PsychAgent → PsicoIA, preserve a cópia funcional do código: não faça refatorações, correções, melhorias, atualizações ou mudanças de comportamento. São permitidas as traduções textuais aprovadas pela regra 7, sem alterar lógica, identificadores, APIs, caminhos, dados ou atribuição acadêmica; a mudança de marca continua limitada a texto de apresentação voltado a pessoas.
7. A PsicoIA está em desenvolvimento local. O objetivo corrente é localizar o software para PT-BR preservando contratos e comportamento. Questões de distribuição e direitos não são critérios de aceite dos testes funcionais de tradução; não interrompa tarefas técnicas independentes por pendências documentais de distribuição. Preserve avisos autorais existentes e não presuma direitos de terceiros. Restrições específicas para conteúdo comportamental/clínico, adaptação de material upstream e publicação estão em `docs/MIGRATION-POLICY.pt-BR.md`.
8. Preserve avisos e documentos existentes e faça alterações pequenas. Exceções funcionais à cópia literal exigem autorização e registro separado; traduções textuais permitidas não exigem relatório repetido de exceção.

## Verificação

Execute `python scripts/harness.py` e os testes relevantes antes de concluir. O harness é um adaptador local limitado; não é uma auditoria OSPS/NIST/DORA. Informe comandos executados, resultados, limitações e verificações não executadas.

Quando uma alteração material afetar arquitetura, segurança ou release, atualize os documentos correspondentes.
