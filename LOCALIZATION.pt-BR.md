# Política e estado da localização

## Objetivos de idioma

O português brasileiro (`pt-BR`) é o idioma principal do conteúdo localizado; o inglês (`en`) é secundário. Na interface web, PT-BR é o padrão e a preferência já salva é respeitada. Na migração, o código upstream deve ser copiado literalmente: sem melhorias, correções ou mudanças funcionais. A marca visível pode mudar de PsychAgent para PsicoIA apenas em prosa de apresentação referente ao produto de destino. Identificadores, contratos serializados, atribuição acadêmica e referências ao upstream permanecem inalterados. Consulte a [política de migração e tradução](docs/MIGRATION-POLICY.pt-BR.md).

## Limites seguros

- Traduza prosa de interface/documentação aprovada para PT-BR e inglês sem alterar comportamento, rotas de API, nomes de campos de requisição/resposta, opções da CLI, variáveis de ambiente, nomes de arquivos ou chaves de dados. A cópia de código deve ser literal; melhorias e correções ficam fora do escopo.
- Quando um sistema upstream retornar uma string localizada ou legada que faça parte de uma resposta da API, traduza-a na camada de apresentação em vez de mudar silenciosamente o contrato do backend. A interface web faz isso para os dois detalhes chineses de erro de autenticação.
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

- Interface web: PT-BR é o padrão; inglês é compatível; os testes existentes de localização da interface passam. Os detalhes chineses de erro de autenticação são localizados apenas na exibição, preservando o texto da resposta do backend.
- Documentação: há guias do projeto e da aplicação web em inglês e PT-BR. O antigo caminho do README chinês foi mantido como ponte de compatibilidade para os guias mantidos.
- Prompts de avaliação: os 60 arquivos em `prompts/eval/` contêm texto chinês. Eles são usados por métodos de pontuação; traduzi-los é uma alteração sensível ao comportamento e exige comparação de notas em um conjunto fixo de avaliação e verificação dos esquemas.
- Catálogos de habilidades: a última validação estrutural local informa cobertura de 16/30 catálogos e 1.233/5.158 registros em PT-BR, e 8/30 catálogos e 141/5.158 registros em inglês. Esses números indicam apenas cobertura estrutural; não comprovam a qualidade da tradução nem a equivalência da recuperação.
- O texto chinês nos caminhos de imagens em Markdown foi mantido porque são caminhos de arquivos; alterá-los sem renomear os recursos e atualizar as referências quebraria os links.

Este retrato não significa que a localização do projeto esteja completa. Atualize os números após cada lançamento validado de catálogos ou prompts.
