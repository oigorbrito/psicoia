# Instruções para agentes

1. Identidade canônica: **PsicoIA**. Idioma principal: português brasileiro (`pt-BR`); inglês (`en`) é secundário quando fizer parte do escopo.
2. Priorize traduzir textos elegíveis, preservar funcionalidades e continuar em lotes independentes.
3. Não altere IDs, nomes técnicos, APIs, schemas, dados, placeholders, formatos ou contratos para facilitar a tradução.
4. Preserve originais, avisos autorais, atribuição acadêmica e restrições específicas do material. Avalie separadamente localização própria, adaptação de material upstream, prompts comportamentais, conteúdo clínico e distribuição.
5. Não trate um `GAP` documental de distribuição como falha automática de localização; a falta de publicação também não concede, por si só, direitos de adaptação.
6. Execute `python scripts/check_localization.py` e os testes relevantes; corrija regressões demonstradas. O harness de distribuição, quando executado, é um gate separado.
7. Operações Git remotas dependem de solicitação explícita do responsável pelo projeto. Não realizar push, PR, merge ou publicação por iniciativa do agente. Quando solicitadas, executar somente após confirmar os requisitos técnicos e as permissões aplicáveis ao conteúdo específico.
8. Mantenha mudanças pequenas; não reabra auditorias ou relatórios históricos sem mudança material de escopo ou evidência.
