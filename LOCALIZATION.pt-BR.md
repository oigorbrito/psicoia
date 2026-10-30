# Política e estado da localização

## Objetivos de idioma

O português brasileiro (`pt-BR`) é o idioma principal; o inglês (`en`) é secundário. A interface web tem textos localizados para os fluxos principais e um seletor persistido no navegador, mas a cobertura continua parcial. O idioma selecionado usa o campo API existente `output_language`. Mensagens operacionais de erro/validação, metadados descritivos do OpenAPI e ajuda/saída das CLIs foram localizados sem alterar rotas, nomes de campos, enums, IDs persistidos ou formatos de resposta. As instruções de idioma da geração foram localizadas de forma limitada; orientações clínicas, conteúdo comportamental, prompts de avaliação e catálogos não foram traduzidos. Exceção à cópia literal autorizada expressamente nesta tarefa: localizar essas instruções de idioma e a apresentação/operação descritas em [PSICOIA_BLOCK14_LOCALIZATION_CLOSURE.md](PSICOIA_BLOCK14_LOCALIZATION_CLOSURE.md). Consulte também a [política de migração e tradução](docs/MIGRATION-POLICY.pt-BR.md).

## Limites seguros

- Localize prosa de apresentação aprovada sem alterar rotas, nomes de campos de requisição/resposta, enums, opções da CLI, variáveis de ambiente, nomes de arquivos técnicos ou chaves de dados. Exceções funcionais expressamente autorizadas devem ser pequenas, isoladas, documentadas e testadas.
- A camada web localiza rótulos de apresentação de etapa/abordagem por IDs estáveis. Mensagens operacionais da API são traduzidas sem alterar o formato das respostas; valores e descrições de domínio preservados para compatibilidade não são prova de interface integralmente localizada.
- Mantenha inalterados os aliases chineses de etapa e valores reconhecidos quando forem usados para ler conteúdo legado ou selecionar comportamento da aplicação.
- Trate o texto dos prompts como sensível ao comportamento. A autorização Block 14 cobre somente instruções de idioma para respostas e valores textuais gerados, preservando os demais conteúdos, delimitadores e chaves JSON. Não traduzir orientações clínicas, prompts de avaliação ou conteúdo de benchmark sem autorização e validação específicas.
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

## Retrato anterior da auditoria (Blocks 14–15)

Para a avaliação atualizada de gates do Block 16, consulte a seção final abaixo.

- Interface web: textos de navegação, autenticação, percursos, sessões, status e erros mapeados estão localizados; rótulos de etapa são exibidos por IDs estáveis. Valores de foco da sessão e strings desconhecidas preservam o conteúdo de origem. Chromium real percorreu seleção/persistência do idioma, cadastro, criação de percurso e envio de mensagem via API local sintética, incluindo verificação de `output_language` em PT-BR e inglês. A resposta do provedor era sintética; não houve avaliação de fluência/modelo.
- API/CLI: autenticação, erros operacionais e validação mantêm status/forma de resposta, com textos PT-BR; descrições de campos OpenAPI também estão em PT-BR. A ajuda dos entrypoints sample/eval/RFT e o título do OpenAPI apresentam PsicoIA sem renomear módulos, flags ou identificadores de compatibilidade.
- Prompts: instruções finais de idioma para respostas e textos gerados foram ajustadas em caminhos autorizados, sem traduzir os prompts clínicos de origem, recomendações, escalas ou prompts de avaliação.
- Documentação: guias do projeto e da aplicação web existem em inglês e PT-BR; o arquivo legado `README_CN.md` mantém seu caminho e aponta para os guias atuais. A atribuição acadêmica e as referências PsychAgent permanecem preservadas.
- Prompts de avaliação: os 60 arquivos em `prompts/eval/` contêm texto chinês. Eles são usados por métodos de pontuação; traduzi-los é uma alteração sensível ao comportamento e exige comparação de notas em um conjunto fixo de avaliação e verificação dos esquemas.
- Catálogos de habilidades: há arquivos localizados e o carregador por idioma usa os arquivos disponíveis, mas a cobertura permanece em 16/30 catálogos e 1.233/5.158 registros em PT-BR, e 8/30 catálogos e 141/5.158 registros em inglês. Catálogos ausentes usam fallback para a origem e são registrados em log. Os números indicam apenas cobertura estrutural, não qualidade da tradução nem equivalência da recuperação.
- O texto chinês nos caminhos de imagens em Markdown foi mantido porque são caminhos de arquivos; alterá-los sem renomear os recursos e atualizar as referências quebraria os links.

A localização permanece parcial no conjunto: conteúdo clínico protegido, os 60 prompts de avaliação e a maior parte dos registros de catálogo continuam fora do escopo. Os fluxos integrados usaram respostas sintéticas locais; não validam qualidade linguística de modelos, equivalência clínica, prontidão de produção ou segurança. Consulte os relatórios dos Blocks 14/15 e o [resultado do Block 16](PSICOIA_BLOCK16_RESULT.md) para evidências e limitações.

## Gates independentes do Block 16

- `IDENTITY_CANONICAL: PASS` — PsicoIA é a identidade do projeto/produto nas superfícies de apresentação controladas auditadas. PsychAgent permanece somente como atribuição de origem, nome de pesquisa/modelo ou identificador necessário à compatibilidade. Figuras/capturas originais permanecem inalteradas e são identificadas como artefatos upstream, não como imagens da interface PsicoIA.
- `SOFTWARE_LOCALIZATION: PASS` — superfícies auditadas não clínicas da web, CLI, erros/metadados da API, script de inicialização e documentação bilíngue estão localizadas sem alterar rotas, campos, enums, nomes técnicos de arquivos ou variáveis de ambiente. Conteúdo protegido/de origem ainda visível é explicitamente identificado, não apresentado como traduzido.
- `CATALOG_TRANSLATION: GAP` — PT-BR: 16/30 arquivos (1.233/5.158 registros); inglês: 8/30 arquivos (141/5.158 registros). O validador estrito ainda aponta catálogos ausentes; nenhum texto adicional de catálogo clínico/de pesquisa foi traduzido.
- `CLINICAL_VALIDATION: NOT_RUN` — não houve revisão profissional de equivalência clínica, segurança ou idioma do modelo.
- `REDISTRIBUTION_RIGHTS: UNKNOWN_EXTERNAL` — os direitos de redistribuição do repositório continuam sem verificação; não houve determinação jurídica nem confirmação externa de direitos.

Os gates são independentes. Não se implica fechamento geral da localização, aprovação clínica, prontidão para produção ou permissão de redistribuição.
