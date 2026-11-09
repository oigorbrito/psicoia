# Roadmap de migração e localização

Este roadmap prioriza ações com base nas evidências locais registradas. **Não é promessa de prazo, garantia de release, avaliação clínica nem afirmação de conformidade.** A ordem pode mudar quando surgirem novas evidências; itens sem responsável, estimativa ou critério concluído não devem ser tratados como compromissos. A regra de migração é cópia literal: preservar o código upstream e não introduzir melhorias, correções ou mudanças funcionais. Só são permitidas a tradução aprovada de conteúdo voltado a pessoas (PT-BR principal e inglês secundário) e a troca da marca visível para PsicoIA onde isso não afete identificadores ou atribuição..

**Exceção delimitada autorizada nesta tarefa:** implementar um novo cliente Android em `android/`, com testes e documentação de apoio. Isso não autoriza alterações no comportamento da aplicação upstream existente, no texto/IDs dos catálogos, nos prompts clínicos de avaliação nem a publicação. Consulte [Cliente Android offline](ANDROID_OFFLINE.pt-BR.md).

## Prioridade 0 — preservar e integrar com proveniência

**Estado: salvaguarda e inventário inicial concluídos; integração pendente.** A árvore contém 1.390 caminhos não rastreados nesta fotografia; `master`, `original` e `origin/main` têm históricos sem ancestral comum. `origin/main` contém o template de evidências, enquanto `original` acompanha o upstream PsychAgent. Um arquivo da árvore local foi criado fora do repositório em `../psicoia-worktree-before-integration.tar.gz` (52 MB), e um bundle Git em `../psicoia-git-refs-before-integration.bundle` (54 MB). A listagem do arquivo e o bundle foram verificados. SHA-256: árvore `bf5ea3b95581ded2e29ff1a97243a23d63759f7a65c0086d097f6fc18b597bc0`; bundle `0fef368c5132d1bba52e8b8b08905f47df510ae837999adce8cc6150276ec939`. Ambos estão no mesmo volume local; não são backup independente contra falha desse disco.

- A árvore e os refs/histórico Git foram salvaguardados em arquivos separados e verificados; preserve-os até a integração ser revisada. Para recuperação de desastre, copie-os também para outro volume/local seguro.
- Definir a base de integração e reconciliar o template com o código/documentação do PsicoIA sem sobrescrever conteúdo útil nem alterar o código-fonte upstream.
- Revisar a lista de arquivos a incluir; excluir caches, arquivos de editor, temporários, segredos e artefatos gerados.
- Manter o upstream como referência; não fazer rebase entre históricos sem ancestral comum nem force push.

**Critério de conclusão:** base, commits/SHAs e arquivos incluídos/excluídos documentados; integração revisável e sem perda de trabalho.

## Prioridade 1 — classificar diferenças em relação ao upstream

**Estado: triagem por grupos concluída; revisão linha a linha pendente.** Contra o snapshot `469f45ef468b968b3fccd1936d7e6a0a574e4c5c`, a comparação byte a byte atual encontra 1.289 de 1.393 caminhos upstream idênticos; 104 diferem e nenhum está ausente. A árvore também contém 74 arquivos locais adicionais (excluindo caches e arquivos de editor); dois catálogos têm sufixo `.partial`. Consulte o inventário atualizado para categorias e decisões pendentes.

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

**Estado: parcialmente verificado nas duas árvores locais; nenhuma está pronta para release.** `master` local: pytest 47 passaram, com 2 subtestes aprovados; `compileall` passou; testes web 7/7 passaram; `npm ci --ignore-scripts` e `npm run build` passaram. Os validadores de catálogo informam PT-BR 16/30 (1.233/5.158 registros) e inglês 8/30 (141/5.158); o teste espera 24 arquivos completos `.json` e exclui dois rascunhos `.json.partial`. Um ambiente isolado com as dependências web passou em `pip check` e importação da aplicação (20 rotas). O `pip check` global falha por conflito de um `rpy 0.1.1` instalado fora do projeto, que exige `openai<2`, enquanto o ambiente global tem OpenAI 2.54.0. O requisito web permite qualquer `openai>=1.0.0`; nova resolução selecionou 3.41.0, portanto compatibilidade com versões principais do SDK precisa ser revisada. `npm audit` informa 9 avisos (6 altos, 2 moderados, 1 baixo, 0 críticos), incluindo `vite` como dependência direta; a simulação indica que a correção do Vite exige atualização de versão principal (8.3.5) e não elimina os avisos sem essa revisão. Nenhuma atualização automática foi aplicada. `pip-audit` no ambiente web isolado encontrou 14 registros de avisos para `starlette==0.37.2`, dependência transitiva; `fastapi==0.110.2` fixa Starlette em `<0.38`, então a correção requer atualização coordenada do framework e testes de regressão. A revisão de segurança também encontrou defaults de demonstração herdados: hash SHA-256 rápido e sem salt por senha, sem verificação de expiração de token, CORS com credenciais e origem curinga, exemplo de servidor em `0.0.0.0` com `--reload` e bearer tokens em `localStorage`. Esses defaults já existiam no upstream e não foram alterados; a aplicação web não está pronta para produção. Na candidata `integration/psicoia`, a coleta do pytest padrão falha por colisão do módulo `test_harness` entre a raiz e `evidence-repo-template`; `--import-mode=importlib` passa 9 testes. O build com `npm ci --ignore-scripts` e o smoke test de importação web passam (20 rotas); não há arquivos de teste unitário frontend nessa branch. O harness retorna código 0, mas informa `GAP` para licença e testes web, além de `UNKNOWN_EXTERNAL`; no `master` local, informa `GAP` para licença e `UNKNOWN_EXTERNAL`, com arquivos de testes Python/web presentes. O resultado do harness não é avaliação de conformidade. Isso não comprova qualidade da tradução nem validade da recuperação.

- A antiga divergência 23/24 foi identificada como expectativa desatualizada: o teste percorre arquivos completos de idioma `.json`, e os 24 satisfazem o critério de contrato com a origem. A expectativa foi corrigida; nenhum conteúdo de catálogo foi alterado.
- Resolver a colisão que impede a coleta do pytest padrão na branch de integração; não tratar a opção `--import-mode=importlib` como correção. Executar o harness e definir/adicionar testes web antes de alegar validação integrada completa.
- Executar build e validações de inicialização/documentação quando as dependências e o ambiente estiverem disponíveis; registrar falhas e limitações.

**Critério de conclusão:** comandos e resultados registrados no estado integrado, com falhas não resolvidas identificadas — não ocultadas.

## Prioridade 2 — localização controlada

**Estado: PT-BR principal; implementação de idioma no código pendente de revisão separada.** PT-BR permanece como idioma principal/padrão e inglês como secundário. A implementação local que propaga `output_language`, altera contratos da web ou seleciona catálogos por idioma fica pendente: não expandir, integrar nem remover até revisão específica, preservando a cópia local existente. A validação estrutural atual informa PT-BR em 16/30 catálogos (1.233/5.158 registros) e inglês em 8/30 (141/5.158). Os 60 arquivos de avaliação em `prompts/eval/` contêm texto chinês.

- Continuar com documentação e texto de apresentação aprovado, mantendo PT-BR como principal. Não ampliar alterações de código/contrato para localização enquanto a exceção de `output_language` estiver pendente.
- Conservar contratos, exemplos que sejam dados/conteúdo de pesquisa e nomes técnicos. Trocar `PsychAgent` por `PsicoIA` apenas em prosa de apresentação referente ao produto de destino; preservar atribuição acadêmica e upstream.
- Tratar tradução de prompts de avaliação como alteração comportamental, exigindo benchmark fixo, checagem de esquema e revisão humana antes de uso como substituição.
- Para catálogos, criar/atualizar embeddings por idioma e validar recuperação antes de habilitar textos localizados na recuperação.
- Atualizar contagens apenas com validação reproduzível; cobertura estrutural não significa revisão linguística concluída.

**Critério de conclusão:** escopo e cobertura declarados, validações apropriadas ao tipo de conteúdo registradas, sem alegar localização completa indevidamente.

## Prioridade 3 — controles externos e publicação

**Estado: publicação bloqueada.** Não foi encontrado `LICENSE`/`COPYING` na árvore local nem no snapshot upstream; direitos e proveniência de código, modelo, dados, perfis, imagens e prompts permanecem sem comprovação. O lockfile web tem 9 avisos de npm, incluindo 6 altos; a stack web Python tem 14 registros de avisos do Starlette, e os defaults herdados de autenticação/CORS exigem revisão de segurança separada. Correções de dependências exigem testes de compatibilidade antes de distribuir. `gitleaks` encontrou 0 resultados na árvore de trabalho atual e 0 no histórico Git. `.gitignore` agora exclui `.vs/`, `.env*`, logs e o artefato local `nul`. `main` remota foi consultada novamente em 2026-10-29 e permanecia em `0ca22eb238828a84034535494d00c66396e12110`; não havia PR aberta. Configurações hospedadas do repositório, MFA, regras de branch, usuários ativos, releases publicados, canal privado de relato e implantação permanecem não verificadas externamente.

- Consultar a plataforma por fonte autoritativa antes de documentar esses estados.
- Definir canal privado de vulnerabilidades, suporte e processo de release antes de anunciar garantias correspondentes.
- Só habilitar CI/controles hospedados depois de revisar permissões, pinning de actions e política do repositório.

**Critério de conclusão:** evidência externa com fonte e data de verificação, ou manter explicitamente como `UNKNOWN_EXTERNAL`.

## Atualização

Atualize este roadmap após mudanças materiais de branch/base, licença, escopo de tradução, resultados de testes ou estado externo. Registre fatos; não invente prazos nem converta objetivo em promessa.
