---
name: psicoia-migration-translation
description: Migrate the PsychAgent upstream codebase into the PsicoIA project while translating approved user-facing content from Chinese to Brazilian Portuguese (primary) and English (secondary), preserving provenance, behavior, data, and verifiable evidence.
compatibility: Requires Git repository access. Tests, frontend builds, and locale validation may require project dependencies.
---

# Migração e localização do PsicoIA

Use esta skill quando a tarefa envolver migrar, comparar, renomear ou traduzir o repositório original PsychAgent para o projeto canônico `psicoia` / PsicoIA. Aplique também `.agents/skills/localization-guardrails/SKILL.md` quando estiver traduzindo conteúdo.

## Objetivo e limites

- Repositório de origem conhecido: `https://github.com/ECNU-ICALK/PsychAgent`.
- A branch `original` deve servir como referência upstream, acompanhada por `upstream/main`; confirme os refs e SHA atuais antes de comparar, pois branches podem avançar.
- O nome canônico de apresentação é **PsicoIA** e o slug do repositório é `psicoia`. Troque `PsychAgent` por `PsicoIA` somente em texto de apresentação voltado a pessoas quando nomear o produto migrado. Preserve nomes do upstream, artigo, autores, checkpoint/modelos publicados e atribuição acadêmica.
- Idioma principal do conteúdo novo/localizado: português brasileiro (`pt-BR`). Idioma secundário: inglês (`en`). Traduza prosa chinesa aprovada para ambos os idiomas; preserve material acadêmico/fonte quando necessário para proveniência.
- A regra da migração é cópia literal do código: nenhuma melhoria, refatoração, correção, atualização de dependência, formatação ampla ou alteração de comportamento. Consulte `docs/MIGRATION-POLICY.pt-BR.md`.
- Não assuma que todo o repositório deve ser traduzido. Neste trabalho, tarefas explicitamente aprovadas podem localizar localmente interface, documentação e prosa operacional própria da PsicoIA. Isso não autoriza tradução ou redistribuição de material upstream, de terceiros ou protegido.

## Regras de migração com proveniência

1. Antes de editar, registre o worktree, branch, HEAD e `git status`. Registre também SHA upstream somente em tarefas que copiem/alterem material upstream ou tratem migração/proveniência. Não descarte, resete, force-push ou sobrescreva trabalho local.
2. Em tarefas de migração/proveniência ou que alterem material upstream, compare os arquivos afetados com `original` por caminho e conteúdo. Para localização de software próprio sem mudança de escopo, verifique o diff contra a branch de trabalho e preserve contratos. Classifique diferenças upstream como apresentação/localização permitida, mudança funcional ou desconhecida; não atribua autoria/causa sem evidência.
3. Em tarefas de migração, preserve a branch upstream como referência imutável e trabalhe sobre a base de integração aprovada; se os históricos não tiverem ancestral comum, não tente rebase convencional. Localização de software próprio segue a branch de trabalho existente e não exige nova comparação/reconciliação de upstream.
4. Em alterações de migração/proveniência, mantenha registro revisável com refs/SHAs, caminhos e decisões. Marque dúvidas como pendentes; não repita esse registro em tarefas de localização que não alterem a base de proveniência.
5. Preserve arquivos e documentação preexistentes. Prefira alterações pontuais; ao reconciliar documentos homônimos, retenha conteúdo útil de ambas as fontes e registre o que foi adotado ou deixado de fora.
6. Ao adicionar material upstream/de terceiros ou preparar distribuição, confira os requisitos específicos de dados, licença e proveniência; não repita essa análise em alterações locais de software próprio sem mudança de escopo. Preserve avisos autorais; não use `git add -A` sem revisão e exclua caches, ambientes, segredos e temporários.

## Regras de localização

- Traduza apenas prosa destinada a pessoas usuárias ou documentação aprovada. Use PT-BR claro e neutralidade clínica; produza a versão inglesa correspondente quando o escopo exigir localização bilíngue.
- Preserve exatamente contratos e elementos legíveis por máquina: identificadores, filenames, imports, rotas, flags CLI, variáveis de ambiente, chaves JSON/YAML, enumerações, IDs, placeholders, expressões Jinja, comandos, URLs e caminhos.
- Preserve nomes de modelos, siglas terapêuticas, citações, métricas e atribuição ao trabalho upstream. Não apresente PsychAgent como trabalho original de PsicoIA nem altere resultados publicados.
- Para material upstream, de terceiros ou de pesquisa, siga a separação de direitos/distribuição em `docs/MIGRATION-POLICY.pt-BR.md`; não traduza incidentalmente `data/`, `assets/profiles/`, benchmarks, respostas de avaliação ou itens de instrumentos clínicos.
- Trate prompts comportamentais e textos usados em recuperação como alterações sensíveis ao comportamento: antes da integração, preserve o original, valide placeholders/esquemas, execute testes de regressão num conjunto fixo e avalie efeitos funcionais com revisão humana. Não afirme equivalência comportamental apenas por testes estruturais.
- Traduções de instrumentos clínicos, escalas padronizadas e outros materiais protegidos exigem revisão de direitos e validação especializada; validação funcional não substitui validação clínica.
- Catálogos de habilidades alimentam recuperação: cada idioma requer embeddings/cache próprios e validação de recuperação. Nunca reutilize embeddings do chinês ou inglês para texto traduzido.
- Não repita gates de publicação em testes locais de localização; antes de distribuir, aplique o gate separado definido em `docs/MIGRATION-POLICY.pt-BR.md`.
- Não renomeie imagens ou recursos por causa de caracteres chineses em seus caminhos sem renomear os arquivos e atualizar/verificar todas as referências.

## Processo de trabalho

1. Declare escopo, base de comparação, critérios de aceite e conteúdo excluído; siga `docs/MIGRATION-POLICY.pt-BR.md`.
2. Faça inventário dos arquivos relevantes e estabeleça testes/validações de baseline quando viável. Registre falhas preexistentes antes de editar.
3. Separe cópia literal, tradução e alteração de marca em revisões distintas quando possível. Não faça migração funcional; exceções exigem autorização explícita, justificativa separada e diff isolado.
4. Verifique equivalência estrutural entre PT-BR e inglês onde ambos forem exigidos; valide links, caminhos, encoding, markup, variáveis e cobertura de locale.
5. Execute os testes relevantes: pytest para Python, testes/build da web, validadores de catálogo e harness conforme a mudança. Informe exatamente quais comandos foram executados e resultados; não declare PASS por inferência.
6. Revise o diff em relação à base de trabalho, verificando arquivos alterados, contratos, comportamento e identificadores. Compare com upstream quando a alteração tocar conteúdo upstream ou quando a tarefa for de migração/proveniência.

## Relato final obrigatório

Informe mudanças efetivas, escopo/cobertura, testes executados, regressões e pendências funcionais. Registre separadamente direitos/distribuição somente quando forem alterados, relevantes ao escopo ou necessários para publicação; para o histórico já analisado, referencie `PSICOIA_BLOCK17_PROVENANCE_RESULT.md` em vez de repetir a auditoria. Não declare localização completa, equivalência comportamental, validação clínica, prontidão de release, segurança ou conformidade sem evidência verificável.
