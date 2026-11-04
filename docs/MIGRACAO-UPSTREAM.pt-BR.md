# Registro de migração do upstream

Este registro documenta observações locais para comparar o projeto `psicoia` com o upstream PsychAgent. A migração acordada é uma cópia literal do código, sem melhorias ou mudanças funcionais; a marca visível pode mudar para PsicoIA apenas em prosa de apresentação, e conteúdo aprovado pode ser traduzido para PT-BR principal e inglês secundário.. Este registro não declara equivalência, tradução completa, proveniência/licença aprovada ou prontidão de integração.

## Referências observadas

- Upstream: [ECNU-ICALK/PsychAgent](https://github.com/ECNU-ICALK/PsychAgent), `upstream/main`.
- Snapshot local da referência upstream: `469f45ef468b968b3fccd1936d7e6a0a574e4c5c` (branch local `original`, configurada para acompanhar `upstream/main` na última consulta).
- Repositório de destino: `oigorbrito/psicoia`, remote `origin`, branch `main` observada em `0ca22eb238828a84034535494d00c66396e12110`.
- Branch local de trabalho consultada: `master`, commit `e13c895850dc074fd5618322c5e7c1cfda34a29c`.

Os três snapshots de histórico consultados (`master`, `original` e `origin/main`) não têm ancestral comum. `origin/main` contém o template de evidências em `evidence-repo-template/`; não é a branch upstream do código PsychAgent.

## Comparação inicial de arquivos

A lista e a triagem por grupos estão em [Inventário inicial das diferenças upstream](INVENTARIO-DIFERENCAS-UPSTREAM.pt-BR.md). A primeira contagem foi corrigida após repetir a comparação com quoting UTF-8 desativado; consulte a nota de correção nesse inventário.

Na comparação byte a byte da árvore de trabalho local com os caminhos rastreados pelo commit upstream acima:

- arquivos rastreados pelo upstream: **1.393**;
- arquivos correspondentes presentes localmente: **1.393**;
- presentes e idênticos: **1.292**;
- presentes e diferentes: **101**;
- não encontrados localmente: **0**.

Esta é a contagem da fotografia inicial, não da revisão atual. A auditoria de publicação posterior registrou 1.289 idênticos, 104 diferentes e 0 ausentes; veja o inventário atualizado. Contagens por caminho não validam arquivos locais adicionais, licenças, direitos de redistribuição ou qualidade das traduções.

## Auditoria local de publicação

Na revisão local antes da preparação de qualquer branch de publicação:

- origem confirmada: `original`/`upstream/main` em `469f45ef468b968b3fccd1936d7e6a0a574e4c5c`; remoto de destino `oigorbrito/psicoia`/`origin/main` em `0ca22eb238828a84034535494d00c66396e12110` na consulta inicial e na reconsulta;
- comparação byte a byte contra a origem: 1.393 caminhos, 1.289 idênticos, 104 diferentes e 0 ausentes;
- três caminhos passaram a diferir desde a triagem inicial: `src/sample/main.py` (somente texto de ajuda da CLI), `src/web/package.json` e `src/web/package-lock.json` (nome privado do pacote alinhado para `psicoia-web`); nenhum contrato de CLI/API foi renomeado;
- `prompts/eval/SCL_90/SCL_90.txt` é byte-idêntico à origem; não houve alteração dos itens do instrumento nesse arquivo;
- a árvore em `master` está na commit `e13c895850dc074fd5618322c5e7c1cfda34a29c`; somente `.gitattributes` está rastreado nesse branch. O restante do projeto está local e não rastreado, portanto ainda não existe um diff de commit revisável para publicação;
- comparação estrutural AST dos 41 arquivos Python que diferem: 29 permanecem iguais após mascarar literais string/bytes e 12 diferem estruturalmente; igualdade AST não comprova equivalência comportamental;
- não foi encontrado `LICENSE`/`COPYING` na árvore local nem no snapshot upstream. Direitos de redistribuição continuam sem comprovação e bloqueiam qualquer push/PR público.

O repositório remoto foi consultado novamente: `main` continuava em `0ca22eb238828a84034535494d00c66396e12110` e não havia PR aberta. A branch `integration/psicoia` permanece local, 17 commits à frente, sem push. Nenhuma nova branch ou PR de publicação foi criada porque os gates de direitos e fidelidade funcional não passaram.

## Salvaguarda local antes da integração

- A árvore de trabalho tinha 113 MB e 1.389 caminhos não rastreados na fotografia inicial deste passo.
- Foi criado fora do repositório `../psicoia-worktree-before-integration.tar.gz` (52 MB), excluindo `.git`; o teste `tar -tzf` passou. SHA-256: `bf5ea3b95581ded2e29ff1a97243a23d63759f7a65c0086d097f6fc18b597bc0`.
- Os refs/histórico Git foram salvos em `../psicoia-git-refs-before-integration.bundle` (54 MB); `git bundle verify` passou e registrou sete refs. SHA-256: `0fef368c5132d1bba52e8b8b08905f47df510ae837999adce8cc6150276ec939`.
- Os dois arquivos estão no mesmo volume local, portanto não protegem contra falha desse disco. Não foi feito checkout nem integração.

## Decisão de escopo atual

- PT-BR permanece o idioma principal/padrão; inglês continua secundário.
- Alterações locais de mecanismo de locale, propagação de `output_language`, contratos/API e seleção de catálogos por idioma estão **pendentes de revisão separada**. Não expandir, integrar nem remover esse trabalho enquanto estiver pendente.
- A cópia upstream literal e as traduções documentais/de apresentação aprovadas podem avançar sem esperar por essa decisão. Prompts de avaliação e catálogo de habilidades continuam sujeitos a validação comportamental/recuperação própria.

## Estado e limites

- Além dos caminhos upstream, a árvore local contém 74 arquivos adicionais nesta fotografia (excluídos caches e arquivos de editor); isso inclui o novo teste local de identidade. Não se deve inferir que estejam commitados ou publicados.
- Nenhuma integração entre `original`, `origin/main` e `master` foi feita neste registro. A auditoria atual não criou commit, branch de publicação, push ou PR; os 17 commits da branch preexistente `integration/psicoia` continuam locais.
- A classificação dos 104 arquivos diferentes permanece **parcial**: o inventário cobre os grupos, mas não representa aprovação linha a linha. Não há caminhos upstream ausentes na comparação atual. Nenhuma diferença funcional está autorizada pela política de cópia literal. Arquivos de prompts, dados, perfis, catálogos e documentação exigem revisão apropriada à sua natureza.
- O nome do projeto de destino é `psicoia`. A atribuição acadêmica, referências, identificadores técnicos e proveniência do PsychAgent upstream devem ser preservados; diferenças de nome não provam autoria ou licença.
- A localização aprovada para conteúdo novo é PT-BR principal e inglês secundário. Não se declara que a localização do repositório esteja completa.

## Próxima etapa segura

1. Atualizar o snapshot upstream (`git fetch upstream`) e registrar o novo SHA antes de uma comparação futura.
2. Gerar uma lista reproduzível dos caminhos alterados/adicionados/removidos e classificar cada mudança com evidência.
3. Revisar licença e proveniência antes de preparar a integração.
4. Integrar em uma branch de trabalho baseada na base acordada, sem rebase entre históricos sem ancestral comum e sem force push.
5. Registrar testes executados e falhas preexistentes; revisar o diff final antes de qualquer publicação.
