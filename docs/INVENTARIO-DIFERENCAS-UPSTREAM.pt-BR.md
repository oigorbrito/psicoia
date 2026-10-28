# Inventário inicial das diferenças locais

Este inventário compara a árvore de trabalho local com os **1.393 caminhos** do commit upstream `469f45ef468b968b3fccd1936d7e6a0a574e4c5c`. A comparação usa os caminhos UTF-8 sem quoting do Git e igualdade byte a byte.

## Resultado corrigido

- Idênticos: **1.292**.
- Diferentes: **101**.
- Ausentes: **0**.

**Correção de auditoria:** a primeira contagem deste trabalho usou a saída com quoting padrão do Git e interpretou cinco caminhos não ASCII como ausentes. A comparação foi repetida com quoting desativado; esses arquivos existem localmente. Os números acima substituem os números anteriores.

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
