# Política de migração e tradução

## Regra central

O PsicoIA é uma migração fiel do código-fonte PsychAgent upstream, não uma oportunidade de refatoração. A cópia do código deve permanecer literal: não adicionar melhorias, otimizações, correções, recursos, dependências, alterações de arquitetura, formatação ampla ou mudanças de comportamento durante a migração.

O nome canônico de apresentação do projeto de destino é **PsicoIA**; o slug do repositório é **`psicoia`**. Em conteúdo voltado a pessoas, substitua a marca PsychAgent por PsicoIA quando a referência for ao produto migrado. Preserve a atribuição e os nomes do artigo, autores, checkpoint/modelos publicados e projeto upstream quando a referência for à origem acadêmica.

## Alterações permitidas

1. Copiar os arquivos de código upstream sem modificações funcionais.
2. Localizar, em PT-BR (principal) e inglês (secundário), a interface, a documentação e a prosa operacional própria da PsicoIA no escopo explicitamente autorizado para este trabalho, preservando sentido, comportamento e contratos.
3. Atualizar o nome visível do produto para PsicoIA apenas em texto de apresentação, interface e documentação.
4. Adicionar recursos de tradução isolados quando necessários, sem alterar lógica; qualquer mecanismo novo requer aprovação explícita e testes. A ausência de `LICENSE` reportada pelo harness não impede, isoladamente, tarefas locais independentes e não concede direitos de adaptação ou redistribuição.
5. Alterar links de marca/documentação somente para apontar para recursos válidos do destino, preservando as referências upstream e citações acadêmicas.

## Alterações proibidas no escopo da migração

- Alterar lógica, fluxo de controle, comportamento, APIs, esquemas, assinaturas, dependências, algoritmos ou dados.
- Renomear módulos, arquivos, diretórios, classes, funções, variáveis, imports, rotas, flags, variáveis de ambiente, chaves serializadas ou identificadores de modelo por substituição global de nome.
- Corrigir bugs, modernizar, reorganizar, formatar ou otimizar código incidentalmente.
- Traduzir benchmarks, perfis, itens de instrumentos clínicos, resultados ou outros dados de pesquisa como parte da migração, salvo escopo separado com base aplicável de uso/adaptação, revisão de direitos e validação especializada adequada.
- Integrar traduções de prompts comportamentais ou textos usados em recuperação sem testes de regressão e avaliação dos efeitos funcionais. Preservar o original e não alegar equivalência comportamental sem evidência.

## Separação entre localização, validação e direitos

- A localização local autorizada de interface, documentação e prosa operacional própria da PsicoIA é distinta da tradução de material upstream. Uma autorização de tarefa para localizar conteúdo próprio não concede direitos sobre material upstream, de terceiros ou protegido.
- Traduções locais experimentais de material upstream exigem uma base aplicável para uso ou adaptação; não se presume permissão pela ausência de publicação, pela ausência de `LICENSE` ou pelo fato de a cópia permanecer local. Quando essa base não estiver estabelecida, mantenha o material sem tradução e registre a pendência. Não reavalie essa questão em tarefas posteriores que permaneçam no escopo de software próprio.
- Conteúdo de proveniência/direitos incertos não pode ser publicado ou redistribuído sem autorização suficiente. Esse gate de distribuição é separado dos critérios de aceitação funcional da localização e não bloqueia trabalho local independente.
- Avalie a localização técnica por completude linguística no escopo permitido, integridade de placeholders, compatibilidade de APIs, identidade PsicoIA, seleção de idioma e regressões funcionais. Não inclua licença ou proveniência na classificação `CLOSED`/`PARTIAL` dessa localização; acompanhe distribuição em gate próprio.
- Validação funcional de prompts/recuperação não substitui revisão clínica. Instrumentos clínicos, escalas padronizadas e demais materiais protegidos exigem revisão de direitos e validação especializada antes da integração.

Identificadores ou nomes técnicos que contenham `PsychAgent` permanecem inalterados se a substituição puder quebrar compatibilidade ou proveniência. Qualquer exceção que modifique código precisa de autorização explícita, justificativa separada, diff isolado e testes; não deve ser apresentada como cópia literal.

## Processo obrigatório

1. Fixe e registre o SHA da origem antes de copiar. Mantenha a branch `original` como referência upstream, sem editar seus arquivos.
2. Compare cada arquivo migrado com o SHA registrado. Todo diff deve pertencer a uma das categorias permitidas acima; diferenças funcionais são bloqueadoras até serem revertidas ou aprovadas separadamente.
3. Para cada texto chinês localizado, preserve placeholders, markup, estrutura, pontuação funcional e identificadores; mantenha versões PT-BR e inglês alinhadas quando o escopo exigir ambas.
4. Separe migração, branding e localização em commits/revisões distintos sempre que possível. Não misture uma alteração funcional aprovada no commit de cópia literal.
5. Execute validações relevantes e registre resultado real. Testes aprovados não provam igualdade total; o diff contra o SHA upstream é a evidência de preservação do código.
6. Informe arquivos não traduzidos, pendências, exceções e limitações. Não declare migração ou localização completa sem inventário completo.

## Relação com outras regras

Esta política concretiza a preferência de migração do usuário e complementa `AGENTS.md`, `docs/ROADMAP.pt-BR.md` e a skill `psicoia-migration-translation`. Em caso de conflito, não faça uma alteração irreversível: registre o conflito e peça esclarecimento.
