# Inventário das diferenças locais — Block 08

Este inventário compara o snapshot local `master` (`e13c895850dc074fd5618322c5e7c1cfda34a29c`) com o upstream `469f45ef468b968b3fccd1936d7e6a0a574e4c5c`, em seus **1.393 caminhos**. A reconciliação de 2026-10-29 compara blobs Git e normaliza os arquivos de trabalho com os filtros Git (`core.autocrlf=true`); diferenças CRLF do checkout Windows não contam como mudanças de conteúdo.

## Resultado atual (reconciliação 2026-10-29)

- Idênticos: **1.289**.
- Diferentes: **104**.
- Ausentes: **0**.

Três diferenças de identidade/apresentação foram adicionadas após o registro histórico 1.292/101/0: texto de ajuda da CLI em `src/sample/main.py` e nome do pacote privado em `src/web/package.json` e `src/web/package-lock.json`. Nenhum contrato técnico foi renomeado. `prompts/eval/SCL_90/SCL_90.txt` mantém o mesmo blob Git upstream.

**Histórico:** a primeira contagem usou quoting padrão do Git e interpretou cinco caminhos não ASCII como ausentes; a correção de quoting produziu 1.292/101/0. Os números históricos foram substituídos pelo resultado atual acima.

**Progresso da revisão:** os diffs completos de 26 caminhos `src/web`, sete caminhos `src/sample`, um YAML de runtime, 25 módulos de avaliação e 33 templates de prompt foram examinados/classificados abaixo; alterações de comportamento e contrato foram mantidas fora do candidato. Foram aplicadas somente mudanças isoladas de apresentação/identidade, registradas no relatório Block 08. Para avaliação, AST mascarando strings não mostrou mudança estrutural; para prompts, sintaxe Jinja foi analisada e referências/variáveis comparadas. Benchmarks e revisão semântica de prompts continuam pendentes. Os exemplos/fences dos oito READMEs foram comparados com upstream; prosa continua pendente de revisão semântica. O `.gitignore` foi conferido; nenhuma classe ainda sem validação ganha autorização implícita.

## Arquivos locais adicionais

Além dos 1.393 caminhos upstream, a árvore `master` contém **74 arquivos locais adicionais** após excluir caches, `.vs/`, `.DS_Store`, `nul`, `node_modules`, `dist` e bytecode Python. Triagem por tipo:

| Tipo de arquivo local adicional | Qtde. | Avaliação inicial |
|---|---:|---|
| Catálogos localizados | 26 (17 PT-BR, 9 inglês) | Dados de recuperação; validação estrutural existe, qualidade/recuperação e caches por idioma precisam de avaliação |
| Testes | 13 | Cobertura local nova; testes de localização permanecem separados; expectativa estrutural corrigida para 24 catálogos completos, sem alteração de conteúdo |
| Documentação/readmes locais | 14 | Guias, apresentação e governança raiz; código de exemplos comparado, revisão semântica da prosa ainda pendente |
| Documentação de governança | 12 | Adaptação local do template; não é código upstream nem prova de conformidade |
| Scripts de localização/harness | 3 | Ferramentas locais novas; revisar como tooling separado |
| Estado e schema de política | 2 | Dados de controle local, não estado autoritativo de GitHub |
| Skills de agente | 2 | Instruções locais, sem efeito no runtime do produto |
| Recurso de locale web | 1 | Texto de interface; sua ligação à aplicação faz parte da implementação de locale pendente |
| `.gitattributes` | 1 | Configuração local do repositório |

## Manifesto das adições locais (74 paths)

A contagem da árvore `master` é mutuamente exclusiva por categoria. O snapshot inicial do candidato continha 33/73 adições. A reconciliação Block 08 acrescenta `.gitattributes` e `tests/test_project_identity.py`, totalizando **35/74** adições de `master`; permanecem fora 26 catálogos, 10 testes de localização e dois scripts de catálogos. Foram acrescentados ainda `pytest.ini`, `src/web/tests/test_domain.py` e `src/web/tests/statusText.test.js`. Consulte `PSICOIA_BLOCK08_RESULT.md` para os totais finais do candidato.

### Catálogos localizados (26; dados de recuperação — excluídos do candidato)

- `assets/skills/sect/bt/stage1/`: `meta_skills.pt-BR.json`, `micro_skills.pt-BR.json`.
- `assets/skills/sect/bt/stage2/`: `meta_skills.pt-BR.json`, `micro_skills.pt-BR.json.partial`.
- `assets/skills/sect/bt/stage3/`: `meta_skills.en.json`, `meta_skills.pt-BR.json`, `micro_skills.en.json`, `micro_skills.pt-BR.json`.
- `assets/skills/sect/cbt/stage1/`: `meta_skills.pt-BR.json`; `stage3/`: `meta_skills.en.json`, `meta_skills.pt-BR.json`.
- `assets/skills/sect/het/stage3/`: `meta_skills.en.json`, `meta_skills.pt-BR.json`, `micro_skills.en.json`, `micro_skills.pt-BR.json`.
- `assets/skills/sect/pdt/stage3/`: `meta_skills.en.json`, `meta_skills.pt-BR.json`, `micro_skills.en.json.partial`.
- `assets/skills/sect/pmt/stage1/`: `meta_skills.pt-BR.json`, `micro_skills.pt-BR.json`; `stage2/`: os mesmos dois tipos PT-BR; `stage3/`: `meta_skills.en.json`, `meta_skills.pt-BR.json`, `micro_skills.en.json`, `micro_skills.pt-BR.json`.

Os 24 arquivos completos `.json` passam na validação estrutural local; o comando de inglês reporta 8/30 catálogos e 141/5.158 registros, e PT-BR 16/30 e 1.233/5.158. Os dois `.partial` não são parseados nem contados por esses validadores. A expectativa do teste local de contagem foi corrigida para 24 arquivos completos; a suíte em `master` passou. Validação estrutural não prova qualidade linguística, proveniência, equivalência de retrieval ou validade dos caches por idioma.

### Testes locais adicionais em `master` (13)

- Incluídos no candidato: `tests/test_harness.py`, `tests/test_localized_documentation.py`, `tests/test_project_identity.py`. Os testes web Block 08 estão listados separadamente.
- Excluídos por dependerem de runtime, API, prompts ou dados de locale pendentes: `src/web/tests/i18n.test.js`; `tests/test_behavioral_therapy_prompt_localization.py`; `tests/test_client_simulator_localization.py`; `tests/test_dummy_backend_localization.py`; `tests/test_eval_retry_localization.py`; `tests/test_generate_skill_catalog_locales.py`; `tests/test_runner_localization.py`; `tests/test_skill_catalog_locale_loading.py`; `tests/test_skill_catalog_localization_validation.py`; `tests/test_web_output_language.py`.

### Documentação/localização e governança

Os 14 arquivos Markdown locais incluídos são: `AGENTS.md`, `CONTRIBUTING.md`, `LOCALIZATION.md`, `LOCALIZATION.pt-BR.md`, `README.pt-BR.md`, `SECURITY.md`, `assets/README.pt-BR.md`, `assets/profiles/README.pt-BR.md`, `assets/skills/README.md`, `assets/skills/README.pt-BR.md`, `configs/README.pt-BR.md`, `prompts/README.pt-BR.md`, `src/README.pt-BR.md`, `src/web/README.pt-BR.md`. A prosa de localização ainda requer revisão semântica; ver a auditoria de exemplos acima.

Os 12 documentos de governança incluídos são `docs/ARCHITECTURE.md`, `docs/HARNESS.md`, `docs/INVENTARIO-DIFERENCAS-UPSTREAM.pt-BR.md`, `docs/MATURITY.md`, `docs/MIGRACAO-UPSTREAM.pt-BR.md`, `docs/MIGRATION-POLICY.md`, `docs/MIGRATION-POLICY.pt-BR.md`, `docs/RELEASE.md`, `docs/ROADMAP.md`, `docs/ROADMAP.pt-BR.md`, `docs/SOURCES.md` e `docs/TESTING.md`. Também foram incluídos `policy/project-state.json`, `policy/project-state.schema.json` e as duas skills `.agents/skills/{localization-guardrails,psicoia-migration-translation}/SKILL.md`; são controles locais, não evidência autoritativa de estado externo.

### Ferramentas e alterações de runtime ainda fora do candidato

- `scripts/harness.py` foi incluído; `scripts/generate_skill_catalog_locales.py` e `scripts/validate_skill_catalog_locales.py` ficaram fora junto dos catálogos pendentes. O gerador chama Ollama e escreve/retoma arquivos `.partial`; não foi executado nesta revisão.
- `src/web/src/i18n.js` ficou fora por ser runtime locale; seus testes também ficaram fora.
- `.gitattributes` foi incluído no candidato para normalizar EOL com `* text=auto`; as demais regras comentadas do template Git não alteram o comportamento do produto.

Dois catálogos têm sufixo `.partial` e não devem ser tratados como entregas completas: `assets/skills/sect/bt/stage2/micro_skills.pt-BR.json.partial` e `assets/skills/sect/pdt/stage3/micro_skills.en.json.partial`. Não adicione esses arquivos em bloco sem revisão individual de conteúdo, proveniência e necessidade.

## Classificação inicial

A tabela abaixo é a classificação inicial por grupo; as revisões detalhadas subsequentes registram os diffs técnicos e a estrutura Jinja. “Pendente/bloqueador” significa que o diff não deve ser aceito como cópia literal até ser explicado, aprovado separadamente ou revertido. Classificação do tipo de mudança não equivale a aprovação semântica.

| Grupo | Qtde. | Classe primária | Decisão/limite |
|---|---:|---|---|
| Documentação Markdown em inglês | 8 | A — apresentação/documentação | Exemplos técnicos e links comparados; revisão semântica completa da prosa permanece pendente. |
| `.gitignore` | 1 | C — configuração do repositório destino | Manter regras locais de segredos, caches e artefatos; não é código upstream. |
| `configs/runtime/psychagent_sglang_local.yaml` | 1 | D — alteração de default | `output_language` muda de chinês para inglês; mantido fora do candidato. |
| Prompts/templates de runtime | 33 | D — conteúdo comportamental | Alterações de instrução e placeholders; sem avaliação comparativa, mantidos fora. |
| Implementações de avaliação (`src/eval/`) | 25 | D — instruções enviadas ao modelo | AST igual após mascarar strings, mas prompts de reparo mudaram; mantidas fora. |
| Geração/recuperação (`src/sample/`) | 7 | D — alteração funcional | Defaults, fallback e seleção/cache de habilidades; mantidos fora. |
| Web | 26 | 1 A, 17 B, 8 D | UI/locale intencional (B) separado de contrato/API e idioma de geração (D); nenhum runtime locale foi integrado. `index.html` recebe somente o título de marca, sem o `lang=pt-BR` incompatível com a UI ainda chinesa. |
| Metadados privados do frontend (`package.json`, lock) | 2 | A — identidade | Nome `psicoia-web`; `private: true` preservado. |
| Ajuda da CLI (`src/sample/main.py`) | 1 | A — identidade | Texto PsicoIA; `--mode psychagent` e comportamento preservados. |

Total: **104 arquivos** — 12 A, 17 B, 1 C e 74 D. A classificação identifica a natureza do diff; B e D não foram incorporadas sem revisão/validação específica.

## Checagem estrutural de código

Os 12 arquivos com diferença estrutural, após mascarar strings/bytes na AST, são `src/sample/backends/dummy_backend.py`, `src/sample/client/simulator.py`, `src/sample/core/prompt_manager.py`, `src/sample/prompt_manager.py`, `src/sample/runner.py`, `src/sample/skill_manager.py`, `src/web/backend/psychagent_engine.py`, `src/web/backend/routes/courses.py`, `src/web/backend/routes/visits.py`, `src/web/backend/schemas.py`, `src/web/backend/services/visit_service.py` e `src/web/main.py`. As funções/campos alterados envolvem defaults e fallbacks localizados, propagação de `output_language`, contrato Pydantic, prompts de geração e seleção/cache de catálogos; nenhum foi integrado como alteração funcional neste candidato.

Foi feita uma comparação AST dos **41 arquivos Python diferentes**, substituindo literais string/bytes por marcadores. Resultado: 29 mantêm a mesma estrutura AST e **12 diferem estruturalmente**. Os 25 arquivos `src/eval/` permanecem AST-equivalentes após mascarar literais, mas alteram instruções de reparo enviadas ao modelo. Em `src/sample/`, `core/schemas.py` e `main.py` são AST-equivalentes; seis arquivos diferem estruturalmente. Em `src/web/`, `backend/domain.py` e `backend/services/course_service.py` são AST-equivalentes; seis diferem estruturalmente. AST não prova equivalência comportamental e não foi aplicado a JavaScript/JSX ou templates.

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

## Revisão dos exemplos técnicos nos READMEs

Comparação de conteúdo dos blocos cercados entre upstream e documentação inglesa do candidato (normalizando apenas duplicatas dos READMEs upstream bilíngues): `README.md` (11/11 idênticos), `assets/profiles/README.md` (1/1), `configs/README.md` (1/1), `prompts/README.md` (2/2 após restaurar o exemplo `prompts/eval/<method_name>/<prompt_name>.txt`), além de `assets/README.md` e `src/README.md` sem blocos cercados. O exemplo `rft runtime` em `configs/README.md` foi restaurado com a mesma grafia do upstream. Em `src/web/README.md`, os comandos de iniciar backend/frontend e build/preview foram separados em blocos para não sugerir execução simultânea no mesmo terminal; os blocos técnicos correspondem ao upstream depois de consolidar duplicatas, exceto pelos itens abaixo.

- `cd PsychAgent_v0402` foi omitido por ser um nome antigo de diretório do projeto, não o diretório garantido do destino.
- `cd src/web` foi movido para a instrução em prosa “From `src/web`” / “No diretório `src/web`”.
- O bloco original com endpoints em três linhas foi substituído por um bloco preservando `http://localhost:8000` e texto com os endpoints frontend/health.
- `README_CN.md` foi deliberadamente convertido em ponte curta para os READMEs mantidos; seus 11 blocos originais não foram preservados nesse caminho. O conteúdo de apresentação e comandos é coberto pelos READMEs atuais, mas a equivalência semântica completa da prosa dos oito READMEs permanece pendente.

## Revisão detalhada do grupo web (26 arquivos upstream diferentes)

Comparação do conteúdo local original com `original:469f45e`; o candidato mantém os blobs upstream dos desvios funcionais e aplicou apenas mudanças isoladas de título em `src/web/index.html` e `src/web/main.py`. A classificação abaixo descreve o diff local, não uma autorização para incorporar o locale/runtime.

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

O arquivo local adicional `src/web/src/i18n.js` (fora dos 104 caminhos upstream) fornece o mapa inglês→PT-BR, mapeamento de duas mensagens de autenticação chinesas, armazenamento em `localStorage`, fallback de locale PT-BR e atualização de `document.lang`. Ele é parte da implementação funcional pendente, não uma tradução que possa ser copiada sem o restante do wiring. O candidato Block 08 contém testes web de domínio Python e helpers JavaScript puros; eles não validam mensagens de backend/API, persistência, seleção de locale ou qualidade de tradução.

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

Os 34 arquivos técnicos acima (26 web + 7 sample + 1 YAML) foram comparados por diff; nenhuma alteração de comportamento, contrato ou recuperação foi incorporada. Foram aplicadas apenas strings de identidade isoladas em CLI/títulos. Essa revisão classifica o tipo de alteração, mas não valida qualidade clínica/linguística ou equivalência comportamental. `.gitignore` foi conferido: mantém arquivos de governança/testes rastreáveis e acrescenta exclusões para `.vs/`, `.env*` (com exceções de exemplo), logs e `nul`. A revisão semântica completa dos oito READMEs, dos 25 módulos de avaliação e dos 33 prompts ainda está pendente.

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

## Próximos gates seguros

1. Revisar semanticamente a prosa dos READMEs localizados; links e blocos técnicos foram verificados, mas isso não comprova fidelidade da tradução.
2. Manter os 33 prompts e as instruções de reparo de avaliação fora do candidato até autorização de comparação comportamental em conjunto fixo e revisão humana. Preservar placeholders/valores de compatibilidade e investigar as diferenças registradas (`output_language`, defaults traduzidos e contagem `{{number}}`).
3. Manter fora do candidato os 26 catálogos localizados e a implementação de runtime de locale/retrieval; resolver a discrepância 23/24 sem editar o teste por conveniência, validar provenance, idioma e recuperação/cache antes de habilitar.
4. Revisar individualmente os 10 testes e os dois scripts de catálogo ligados a locale; `.gitattributes` já foi adotado no candidato para normalização de EOL.
5. Obter evidência de licença/proveniência antes de qualquer distribuição. Não escolher licença por conveniência.

Não descarte nem sobrescreva o trabalho pendente na árvore fonte. Toda inclusão adicional deve ser revisada contra `original` e registrada no manifesto.
