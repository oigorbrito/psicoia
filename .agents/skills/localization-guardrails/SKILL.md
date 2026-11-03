---
name: localization-guardrails
description: Localize eligible PsicoIA UI, documentation, and operational text into Brazilian Portuguese and English while preserving behavior and contracts.
compatibility: Requires repository access; Python and Node/npm may be needed for validation.
---

# Localização do PsicoIA

Use esta skill como orientação canônica para localização técnica. O idioma principal é PT-BR; mantenha inglês quando fizer parte do fluxo ou do escopo.

## Limites

- Traduza prosa visível e operacional elegível; não use tradução para refatorar, corrigir ou redesenhar o produto.
- Preserve exatamente identificadores, IDs, nomes de arquivos, APIs, schemas, campos, enums, dados, caminhos, comandos e attribution.
- Preserve placeholders, inclusive `{{ ... }}` e `{% ... %}`, formatos JSON/XML, marcação, pontuação de controle e defaults.
- Não traduza nomes técnicos, chaves serializadas, benchmarks, perfis, dados de pesquisa ou itens de instrumentos como limpeza incidental.
- Separe localização própria, adaptação de material upstream, alteração de prompt comportamental, validação clínica e redistribuição conforme `docs/MIGRATION-POLICY.pt-BR.md`. Lacuna de redistribuição não é proibição técnica geral; trabalho local tampouco comprova direito de adaptação.

## Fluxo

1. Delimite apenas os arquivos e strings afetados e reutilize o mecanismo de locale existente.
2. Preserve o original quando necessário. Para prompts, fixe casos de regressão e avalie efeitos; para catálogos de recuperação, mantenha sidecars/caches por idioma e valide a recuperação. Não alegue equivalência clínica ou comportamental sem evidência adequada.
3. Execute `python scripts/check_localization.py` e os testes/build relevantes; corrija regressões introduzidas.
4. Informe mudanças efetivas, cobertura e pendências específicas. Não reabra relatórios históricos ou gates de publicação sem mudança material de escopo.
