# Instruções para agentes

Estas instruções são regras locais de trabalho; não representam certificação ou conformidade externa.

## Antes de alterar

1. Leia `policy/project-state.json`, `docs/MATURITY.md`, `docs/ARCHITECTURE.md`, `docs/TESTING.md`, `docs/HARNESS.md` e `docs/MIGRATION-POLICY.pt-BR.md`.
2. Confira `docs/SOURCES.md` antes de fazer afirmações factuais sobre o projeto ou citar padrões externos.
3. Não transforme evidência ausente, desatualizada ou não executada em aprovação.
4. Use os estados `PASS`, `GAP`, `UNKNOWN_EXTERNAL`, `NOT_APPLICABLE` e `NOT_RUN` somente com os significados descritos em `docs/TESTING.md`.
5. Não declare conformidade, maturidade, segurança, prontidão de produção ou equivalência clínica sem evidência verificável.
6. Para a migração PsychAgent → PsicoIA, preserve a cópia funcional do código: não faça refatorações, correções, melhorias, atualizações ou mudanças de comportamento. São permitidas as traduções textuais aprovadas pela regra 7, sem alterar lógica, identificadores, APIs, caminhos, dados ou atribuição acadêmica; a mudança de marca continua limitada a texto de apresentação voltado a pessoas.
7. No escopo deste trabalho, está autorizada a localização local de interface, documentação e prosa operacional própria da PsicoIA para PT-BR (principal) e inglês (secundário), sem alterar comportamento ou contratos. Traduções locais experimentais de material upstream só podem ser feitas quando houver base aplicável para uso/adaptação; a ausência de publicação não presume essa autorização. Prompts comportamentais e textos de recuperação só podem ser integrados após testes de regressão e avaliação dos efeitos funcionais. Instrumentos clínicos, escalas padronizadas e materiais protegidos exigem revisão de direitos e validação especializada. A ausência de `LICENSE` indicada pelo harness não impede, por si só, tarefas locais independentes; nenhum conteúdo de direitos incertos pode ser publicado ou redistribuído sem autorização suficiente.
8. Preserve os documentos existentes e faça alterações pequenas. Não adicione controles apenas para aparentar maturidade; registre separadamente qualquer exceção autorizada à cópia literal.

## Verificação

Execute `python scripts/harness.py` e os testes relevantes antes de concluir. O harness é um adaptador local limitado; não é uma auditoria OSPS/NIST/DORA. Informe comandos executados, resultados, limitações e verificações não executadas.

Quando uma alteração material afetar arquitetura, segurança ou release, atualize os documentos correspondentes.
