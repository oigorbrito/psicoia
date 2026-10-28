# Registro de migração do upstream

Este registro documenta observações locais para comparar o projeto `psicoia` com o upstream PsychAgent. A migração acordada é uma cópia literal do código, sem melhorias ou mudanças funcionais; a marca visível pode mudar para PsicoIA apenas em prosa de apresentação, e conteúdo aprovado pode ser traduzido para PT-BR principal e inglês secundário. Consulte a [política de migração e tradução](MIGRATION-POLICY.pt-BR.md). Este registro não declara equivalência, tradução completa, proveniência/licença aprovada ou prontidão de integração.

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

Esta contagem é apenas uma fotografia da comparação por caminho e conteúdo. As diferenças ainda não foram classificadas. Pela política acordada, somente tradução aprovada e alteração de marca em prosa de apresentação são permitidas; qualquer mudança funcional ou de identificador técnico é um desvio bloqueador, não uma adaptação aceita. A contagem também não valida arquivos locais adicionais, conteúdo, licenças, direitos de redistribuição ou qualidade das traduções.

## Salvaguarda local antes da integração

- A árvore de trabalho tinha 113 MB e 1.389 caminhos não rastreados na fotografia inicial deste passo.
- Foi criado fora do repositório `../psicoia-worktree-before-integration.tar.gz` (52 MB), excluindo `.git`; o teste `tar -tzf` passou. SHA-256: `bf5ea3b95581ded2e29ff1a97243a23d63759f7a65c0086d097f6fc18b597bc0`.
- Os refs/histórico Git foram salvos em `../psicoia-git-refs-before-integration.bundle` (54 MB); `git bundle verify` passou e registrou sete refs. SHA-256: `0fef368c5132d1bba52e8b8b08905f47df510ae837999adce8cc6150276ec939`.
- Os dois arquivos estão no mesmo volume local, portanto não protegem contra falha desse disco. Na fotografia da etapa de salvaguarda ainda não havia checkout nem integração.

## Decisão de escopo atual

- PT-BR é o idioma-alvo principal e inglês continua secundário; a interface e os padrões do código upstream ainda não foram localizados neste candidato.
- Alterações locais de mecanismo de locale, propagação de `output_language`, contratos/API e seleção de catálogos por idioma estão **pendentes de revisão separada**. Não expandir, integrar nem remover esse trabalho enquanto estiver pendente.
- A cópia upstream literal e as traduções documentais/de apresentação aprovadas podem avançar sem esperar por essa decisão. Prompts de avaliação e catálogo de habilidades continuam sujeitos a validação comportamental/recuperação própria.

## Candidato de integração atual

- Foi criada a branch local `integration/psicoia`, em worktree separada `../psicoia-integration`, baseada em `origin/main`.
- O merge local de `original` foi concluído no commit `af5cc72` (`Integrate PsychAgent upstream and evidence template`); o único conflito de árvore foi `README.md`, resolvido com a versão local de apresentação PsicoIA.
- A comparação por blob do commit de integração confirma que **1.392 dos 1.393 arquivos upstream estão idênticos** ao commit `original`; `README.md` é a única exceção inicial de apresentação/documentação. Diferenças de EOL na cópia de trabalho do Windows não foram confundidas com mudanças de blob.
- No snapshot do candidato `9e547ed`, a comparação por blob encontrou **1.384 idênticos, 9 diferentes e 0 ausentes** entre os 1.393 caminhos upstream. Os nove são `.gitignore` e oito READMEs (raiz, legado chinês, assets, perfis, configs, prompts, src e src/web); os demais arquivos upstream, inclusive código/runtime, permanecem byte-a-byte idênticos. `.gitignore` remove apenas as regras que ocultavam `docs/` e `tests/` locais.
- A camada de locale/API/output_language, catálogos traduzidos e testes associados permanece fora do candidato por estar pendente. O commit `10a251f` adicionou governança, pares de documentação PT-BR/inglês aprovados, harness e testes de documentação/harness.
- Os commits de integração/documentação/auditoria `af5cc72`, `10a251f`, `5d06503`, `b39e662`, `e896ba1` e `9e547ed` existem somente localmente e ainda não foram enviados ao remoto. A árvore de origem e `master` permanecem intactos.

## Estado e limites

- Além dos caminhos upstream, a árvore fonte contém 73 arquivos locais adicionais nesta fotografia (excluídos caches e arquivos de editor); a lista e classificação inicial estão no inventário. Não se deve inferir que estejam commitados ou publicados.
- Os 101 diffs estão listados e classificados por grupo; a revisão semântica dos oito READMEs e dos 33 prompts, a validação por benchmark e o aceite individual permanecem **pendentes**. Não há caminhos upstream ausentes. Nenhuma diferença funcional está autorizada pela política de cópia literal. Arquivos de prompts, dados, perfis e catálogos exigem revisão apropriada à sua natureza.
- O nome do projeto de destino é `psicoia`. A atribuição acadêmica, referências, identificadores técnicos e proveniência do PsychAgent upstream devem ser preservados; diferenças de nome não provam autoria ou licença.
- A localização aprovada para conteúdo novo é PT-BR principal e inglês secundário. Não se declara que a localização do repositório esteja completa.

## Próxima etapa segura

1. Obter decisão documentada sobre licença/proveniência antes de qualquer publicação; o harness ainda reporta `GAP`.
2. Revisar semanticamente os READMEs e prompts pendentes, incluindo tags/defaults de Jinja; só considerar avaliação comparativa de prompts após autorização e definição de conjunto fixo.
3. Classificar individualmente os 73 arquivos adicionais; manter os dois catálogos `.partial`, testes de contagem e alterações de locale/API/retrieval separados até validação/autorização.
4. Atualizar o SHA upstream antes de qualquer comparação futura e registrar diferenças novas.
5. Reexecutar testes apropriados, registrar limitações e revisar o diff final; não fazer push sem revisão explícita.
