# Inventário inicial das diferenças locais

Este inventário compara a árvore de trabalho local com os **1.393 caminhos** do commit upstream `469f45ef468b968b3fccd1936d7e6a0a574e4c5c`. A comparação usa os caminhos UTF-8 sem quoting do Git e igualdade byte a byte.

## Resultado corrigido

- Idênticos: **1.292**.
- Diferentes: **101**.
- Ausentes: **0**.

**Correção de auditoria:** a primeira contagem deste trabalho usou a saída com quoting padrão do Git e interpretou cinco caminhos não ASCII como ausentes. A comparação foi repetida com quoting desativado; esses arquivos existem localmente. Os números acima substituem os números anteriores.

**Progresso da revisão:** os diffs completos de 26 caminhos `src/web`, sete caminhos `src/sample`, um YAML de runtime, 25 módulos de avaliação e 33 templates de prompt foram examinados/classificados abaixo; nenhum desses desvios técnicos/comportamentais foi levado ao candidato. Para avaliação, AST mascarando strings não mostrou mudança estrutural; para prompts, sintaxe Jinja foi analisada e referências/variáveis comparadas. Benchmarks e revisão semântica de prompts continuam pendentes. O `.gitignore` foi conferido. A revisão semântica dos oito READMEs também permanece pendente; nenhuma classe ainda sem validação ganha autorização implícita.

## Arquivos locais adicionais

Além dos 1.393 caminhos upstream, a árvore contém **73 arquivos locais adicionais** após excluir caches, `.vs/`, `.DS_Store`, `nul`, `node_modules`, `dist` e bytecode Python. Triagem por tipo:

| Tipo de arquivo local adicional | Qtde. | Avaliação inicial |
|---|---:|---|
| Catálogos localizados | 26 (17 PT-BR, 9 inglês) | Dados de recuperação; validação estrutural existe, qualidade/recuperação e caches por idioma precisam de avaliação |
| Testes | 12 | Cobertura local nova; manter separados da cópia upstream; um teste de contagem atualmente falha (23 esperado, 24 observado) |
| Documentação/readmes de localização | 14 | Texto local de apresentação; revisar e manter em PT-BR principal/inglês secundário |
| Documentação de governança | 12 | Adaptação local do template; não é código upstream nem prova de conformidade |
| Scripts de localização/harness | 3 | Ferramentas locais novas; revisar como tooling separado |
| Estado e schema de política | 2 | Dados de controle local, não estado autoritativo de GitHub |
| Skills de agente | 2 | Instruções locais, sem efeito no runtime do produto |
| Recurso de locale web | 1 | Texto de interface; sua ligação à aplicação faz parte da implementação de locale pendente |
| `.gitattributes` | 1 | Configuração local do repositório |

Dois catálogos têm sufixo `.partial` e não devem ser tratados como entregas completas: `assets/skills/sect/bt/stage2/micro_skills.pt-BR.json.partial` e `assets/skills/sect/pdt/stage3/micro_skills.en.json.partial`. Não adicione esses arquivos em bloco sem revisão individual de conteúdo, proveniência e necessidade.

## Classificação inicial

As classificações abaixo são por grupo de arquivos e representam triagem, não revisão semântica linha a linha. “Pendente/bloqueador” significa que o diff não deve ser aceito como cópia literal até ser explicado, aprovado separadamente ou revertido.

| Grupo | Qtde. | Classificação inicial | Próxima decisão |
|---|---:|---|---|
| Documentação Markdown em inglês (lista abaixo) | 8 | Texto/documentação alterados; potencialmente compatível com localização, mas falta revisão de equivalência e escopo | Revisar prosa, links, atribuição e diferenças além de tradução; manter fonte acadêmica fiel |
| `.gitignore` | 1 | Regra local de inclusão/ignoração; não é tradução nem código upstream | Manter somente como configuração do repositório de destino, com revisão de arquivos que passa a expor |
| `configs/runtime/psychagent_sglang_local.yaml` | 1 | `output_language` mudou de chinês para inglês; altera o default de execução | **Bloqueador de cópia literal**; reverter ou autorizar como mudança isolada de localização |
| Prompts/templates de runtime (lista abaixo) | 33 | Texto de instrução para modelos foi alterado/traduzido; conteúdo comportamental | **Pendente e sensível ao comportamento**; não substituir prompts de origem sem autorização e avaliação comparativa |
| Implementações de avaliação (`src/eval/`, lista abaixo) | 25 | Comentários/docstrings foram traduzidos; mensagens de reparo JSON enviadas ao modelo também mudaram | **Pendente**; preservar a lógica, revisar diferenças de instrução e validar efeito em avaliação antes de aceitar |
| Geração/recuperação (`src/sample/`, lista abaixo) | 7 | Há mudanças de output language, defaults/fallbacks e seleção/carregamento de catálogos por idioma | **Bloqueador de cópia literal/funcional**; exige decisão separada, testes e validação de recuperação; não classificar como mera tradução |
| Web (26 arquivos de código, lista abaixo) | 26 | Inclui texto de UI traduzido, wiring de locale e campos/propagação de idioma de resposta no backend/API | Separar recursos textuais de mudanças de contrato e comportamento; campos/API/output language são **bloqueadores** até autorização explícita |

A soma é 101 arquivos upstream diferentes. A classe de cada alteração ainda não foi verificada linha por linha; não se declara que qualquer grupo está aprovado ou semanticamente equivalente.

## Checagem estrutural de código

Foi feita uma comparação AST dos 40 arquivos Python diferentes, substituindo todos os literais string por um marcador antes da comparação. Resultado: os 25 arquivos `src/eval/` mantêm a mesma estrutura AST sob esse teste; isso **não** prova equivalência comportamental, pois as instruções de reparo enviadas ao modelo mudaram. Em `src/sample/`, somente `core/schemas.py` mantém a estrutura AST sob a normalização; nos outros seis arquivos há mudanças estruturais. Em `src/web/`, `backend/domain.py` e `backend/services/course_service.py` mantêm a estrutura AST após normalização; os outros seis arquivos Python web diferem estruturalmente. O teste AST não foi aplicado a JavaScript/JSX nem a templates e não é prova de ausência de alterações funcionais.

Conclusão operacional: há alterações de código além da troca de strings. Diferenças concretas identificadas:

- `src/web/backend/schemas.py` adiciona `OutputLanguage` e campos `output_language` às requisições; rotas, `psychagent_engine.py` e `visit_service.py` propagam o valor e alteram o idioma de textos gerados. Isso muda contratos e comportamento da API.
- `src/web/src/App.jsx`, componentes e `useMindCareApp.js` adicionam seleção/propagação do locale e escolha do idioma das respostas; `src/web/src/i18n.js` é um recurso local novo.
- `src/sample/core/prompt_manager.py`, `runner.py`, `client/simulator.py`, `dummy_backend.py` e `skill_manager.py` alteram idioma padrão, fallbacks, saída simulada e carregamento/cache de catálogos por idioma. O carregamento de habilidades pode afetar a recuperação.
- `configs/runtime/psychagent_sglang_local.yaml` muda o default `output_language` de chinês para inglês.
- 33 templates de prompt foram traduzidos/alterados; instruções de reparo em 25 módulos de avaliação também mudaram. Mesmo sem mudança estrutural Python, texto enviado ao modelo pode alterar respostas, avaliações e pontuações.

Essas mudanças não são cópia literal. Decisão atual do usuário: manter PT-BR como principal e deixar essa camada de implementação de idioma pendente de revisão separada. Até essa revisão, não expandir, integrar nem remover essas alterações locais; seguir com a classificação do restante, cópia de arquivos idênticos e documentação aprovada.


## Documentação alterada (8)

- `README.md`
- `README_CN.md`
- `assets/README.md`
- `assets/profiles/README.md`
- `configs/README.md`
- `prompts/README.md`
- `src/README.md`
- `src/web/README.md`

## Revisão detalhada do grupo web (26 arquivos upstream diferentes)

Comparação do conteúdo local original com `original:469f45e`; o candidato de integração mantém os blobs upstream desses arquivos. A classificação abaixo descreve o diff local, não uma autorização para incorporá-lo.

| Arquivo | Diferença observada | Classificação/decisão |
|---|---|---|
| `src/web/backend/domain.py` | Traduz para inglês nomes/descrições de etapas e abordagens; IDs (`assessment`, `cbt` etc.) permanecem iguais. | Texto apresentado pela API/UI; tradução isolada de locale pendente. |
| `src/web/backend/psychagent_engine.py` | Adiciona `output_language` às funções de resposta/artefatos; passa idioma a prompts/chamadas; acrescenta instruções de idioma e traduz valores fallback/sessão. | Mudança de assinatura, prompt e comportamento; bloqueador funcional. |
| `src/web/backend/routes/courses.py` | Encaminha `payload.output_language` à criação de curso. | Acoplado a novo campo de request/API; mudança funcional. |
| `src/web/backend/routes/visits.py` | Encaminha `payload.output_language` à abertura, envio de mensagem e encerramento. | Acoplado a novo campo de request/API; mudança funcional. |
| `src/web/backend/schemas.py` | Traduz descrições e acrescenta `OutputLanguage` mais campos opcionais `output_language` em requests de curso/sessão/mensagem/fechamento. | Expansão explícita do contrato OpenAPI/API; bloqueador até revisão específica. |
| `src/web/backend/services/course_service.py` | Traduz títulos padrão/fallback e detalhes de erros HTTP; fluxo de controle permanece igual no diff inspecionado. | Conteúdo de resposta exposto pela API, mas sem seleção de locale; não é só documentação. |
| `src/web/backend/services/visit_service.py` | Altera assinaturas/callbacks e propaga idioma; traduz prompts, mensagens persistidas, erros e defaults; aceita `Unknown` em `UNKNOWN_TEXT_VALUES`. | Mistura de contrato, valores persistidos e tratamento de dados; bloqueador funcional. |
| `src/web/main.py` | Acrescenta parâmetro opcional e propaga idioma aos callbacks do engine. | Mudança de fluxo/assinatura. |
| `src/web/index.html` | Altera `lang` para `pt-BR` e traduz o título para inglês. | Metadados de idioma e apresentação; `lang` estático precisa permanecer coerente com locale selecionado. |
| `src/web/src/App.jsx` | Cria estado de locale, expõe seletor e passa locale a componentes; traduz rótulos/estados. | Wiring e comportamento de UI, além de texto. |
| `src/web/src/components/chat/ChatInput.jsx` | Traduções, locale prop e textos de entrada/aviso. | UI localizada; assinatura de componente alterada. |
| `src/web/src/components/chat/ChatMessages.jsx` | Traduz estados vazios e passa locale. | UI localizada; assinatura de componente alterada. |
| `src/web/src/components/common/FeedbackBanner.jsx` | Traduz botão de fechar; locale prop. | UI localizada; assinatura de componente alterada. |
| `src/web/src/components/common/StageBadge.jsx` | Traduz etapa/fallback; locale prop. | UI localizada; assinatura de componente alterada. |
| `src/web/src/components/common/schoolText.js` | Substitui rótulos chineses por inglês e busca PT-BR via helper; adiciona argumento locale. | Texto apresentado e interface interna alterada; IDs de abordagem preservados. |
| `src/web/src/components/common/statusText.js` | Traduz status e formato de sessão; acrescenta argumentos locale. | Valores de apresentação e interfaces internas alterados; valores de status preservados. |
| `src/web/src/components/layout/HeaderBar.jsx` | Traduz rótulos e adiciona seletor de idioma que chama persistência de locale. | UI + comportamento de seleção/persistência; locale atravessa a árvore. |
| `src/web/src/components/layout/MobileBottomSheet.jsx` | Traduz ações/labels e acrescenta locale prop. | UI localizada; assinatura de componente alterada. |
| `src/web/src/components/layout/RightPanel.jsx` | Traduz estágios, objetivos e avisos; troca defaults de foco para inglês e acrescenta locale prop. | Conteúdo de UI inclui texto de saúde; revisar precisão e cobertura PT-BR. |
| `src/web/src/components/layout/Sidebar.jsx` | Traduz navegação, status, acessibilidade e estados vazios; acrescenta locale prop. | UI localizada; assinatura de componente alterada. |
| `src/web/src/components/layout/VisitTimeline.jsx` | Traduz linha do tempo, status e contagem; acrescenta locale prop. | UI localizada; assinatura de componente alterada. |
| `src/web/src/components/modals/AuthModal.jsx` | Traduz labels/feedback do modal; acrescenta locale prop. | UI localizada; mensagens de autenticação requerem revisão de boundary com backend. |
| `src/web/src/components/modals/CompleteCourseModal.jsx` | Traduz modal de conclusão; acrescenta locale prop. | UI localizada; assinatura de componente alterada. |
| `src/web/src/components/modals/CreateCourseModal.jsx` | Traduz modal/placeholders e muda título sugerido; acrescenta locale prop. | UI e valor inicial do formulário alterados; revisão de conteúdo. |
| `src/web/src/components/modals/SchoolModal.jsx` | Traduz seleção/aviso e acrescenta locale prop. | UI localizada; assinatura de componente alterada. |
| `src/web/src/hooks/useMindCareApp.js` | Traduz feedbacks e acrescenta `output_language` aos requests de criar/abrir/enviar/fechar; usa helper de tradução para alguns erros. | Mudança de API e comportamento; bloqueador. |

O arquivo local adicional `src/web/src/i18n.js` (fora dos 101 caminhos upstream) fornece o mapa inglês→PT-BR, mapeamento de duas mensagens de autenticação chinesas, armazenamento em `localStorage`, fallback de locale PT-BR e atualização de `document.lang`. Ele é parte da implementação funcional pendente, não uma tradução que possa ser copiada sem o restante do wiring. Não há testes web no candidato; mensagens de backend/API e persistência também não foram validadas por testes de locale.

## Revisão detalhada de geração/recuperação e configuração (8 arquivos upstream diferentes)

| Arquivo | Diferença observada | Classificação/decisão |
|---|---|---|
| `configs/runtime/psychagent_sglang_local.yaml` | Default `output_language` muda de `中文` para `English`. | Altera default operacional; bloquear na cópia literal. |
| `src/sample/backends/dummy_backend.py` | Muda idioma default e roteamento de respostas simuladas; acrescenta respostas PT-BR e remove detecção/ramo chinês. | Muda fixture/comportamento demonstrativo e geração sintética; requer autorização e testes por idioma. |
| `src/sample/client/simulator.py` | Traduz instruções e respostas, muda default e inclui marcadores PT-BR na inferência de humor/concern. | Prompt e lógica de simulação mudam; pode alterar dados/avaliações gerados. |
| `src/sample/core/prompt_manager.py` | Traduz fallbacks vazios; reescreve fallback de diálogo do cliente com instruções e seções EN/PT-BR; adapta nomes de terapia e sessão de abertura por idioma. | Conteúdo comportamental de prompt reestruturado; exige comparação fixa e revisão humana. |
| `src/sample/core/schemas.py` | Default de `output_language` muda de chinês para inglês, inclusive fallback de parse. | Muda default de configuração/execução. |
| `src/sample/prompt_manager.py` | Acrescenta substituição manual de `{{ output_language }}` quando Jinja indisponível. | Novo comportamento de fallback/template, não tradução. |
| `src/sample/runner.py` | Traduz foco de sessão, acrescenta catálogo PT-BR e helper de seleção; passa idioma a prompts; adiciona instruções de idioma aos prompts de resumo/perfil. | Muda planejamento, prompts e conteúdo produzido; comportamento sensível. Valores de estágio chineses permanecem. |
| `src/sample/skill_manager.py` | Seleciona catálogos/caches por idioma, cria digest SHA-256 de cache e usa fallback textual inglês; comments traduzidos. | Muda recuperação, seleção e invalidação de embeddings; requer auditoria de cache e avaliação de retrieval por idioma. |

Os 34 arquivos técnicos acima (26 web + 7 sample + 1 YAML) foram comparados por diff completo nesta etapa; nenhum foi incorporado ao candidato. Essa revisão classifica o tipo de alteração, mas não valida a qualidade clínica/linguística, compatibilidade do contrato ou equivalência comportamental. `.gitignore` foi conferido separadamente: a única mudança remove as regras `/docs/` e `/tests/` para permitir rastrear governança e testes locais. A revisão semântica completa dos oito READMEs, dos 25 módulos de avaliação e dos 33 prompts ainda está pendente.

## Revisão estrutural dos templates de prompt (33 arquivos)

Os diffs completos foram comparados; os templates foram analisados com Jinja em ambas as versões. Os 33 parsers Jinja foram aceitos pela análise sintática, mas isso não valida renderização com o contexto da aplicação, tradução, instruções, placeholders interpolados ou comportamento do modelo.

- O conteúdo chinês foi amplamente substituído por inglês; esta revisão não aprovou equivalência semântica, e não há conjunto PT-BR paralelo nesses 33 templates. Algumas instruções adicionam `output_language` para orientar a resposta gerada.
- A sequência textual exata de tags Jinja mudou em 19/33 arquivos. Parte das diferenças é espaçamento (`{{client_info}}` → `{{ client_info }}`), parte traduz labels/defaults dentro de expressões; não considerar sintaxe de placeholder “preservada literalmente” apenas porque Jinja aceita as duas formas.
- A análise de variáveis livres Jinja encontrou nomes novos `output_language` em sete templates, sem nome antigo removido. Há nove novas ocorrências dessa variável em oito templates; em `prompts/public/counselor_system.jinja2` ela já era usada em outra expressão. O candidato upstream não recebe esse valor para todos esses prompts, pois o wiring local de runtime permanece excluído.
- `prompts/psychagent/skill/select_skill/system.txt` tem três ocorrências a menos de `{{number}}` que o upstream; ainda restam outras ocorrências, então a variável não desaparece completamente, mas a redundância da quantidade exigida foi reduzida. Isso é uma diferença de instrução e merece revisão explícita.
- Os valores default dentro de `default(...)` mudaram do chinês para inglês (por exemplo `未知` → `Unknown`, `来访者` → `Client`, `无` → `None`); labels interpolados como `line('姓名', ...)` também foram traduzidos. Esses valores entram no prompt enviado ao modelo, não são apenas comentários.
- Uma varredura Unicode encontrou 604 caracteres Han residuais em 15 templates. A inspeção das linhas os identificou como valores de compatibilidade (etapas, status, tópicos, termos de modalidade) e exemplos de nomes de habilidades que precisam permanecer idênticos aos dados/catálogos existentes. Não os trate como prosa automaticamente traduzível.

## Templates de prompt alterados (33)



- `prompts/client/dialogue.jinja2`
- `prompts/psychagent/bt/counsel/system.jinja2`
- `prompts/psychagent/bt/profile/system.jinja2`
- `prompts/psychagent/bt/profile/user.jinja2`
- `prompts/psychagent/bt/summary/system.jinja2`
- `prompts/psychagent/bt/summary/user.jinja2`
- `prompts/psychagent/cbt/counsel/system.jinja2`
- `prompts/psychagent/cbt/profile/system.jinja2`
- `prompts/psychagent/cbt/profile/user.jinja2`
- `prompts/psychagent/cbt/summary/system.jinja2`
- `prompts/psychagent/cbt/summary/user.jinja2`
- `prompts/psychagent/het/counsel/system.jinja2`
- `prompts/psychagent/het/profile/system.jinja2`
- `prompts/psychagent/het/profile/user.jinja2`
- `prompts/psychagent/het/summary/system.jinja2`
- `prompts/psychagent/het/summary/user.jinja2`
- `prompts/psychagent/pdt/counsel/system.jinja2`
- `prompts/psychagent/pdt/profile/system.jinja2`
- `prompts/psychagent/pdt/profile/user.jinja2`
- `prompts/psychagent/pdt/summary/system.jinja2`
- `prompts/psychagent/pdt/summary/user.jinja2`
- `prompts/psychagent/pmt/counsel/system.jinja2`
- `prompts/psychagent/pmt/profile/system.jinja2`
- `prompts/psychagent/pmt/profile/user.jinja2`
- `prompts/psychagent/pmt/summary/system.jinja2`
- `prompts/psychagent/pmt/summary/user.jinja2`
- `prompts/psychagent/skill/rewrite/system.txt`
- `prompts/psychagent/skill/rewrite/user.txt`
- `prompts/psychagent/skill/select_skill/system.txt`
- `prompts/psychagent/skill/select_skill/user.txt`
- `prompts/public/counselor_system.jinja2`
- `prompts/public/public_recap.jinja2`
- `prompts/public/session_opening.jinja2`

## Revisão detalhada das implementações de avaliação (25 arquivos)

O diff completo foi comparado em todos os 25 caminhos desta classe. Uma segunda comparação AST independente, mascarando todos os literais string, encontrou **0 diferenças estruturais**; isso não prova equivalência dos textos enviados ao modelo. As alterações observadas são comentários/docstrings em inglês e instruções de reparo de JSON em inglês. Não identifiquei alteração de fluxo de controle, esquema Python ou cálculo nos diffs inspecionados.

As mensagens de reparo mantêm nos exemplos verificados o nome da chave `items`, as contagens exigidas, nomes dos campos e faixas numéricas (`score`), mas são prompts enviados ao modelo e podem afetar reparos, validação subsequente ou a decisão de nova tentativa. A tradução não tem benchmark comparativo nem revisão bilingue concluída; portanto, manter os arquivos upstream no candidato. Em `panas.py`, a aritmética explícita do escore e os rótulos de itens não mudaram; as mudanças são comentários/docstring e a instrução de reparo. Essa inspeção não autoriza tradução de itens de instrumentos clínicos, que continuam fora do escopo.

Arquivos com instruções de reparo de JSON modificadas: `src/eval/core/base.py`; os nove avaliadores de cliente (`bdi_ii.py`, `cct.py`, `ipo.py`, `panas.py`, `phq_9.py`, `scl_90.py`, `sfbt.py`, `srs.py`, `stai.py`); os avaliadores de aconselhamento `ctrs.py`, `custom_dim.py`, `dialogue_grounding.py`, `dialogue_planning.py`, `dialogue_redundancy.py`, `eft_tfs.py`, `htais.py`, `human_eval.py`, `human_vs_llm.py`, `miti.py`, `plan_consistency.py`, `psc.py`, `tes.py`, `wai.py`; e `src/eval/methods/rro.py`. `custom_dim.py`, entre outros, interpola contagens/nome de prompt nos textos; os valores interpolados permanecem referências técnicas.

## Implementações de avaliação alteradas (25)

- `src/eval/core/base.py`
- `src/eval/methods/client/bdi_ii.py`
- `src/eval/methods/client/cct.py`
- `src/eval/methods/client/ipo.py`
- `src/eval/methods/client/panas.py`
- `src/eval/methods/client/phq_9.py`
- `src/eval/methods/client/scl_90.py`
- `src/eval/methods/client/sfbt.py`
- `src/eval/methods/client/srs.py`
- `src/eval/methods/client/stai.py`
- `src/eval/methods/counselor/ctrs.py`
- `src/eval/methods/counselor/custom_dim.py`
- `src/eval/methods/counselor/dialogue_grounding.py`
- `src/eval/methods/counselor/dialogue_planning.py`
- `src/eval/methods/counselor/dialogue_redundancy.py`
- `src/eval/methods/counselor/eft_tfs.py`
- `src/eval/methods/counselor/htais.py`
- `src/eval/methods/counselor/human_eval.py`
- `src/eval/methods/counselor/human_vs_llm.py`
- `src/eval/methods/counselor/miti.py`
- `src/eval/methods/counselor/plan_consistency.py`
- `src/eval/methods/counselor/psc.py`
- `src/eval/methods/counselor/tes.py`
- `src/eval/methods/counselor/wai.py`
- `src/eval/methods/rro.py`

## Geração e recuperação alteradas (7)

- `src/sample/backends/dummy_backend.py`
- `src/sample/client/simulator.py`
- `src/sample/core/prompt_manager.py`
- `src/sample/core/schemas.py`
- `src/sample/prompt_manager.py`
- `src/sample/runner.py`
- `src/sample/skill_manager.py`

## Código web alterado (26)

- `src/web/backend/domain.py`
- `src/web/backend/psychagent_engine.py`
- `src/web/backend/routes/courses.py`
- `src/web/backend/routes/visits.py`
- `src/web/backend/schemas.py`
- `src/web/backend/services/course_service.py`
- `src/web/backend/services/visit_service.py`
- `src/web/main.py`
- `src/web/index.html`
- `src/web/src/App.jsx`
- `src/web/src/components/chat/ChatInput.jsx`
- `src/web/src/components/chat/ChatMessages.jsx`
- `src/web/src/components/common/FeedbackBanner.jsx`
- `src/web/src/components/common/StageBadge.jsx`
- `src/web/src/components/common/schoolText.js`
- `src/web/src/components/common/statusText.js`
- `src/web/src/components/layout/HeaderBar.jsx`
- `src/web/src/components/layout/MobileBottomSheet.jsx`
- `src/web/src/components/layout/RightPanel.jsx`
- `src/web/src/components/layout/Sidebar.jsx`
- `src/web/src/components/layout/VisitTimeline.jsx`
- `src/web/src/components/modals/AuthModal.jsx`
- `src/web/src/components/modals/CompleteCourseModal.jsx`
- `src/web/src/components/modals/CreateCourseModal.jsx`
- `src/web/src/components/modals/SchoolModal.jsx`
- `src/web/src/hooks/useMindCareApp.js`

## Outros arquivos alterados

- `configs/runtime/psychagent_sglang_local.yaml`
- `.gitignore`

## Próximo passo

Revisar os grupos bloqueadores em diffs menores e separar: (a) localização de UI/documentação aprovada; (b) alterações comportamentais ou contratos, que não entram na cópia literal sem autorização específica; (c) prompts e recuperação, que precisam de validação comportamental própria. Não reverter automaticamente: preserve primeiro a árvore local e decida cada classe com o usuário.
