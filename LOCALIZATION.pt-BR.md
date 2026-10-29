# Política e estado da localização

## Objetivos de idioma

O português brasileiro (`pt-BR`) é o idioma principal; o inglês (`en`) é secundário. A interface web dispõe agora de textos localizados para fluxos principais e de um seletor de idioma salvo no navegador; a cobertura não é completa. A opção de idioma também é enviada no campo API já existente `output_language` ao criar percursos/sessões, enviar mensagens e encerrar sessões. A migração preserva identificadores, contratos, dados, atribuição acadêmica e referências ao upstream; conteúdo clínico, prompts operacionais e catálogos não foram traduzidos neste trabalho. Exceção autorizada por esta tarefa à cópia literal: interface local de idioma e envio do idioma selecionado pelo campo já existente `output_language`; não foram adicionadas rotas, enums ou campos de API. Consulte a [política de migração e tradução](docs/MIGRATION-POLICY.pt-BR.md).

## Limites seguros

- Traduza prosa de interface/documentação aprovada para PT-BR e inglês sem alterar comportamento, rotas de API, nomes de campos de requisição/resposta, opções da CLI, variáveis de ambiente, nomes de arquivos ou chaves de dados. A cópia de código deve ser literal; melhorias e correções ficam fora do escopo.
- Quando um sistema upstream retornar uma string localizada ou legada que faça parte de uma resposta da API, traduza-a na camada de apresentação em vez de mudar silenciosamente o contrato do backend. A implementação local dessa tradução está pendente e não faz parte deste candidato de integração.
- Mantenha inalterados os aliases chineses de etapa e valores reconhecidos quando forem usados para ler conteúdo legado ou selecionar comportamento da aplicação.
- Trate o texto dos prompts como sensível ao comportamento. Um prompt de avaliação traduzido pode mudar as notas mesmo que o esquema JSON permaneça válido. Não substitua o prompt de origem antes de compará-lo com um benchmark e verificar o contrato de saída.
- Trate o texto das habilidades como entrada de recuperação. Catálogos localizados precisam de caches de embeddings específicos por idioma e avaliação da recuperação. Nunca reutilize embeddings do idioma de origem para texto traduzido.
- Não traduza exemplos de benchmark nem itens de instrumentos clínicos como parte de uma limpeza incidental. Essas alterações exigem escopo explícito, revisão de proveniência e validação.

## Comandos de validação

Na raiz do repositório:

```bash
cd src/web && node --test tests/*.test.js
python scripts/validate_skill_catalog_locales.py --locale en --allow-missing
python scripts/validate_skill_catalog_locales.py --locale pt-BR --allow-missing
```

Para gerar um build de produção do frontend, execute `cd src/web && npm run build` após instalar as dependências do frontend. A verificação de links deve cobrir todos os guias Markdown localizados. Mantenha equivalentes entre idiomas os exemplos de comandos, placeholders, chaves JSON e blocos de código.

## Retrato atual da auditoria

- Interface web: foram localizados os fluxos principais de navegação, autenticação, criação/conclusão de percursos, sessões, status e mensagens de interface. Os rótulos de idioma PT-BR/EN e a conversão para os valores preexistentes do enum `output_language` têm testes unitários. Rótulos de etapa e foco de sessão oriundos do backend permanecem no idioma de origem; mensagens/status fora do mapa também podem aparecer sem tradução. Não foi executado fluxo visual interativo com navegador.
- Documentação: guias do projeto e da aplicação web existem em inglês e PT-BR; os READMEs principais agora apresentam PsicoIA como destino e preservam PsychAgent para proveniência, artigo, modelo e pesquisa.
- Prompts de avaliação: os 60 arquivos em `prompts/eval/` contêm texto chinês. Eles são usados por métodos de pontuação; traduzi-los é uma alteração sensível ao comportamento e exige comparação de notas em um conjunto fixo de avaliação e verificação dos esquemas.
- Catálogos de habilidades: o trabalho local de tradução informa cobertura de 16/30 catálogos e 1.233/5.158 registros em PT-BR, e 8/30 catálogos e 141/5.158 registros em inglês. Esses catálogos traduzidos não foram incluídos neste candidato; os números indicam apenas cobertura estrutural e não comprovam qualidade da tradução nem equivalência da recuperação.
- O texto chinês nos caminhos de imagens em Markdown foi mantido porque são caminhos de arquivos; alterá-los sem renomear os recursos e atualizar as referências quebraria os links.

A localização permanece parcial. O backend ainda entrega strings chinesas de etapas, abordagens e contextos; dados, conteúdo clínico, prompts de avaliação/geração e catálogos permanecem fora do escopo autorizado aqui. A build e os testes unitários da web não substituem revisão linguística/profissional nem validação funcional integrada com modelos. Atualize este retrato somente após evidência correspondente.
