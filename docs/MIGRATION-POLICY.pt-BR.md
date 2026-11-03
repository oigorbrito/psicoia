# Política de localização, adaptação e migração

## Identidade e preservação

O nome canônico de apresentação é **PsicoIA**; o slug é `psicoia`. Use PsicoIA ao nomear o produto de destino. Preserve PsychAgent, títulos, autores, modelos, citações e avisos quando forem atribuição à origem acadêmica.

A migração de código continua literal: não refatore, corrija, modernize nem altere lógica, dependências, dados, contratos ou comportamento incidentalmente. Na tradução, preserve IDs, chaves, schemas, rotas, enums, placeholders/Jinja, markup, caminhos, formatos de saída e pontuação funcional.

## Classifique a operação concreta

1. **Localização de software próprio:** traduza a interface, documentação e prosa operacional própria da PsicoIA para PT-BR; mantenha EN quando já fizer parte do fluxo. Reuse os recursos de idioma existentes e teste seleção de locale, placeholders e contratos. Uma lacuna de distribuição não é critério automático de rejeição dessa localização.
2. **Adaptação local de material upstream:** não presuma nem proibição geral nem autorização. Avalie o material e o ato concreto (uso, cópia, tradução/adaptação e eventual integração). Direitos de redistribuição desconhecidos não bloqueiam automaticamente todo trabalho local; manter o trabalho local também não concede direitos. Se a base aplicável não estiver estabelecida para o material específico, preserve-o e prossiga com trabalho independente elegível.
3. **Prompts e recuperação:** são sensíveis a comportamento. Preserve a versão original; antes de integrar uma variante, confira placeholders e formatos, compare casos fixos e avalie efeitos funcionais. Não declare equivalência comportamental só por testes estruturais.
4. **Conteúdo clínico e instrumentos:** tradução técnica não é validação clínica. Instrumentos, escalas e conteúdo clínico que exija revisão especializada permanecem separados até haver a revisão e a base de uso/adaptação aplicáveis.
5. **Publicação e redistribuição:** é um gate independente. Não publique nem redistribua material sem autorização suficiente e sem preservar os avisos/atribuições exigidos. Não use o resultado do harness como decisão jurídica.

Essas categorias não se bloqueiam mutuamente: uma pendência de prompt, catálogo ou publicação não interrompe localização própria independente. Não repita auditorias gerais em lotes sem mudança material de escopo; avalie somente o material e a operação que serão alterados.

## Catálogos e dados

Catálogos usados na recuperação exigem arquivos e caches separados por idioma e validação da recuperação; não reutilize embeddings do texto-fonte para uma versão localizada nem sobrescreva o original. Preserve IDs e relações como `skill_id`, `parent_ids` e `sect`. Não traduza incidentalmente benchmarks, perfis, exemplos de avaliação, dados ou itens de instrumentos.

## Processo curto

1. Identifique o conteúdo e classifique a operação acima; não faça inventário fora do escopo.
2. Faça a menor tradução que preserve sentido, segurança, identificadores e contratos; mantenha o original quando necessário.
3. Rode `python scripts/check_localization.py` e os testes/build relevantes. Compare os fluxos afetados; registre limitações sem transformar evidência ausente em aprovação.
4. Atualize documentação somente quando a mudança material exigir; relatórios antigos são evidência histórica, não instruções operacionais.
