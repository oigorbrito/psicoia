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

**Estado: o Block 08 auditou por classe as 104 diferenças da árvore fonte; a validação semântica continua pendente onde indicado.** Contra o snapshot upstream `469f45ef468b968b3fccd1936d7e6a0a574e4c5c`, 1.289 dos 1.393 caminhos são idênticos, 104 diferem e nenhum está ausente. A normalização AST encontrou 12 diferenças estruturais entre 41 arquivos Python alterados. A árvore fonte contém 74 adições locais (excluídos caches e lixo de editor); dois catálogos têm sufixo `.partial`. Consulte `PSICOIA_BLOCK08_RESULT.md` e o inventário.

- Revisar semanticamente a prosa dos oito READMEs localizados e os 33 prompts (incluindo diferenças de placeholders/defaults e a perda de três ocorrências de `{{number}}` no seletor de habilidades).
- Tratar mudanças de API, runtime, defaults, parsing e recuperação como desvios bloqueadores; não incorporá-las sem autorização separada e validação adequada.
- Manter em revisão específica prompts de avaliação/reparo, dados, perfis, catálogos e contratos técnicos; nunca inferir que teste estrutural comprova equivalência clínica ou comportamental.
- Registrar em `docs/MIGRACAO-UPSTREAM.pt-BR.md` qualquer nova decisão, validação ou evidência; manter itens sem evidência como pendentes.

**Critério de conclusão:** inventário reproduzível com classificação e justificativa para cada diferença relevante; itens sem evidência permanecem marcados como pendentes.

## Prioridade 1 — licença e proveniência

**Estado: preferência do usuário registrada; aplicação bloqueada por proveniência/autoridade.** O usuário escolheu MIT como licença desejada. O harness ainda não encontra arquivo de licença reconhecido; o snapshot upstream não lista `LICENSE`, `COPYING` ou `LICENSES`. A escolha não comprova titularidade nem autorização para relicenciar o código upstream.

- Confirmar evidência de autoridade para aplicar MIT ao conteúdo pretendido, incluindo código upstream, modelos, datasets, perfis, imagens, prompts e dependências.
- Obter o nome exato do titular e o ano para o aviso de copyright.
- Não criar nem declarar `LICENSE` até esses pontos serem resolvidos; não publicar conteúdo de proveniência incerta.

**Critério de conclusão:** evidência de autoridade, titular/ano confirmados e texto MIT aplicável, ou restrições explícitas de distribuição.

## Prioridade 2 — validação técnica

**Estado: verificado localmente em `reconciliation/psicoia-block08` (2026-10-29).** `python -m pytest -q`: 17 passaram; os testes do template foram executados separadamente: 4 passaram. Testes Node em `src/web`: 2 passaram; build Vite e import smoke do backend passaram (20 rotas). O harness registra a lacuna de licença e controles externos desconhecidos. `npm audit` encontrou 9 advisories; `pip-audit` encontrou 14 registros para Starlette. Nenhuma atualização de dependência nem alegação de prontidão para produção foi feita.

- `pytest.ini` limita a coleta padrão aos testes do projeto e evita a colisão de `test_harness` sem excluir conteúdo do template.
- Os testes web cobrem somente funções puras de domínio/helpers; fluxos completos de API, UI React, autenticação/CORS e qualidade da localização continuam sem teste. Validadores de catálogo permanecem fora do candidato enquanto a revisão de locale/recuperação estiver pendente.
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
