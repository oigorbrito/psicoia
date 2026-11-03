---
name: psicoia-migration-translation
description: Preserve PsychAgent provenance and literal code during PsicoIA migration; use the localization guardrails for text changes.
compatibility: Requires Git repository access; tests/builds may require project dependencies.
---

# Migração PsychAgent → PsicoIA

Use esta skill para cópia, comparação ou alterações que toquem a migração/upstream. Para tradução, aplique a orientação técnica canônica em `.agents/skills/localization-guardrails/SKILL.md` e a classificação de operações em `docs/MIGRATION-POLICY.pt-BR.md`.

## Regras específicas de migração

- Preserve código, comportamento, caminhos, IDs e contratos da origem; não faça refatorações, correções ou atualizações incidentais.
- Preserve avisos autorais e atribuição acadêmica. Use PsicoIA apenas como marca visível do produto de destino; não atribua o trabalho upstream ao PsicoIA.
- Registre SHA/ref de origem e compare arquivos somente quando a tarefa copiar ou alterar material upstream ou tratar de proveniência. Não repita essa comparação/auditoria em localização de software próprio sem mudança de escopo.
- Diferencie adaptação local de material upstream de publicação/redistribuição. A falta de autorização de distribuição não é uma proibição geral de trabalho local nem uma autorização para adaptar. Avalie a operação e o material concretos; preserve a origem quando a base aplicável não estiver estabelecida.
- Prompts e catálogos podem alterar geração/recuperação; use regressões e avaliação apropriadas antes de integrar variantes. Revisão funcional não substitui validação clínica.
- Não renomeie identificadores técnicos ou recursos para traduzir texto. Não apague arquivos ou histórico sem instrução explícita.

Não repita inventários ou relatórios de proveniência históricos para tarefas independentes. Registre somente decisões e limitações novas que sejam necessárias para a mudança atual.
