# PsicoIA — Bloco 19: localização PT-BR

**Resultado: PARTIAL; sem novo conteúdo integrado.** Nenhum texto operacional novo restou no escopo local já autorizado: as mensagens/labels de interface existentes têm valores PT-BR e inglês no mapa `src/web/src/i18n.jsx`; erros da interface também passam pelo mapeamento localizado. As verificações confirmaram seleção de idioma, identidade e contratos, mas não houve aumento de cobertura. Não classifico o bloco como concluído.

## Base e medição

- Branch: `reconciliation/psicoia-block18-translation`.
- HEAD inicial: `0cd961626042e3d38a8909f6b235781ef4b9f143`.
- Cobertura anterior → atual: PT-BR **16/30 catálogos, 1.233/5.158 registros → 16/30, 1.233/5.158**; EN **8/30, 141/5.158 → 8/30, 141/5.158**.
- Novos registros traduzidos neste bloco: **0**. Registros sem tradução não foram contados como traduzidos.

## Escopo inspecionado e pendências específicas

- Mensagens de interface, feedback operacional, status e labels em `src/web/src/` já têm valores PT-BR/EN nas estruturas de localização ou mapeamentos por estado; não dupliquei essas traduções.
- `prompts/public/` contém instruções para geração de fala de aconselhamento e uso de contexto em sessões; `prompts/psychagent/skill/select_skill/` contém instrução de seleção para recuperação. São textos que afetam comportamento/recuperação, não mera apresentação. Permanecem pendentes de avaliação de regressão em conjunto fixo e revisão de efeitos antes de integração.
- Instruções de diálogo da pessoa simulada e textos de abordagem/etapa em `src/web/backend/` também influenciam contexto comportamental/clinical; não foram traduzidos neste bloco.
- A pendência desses materiais é específica de comportamento, conteúdo ou adaptação; não é o `GAP` do harness de licença. O registro de distribuição/proveniência permanece em `PSICOIA_BLOCK17_PROVENANCE_RESULT.md`; não foi refeito.

## Verificação funcional

- `python scripts/check_localization.py` — **45 testes Python e 6 Node passaram**. Inclui identidade PsicoIA, seleção de idioma, valores de API, carregamento de localização/cache e labels/status web. Não executa gates de release/distribuição.
- `python scripts/validate_skill_catalog_locales.py --locale pt-BR --allow-missing` — **16/30; 1.233/5.158**.
- `python scripts/validate_skill_catalog_locales.py --locale en --allow-missing` — **8/30; 141/5.158**.
- `git diff --check` — passou antes da criação deste relatório.
- Navegador/API ao vivo — não executados neste bloco; não houve mudança em runtime. A execução Chromium anterior está registrada em `PSICOIA_BLOCK18B_RESULT.md`.

## Fechamento

O gate funcional das localizações existentes passou, mas o objetivo de adicionar traduções novas e aumentar cobertura **não foi satisfeito**. Nenhum prompt, catálogo, escala ou conteúdo clínico foi modificado. Próximo avanço de conteúdo exige um conjunto concretamente elegível e, para prompts/recuperação, testes de regressão e avaliação de efeitos; não repetir a análise geral do Bloco 17. Sem publicação, push, PR ou merge.
