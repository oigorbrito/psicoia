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

1. Antes de editar, registre a branch/ref e SHA de origem e destino e examine `git status`. Não descarte, resete, force-push ou sobrescreva trabalho local.
2. Compare arquivos com a branch `original` por caminho e conteúdo. Classifique diferenças como texto de apresentação/branding permitido, tradução aprovada, arquivo upstream novo/removido ou desconhecida. Diferença funcional ou mudança em identificador técnico é desvio bloqueador: reverta ou peça autorização explícita e mantenha-a isolada. Não atribua autoria/causa sem evidência.
3. Preserve a branch upstream como referência imutável para comparação. Faça alterações em branch de trabalho derivada da base de integração aprovada; se os históricos não tiverem ancestral comum, não tente rebase convencional. Planeje integração explícita e revisável, sem force push.
4. Mantenha registro de migração revisável (por exemplo, `docs/UPSTREAM-MIGRATION.md`) com refs/SHAs, caminhos alterados, decisão e validações. Marque dúvidas como pendentes; não converta arquivos ausentes ou inacessíveis em equivalência.
5. Preserve arquivos e documentação preexistentes. Prefira alterações pontuais; ao reconciliar documentos homônimos, retenha conteúdo útil de ambas as fontes e registre o que foi adotado ou deixado de fora.
6. Antes de adicionar arquivos, inspecione dados, licenças, proveniência, segredos e artefatos gerados. Não use `git add -A` sem revisão. Exclua caches, ambientes, segredos, arquivos temporários e lixo do editor.

## Regras de localização

- Traduza apenas prosa destinada a pessoas usuárias ou documentação aprovada. Use PT-BR claro e neutralidade clínica; produza a versão inglesa correspondente quando o escopo exigir localização bilíngue.
- Preserve exatamente contratos e elementos legíveis por máquina: identificadores, filenames, imports, rotas, flags CLI, variáveis de ambiente, chaves JSON/YAML, enumerações, IDs, placeholders, expressões Jinja, comandos, URLs e caminhos.
- Preserve nomes de modelos, siglas terapêuticas, citações, métricas e atribuição ao trabalho upstream. Não apresente PsychAgent como trabalho original de PsicoIA nem altere resultados publicados.
- Traduções locais experimentais de material upstream só podem ocorrer quando houver base aplicável para uso/adaptação e revisão de proveniência. A ausência de publicação, uma cópia local ou a ausência de `LICENSE` não concede autorização. Não traduza incidentalmente `data/`, `assets/profiles/`, benchmarks, respostas de avaliação ou itens de instrumentos clínicos.
- Trate prompts comportamentais e textos usados em recuperação como alterações sensíveis ao comportamento: antes da integração, preserve o original, valide placeholders/esquemas, execute testes de regressão num conjunto fixo e avalie efeitos funcionais com revisão humana. Não afirme equivalência comportamental apenas por testes estruturais.
- Traduções de instrumentos clínicos, escalas padronizadas e outros materiais protegidos exigem revisão de direitos e validação especializada; validação funcional não substitui validação clínica.
- Catálogos de habilidades alimentam recuperação: cada idioma requer embeddings/cache próprios e validação de recuperação. Nunca reutilize embeddings do chinês ou inglês para texto traduzido.
- A falta de `LICENSE` indicada pelo harness é uma lacuna de evidência do repositório, não um bloqueio técnico automático para trabalho local independente autorizado. Não publique nem redistribua conteúdo de direitos incertos sem autorização suficiente.
- Não renomeie imagens ou recursos por causa de caracteres chineses em seus caminhos sem renomear os arquivos e atualizar/verificar todas as referências.

## Processo de trabalho

1. Declare escopo, base de comparação, critérios de aceite e conteúdo excluído; siga `docs/MIGRATION-POLICY.pt-BR.md`.
2. Faça inventário dos arquivos relevantes e estabeleça testes/validações de baseline quando viável. Registre falhas preexistentes antes de editar.
3. Separe cópia literal, tradução e alteração de marca em revisões distintas quando possível. Não faça migração funcional; exceções exigem autorização explícita, justificativa separada e diff isolado.
4. Verifique equivalência estrutural entre PT-BR e inglês onde ambos forem exigidos; valide links, caminhos, encoding, markup, variáveis e cobertura de locale.
5. Execute os testes relevantes: pytest para Python, testes/build da web, validadores de catálogo e harness conforme a mudança. Informe exatamente quais comandos foram executados e resultados; não declare PASS por inferência.
6. Revise o diff em relação ao SHA upstream e ao estado anterior, incluindo arquivos não rastreados e removidos. Procure alterações acidentais de dados, contratos, comportamento, atribuição e licença.

## Relato final obrigatório

Informe: escopo realizado; refs/SHAs comparados; arquivos alterados e decisões de migração; o que ficou sem traduzir e por quê; testes executados e resultados; falhas preexistentes; lacunas de licença, proveniência ou validação; e se há arquivos ainda não rastreados. Não declare localização completa, equivalência com upstream, prontidão de release, segurança ou conformidade sem evidência verificável.
