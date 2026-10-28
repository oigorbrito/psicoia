# Roadmap de migração e localização

Este roadmap prioriza ações com base nas evidências locais registradas. **Não é promessa de prazo, garantia de release, avaliação clínica nem afirmação de conformidade.** A ordem pode mudar quando surgirem novas evidências; itens sem responsável, estimativa ou critério concluído não devem ser tratados como compromissos. A regra de migração é cópia literal: preservar o código upstream e não introduzir melhorias, correções ou mudanças funcionais. Só são permitidas a tradução aprovada de conteúdo voltado a pessoas (PT-BR principal e inglês secundário) e a troca da marca visível para PsicoIA onde isso não afete identificadores ou atribuição. Consulte a [política de migração e tradução](MIGRATION-POLICY.pt-BR.md).

## Prioridade 0 — preservar e integrar com proveniência

**Estado: commits locais de integração e governança/documentação criados; sem push.** A árvore fonte anterior contém 1.390 caminhos não rastreados nesta fotografia; `master`, `original` e `origin/main` têm históricos sem ancestral comum. O candidato está na branch `integration/psicoia`, em worktree separada, baseada em `origin/main`; `af5cc72` integra `original` com `origin/main`. `origin/main` contém o template de evidências, enquanto `original` acompanha o upstream PsychAgent. Um arquivo da árvore local foi criado fora do repositório em `../psicoia-worktree-before-integration.tar.gz` (52 MB), e um bundle Git em `../psicoia-git-refs-before-integration.bundle` (54 MB). A listagem do arquivo e o bundle foram verificados. SHA-256: árvore `bf5ea3b95581ded2e29ff1a97243a23d63759f7a65c0086d097f6fc18b597bc0`; bundle `0fef368c5132d1bba52e8b8b08905f47df510ae837999adce8cc6150276ec939`. Ambos estão no mesmo volume local; não são backup independente contra falha desse disco.

- A árvore de origem e os refs/histórico Git foram salvaguardados em arquivos separados e verificados; preserve-os até a integração ser revisada. Para recuperação de desastre, copie-os também para outro volume/local seguro.
- O candidato separado usa `origin/main` como base; o merge do código de `original` está em `af5cc72` e a governança/documentação em `10a251f`, sem alterar a árvore original.
- Revisar a lista de arquivos a incluir; excluir caches, arquivos de editor, temporários, segredos e artefatos gerados.
- Manter o upstream como referência; não fazer rebase entre históricos sem ancestral comum nem force push.

**Critério de conclusão:** base, commits/SHAs e arquivos incluídos/excluídos documentados; integração revisável e sem perda de trabalho.

## Prioridade 1 — classificar diferenças em relação ao upstream

**Estado: triagem por grupos concluída; revisão linha a linha pendente.** No snapshot `469f45ef468b968b3fccd1936d7e6a0a574e4c5c`, 1.292 dos 1.393 caminhos rastreados pelo upstream estavam idênticos; 101 diferiam e nenhum estava ausente. A árvore também contém 73 arquivos locais adicionais (excluindo caches e lixo de editor); dois catálogos têm sufixo `.partial`. Consulte o inventário para as categorias e decisões pendentes.

- Classificar cada caminho diferente como tradução aprovada, alteração de marca em prosa, arquivo upstream adicionado/removido ou desconhecido.
- Tratar qualquer diferença de lógica, dependência, dado, interface técnica ou identificador como desvio: não incorporar como parte da cópia literal; reverter ou pedir autorização separada antes de alterar.
- Inspecionar com prioridade prompts, configurações, dados, perfis, catálogos e contratos técnicos, preservando-os sem alteração não autorizada.
- Atualizar `docs/MIGRACAO-UPSTREAM.pt-BR.md` e `docs/INVENTARIO-DIFERENCAS-UPSTREAM.pt-BR.md` com decisões e evidência, inclusive itens ainda sem resolução.

**Critério de conclusão:** inventário reproduzível com classificação e justificativa para cada diferença relevante; itens sem evidência permanecem marcados como pendentes.

## Prioridade 1 — licença e proveniência

**Estado: lacuna confirmada localmente.** O harness não encontrou arquivo de licença reconhecido; o snapshot upstream consultado também não lista `LICENSE`, `COPYING` ou `LICENSES`. Isso não determina a titularidade nem autoriza redistribuição.

- Verificar direitos e termos aplicáveis ao código, modelos, datasets, perfis, imagens, prompts e demais dependências.
- Obter orientação/autorização apropriada antes de escolher ou declarar uma licença para o conjunto migrado.
- Não adicionar uma licença por conveniência nem publicar conteúdo cuja proveniência esteja incerta.

**Critério de conclusão:** decisão documentada com evidência e texto de licença aplicável, ou restrições explícitas de distribuição.

## Prioridade 2 — validação técnica

**Estado: verificado parcialmente no candidato `af5cc72` e na documentação staged.** `python -m pytest -q --import-mode=importlib`: 9 passaram. `python -m pytest -q`: falha na coleta por colisão de módulo entre os dois arquivos `test_harness.py` do repositório e do template. Harness: lacuna de licença e testes web ausentes; estado externo desconhecido. A suíte web e os validadores de catálogos não foram incluídos porque dependem de localização pendente.

- Registrar e investigar a discrepância entre a expectativa de 23 e a contagem observada de 24; não alterar testes ou código para eliminar a falha sem autorização explícita e confirmação do critério esperado.
- Reexecutar pytest, testes web, validadores e harness na branch de integração após a revisão final; documentar a limitação de coleta do pytest padrão e a ausência atual de testes web.
- Executar build e validações de inicialização/documentação quando as dependências e o ambiente estiverem disponíveis; registrar falhas e limitações.

**Critério de conclusão:** comandos e resultados registrados no estado integrado, com falhas não resolvidas identificadas — não ocultadas.

## Prioridade 2 — localização controlada

**Estado: PT-BR é o objetivo de localização; implementação de idioma no código pendente de revisão separada.** Inglês é secundário. A interface e os padrões upstream permanecem inalterados neste candidato; a implementação local que propaga `output_language`, altera contratos da web ou seleciona catálogos por idioma fica pendente: não expandir, integrar nem remover até revisão específica, preservando a cópia local existente. A validação estrutural do trabalho local informa PT-BR em 16/30 catálogos (1.233/5.158 registros) e inglês em 8/30 (141/5.158); esses catálogos não foram incluídos aqui. Os 60 arquivos de avaliação em `prompts/eval/` contêm texto chinês.

- Continuar com documentação e texto de apresentação aprovado, mantendo PT-BR como principal. Não ampliar alterações de código/contrato para localização enquanto a exceção de `output_language` estiver pendente.
- Conservar contratos, exemplos que sejam dados/conteúdo de pesquisa e nomes técnicos. Trocar `PsychAgent` por `PsicoIA` apenas em prosa de apresentação referente ao produto de destino; preservar atribuição acadêmica e upstream.
- Tratar tradução de prompts de avaliação como alteração comportamental, exigindo benchmark fixo, checagem de esquema e revisão humana antes de uso como substituição.
- Para catálogos, criar/atualizar embeddings por idioma e validar recuperação antes de habilitar textos localizados na recuperação.
- Atualizar contagens apenas com validação reproduzível; cobertura estrutural não significa revisão linguística concluída.

**Critério de conclusão:** escopo e cobertura declarados, validações apropriadas ao tipo de conteúdo registradas, sem alegar localização completa indevidamente.

## Prioridade 3 — controles externos e publicação

**Estado: desconhecido externamente.** As configurações hospedadas do GitHub, MFA, regras de branch, usuários ativos, releases publicados, canal privado de relato e implantação não foram comprovados pela árvore local.

- Consultar a plataforma por fonte autoritativa antes de documentar esses estados.
- Definir canal privado de vulnerabilidades, suporte e processo de release antes de anunciar garantias correspondentes.
- Só habilitar CI/controles hospedados depois de revisar permissões, pinning de actions e política do repositório.

**Critério de conclusão:** evidência externa com fonte e data de verificação, ou manter explicitamente como `UNKNOWN_EXTERNAL`.

## Atualização

Atualize este roadmap após mudanças materiais de branch/base, licença, escopo de tradução, resultados de testes ou estado externo. Registre fatos; não invente prazos nem converta objetivo em promessa.
