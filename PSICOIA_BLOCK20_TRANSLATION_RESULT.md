# PsicoIA — Bloco 20: fluxo de abertura de sessão

**Estado: PARTIAL.** Foi caracterizado e testado um fluxo vertical sintético. Não foi integrada tradução nova: o prompt e os dados de etapa do fluxo selecionado são conteúdo upstream que permanece sem base específica documentada para adaptação. O resultado não atribui validação clínica ao conteúdo nem transforma o impedimento específico em bloqueio geral da localização.

## Base e commits

- Worktree: `D:/projetos/psicoia-reconciliation-block18`.
- Branch: `reconciliation/psicoia-block20-behavioral-translation`, criada em `7026ece574a187e115a74e212464050088696f92`; ancestralidade com `8ac3619` confirmada.
- HEAD final de implementação/testes: `e6af59b25e5291bb178eb1d884ebb4f49cca361f`.
- Commits funcionais de caracterização: `556b4ea` e `e6af59b`; preservam todos os commits anteriores.
- O SHA do commit final que contém este relatório é informado no fechamento, pois o próprio relatório não pode conter seu hash sem autorreferência.

## Fluxo e baseline congelado

Fluxo escolhido: criação de visita pela camada de serviço (`create_visit`) com callback sintético, contexto SQLite temporário e recuperação posterior do estado persistido.

- Entrada sintética: curso CBT, visita 1 de 3, nota `foco sintético`, idioma `Português (Brasil)`.
- Etapa selecionada: `assessment`; o contexto retornado inclui rótulo e descrição em chinês. A sessão de abertura não seleciona documentos RAG: IDs recuperados = `[]`.
- Campos que compõem o prompt: escola, chave de etapa, número da visita e total planejado. A seed da pessoa usuária já é PT-BR: `Esta é a sessão 1\nFoco da sessão: foco sintético`.
- Prompt original renderizado: SHA-256 UTF-8 `9d8348a80a1ceb04db4ee85e5060f0ae866f2a716111d253f399bcd686a9326d`; metadados de etapa: SHA-256 `a98e22dfc0d74da0c4f513609000969a8c4a68b74e59dfc0130eed0d20efaf2e`; marcadores Jinja não renderizados: 0.
- Callback determinístico retorna `{text, end}`: `Esta é uma resposta sintética em português brasileiro.`, `end=false`. O estado relido do SQLite preserva etapa, status `open`, dois registros de mensagem e o mesmo texto de resposta.
- Falha sintética do callback: a abertura usa o fallback PT-BR já existente e o estado resultante persiste.

A fixture `tests/fixtures/block20/session_opening_baseline.json` guarda hashes e invariantes, não uma cópia do prompt clínico. A resposta é sintética; não foi feita geração por modelo nem avaliação de qualidade linguística.

## Decisão de adaptação

A frase de contagem de sessão (`total_part`) e as instruções adjacentes em `src/web/backend/services/visit_service.py` também aparecem em `original:src/web/backend/services/visit_service.py`; o conteúdo CJK de etapa está em `original:src/web/backend/domain.py`. O fluxo de prompt contém instruções de aconselhamento/segurança e descrições de etapa. Não traduzi nem reescrevi esses segmentos: não há base de adaptação específica registrada para esse material, e a caracterização funcional não concede direitos nem valida conteúdo clínico. Essa é a limitação específica deste fluxo; não foi refeita a análise geral do Bloco 17.

A UI já traduz rótulos de etapa pelo ID estável. Foi acrescentado um teste com payload CJK sintético para comprovar a exibição PT-BR/EN por `stage.key`; não foi contado como tradução nova. A lógica de etapa, contexto, prompts de produção, contratos de API e identificadores persistidos não foram alterados.

## Regressão e verificação

- `python scripts/check_localization.py` — **45 passaram, 1 skip; 6 testes Node passaram**. O skip ocorre porque o Python padrão não tem `sqlmodel`; os testes de caracterização foram executados separadamente no ambiente web.
- `python -m pytest -q` — **56 passaram, 1 skip**; o módulo de caracterização opcional também foi executado com as dependências web.
- `python scripts/harness.py` — executado separadamente. O `GAP` de licença continua sendo apenas evidência do gate geral de distribuição, não critério funcional de localização.
- `PYTHONPATH='src;.;D:\temp\psicoia-block14-venv\Lib\site-packages' python -m pytest -q tests/test_block20_session_opening_characterization.py` — **3 passaram**. Foram observados avisos de depreciação já originados por Starlette/Pydantic e pelo código de data/serialização; não houve falha.
- Validadores de catálogo `--allow-missing`: PT-BR **16/30, 1.233/5.158**; EN **8/30, 141/5.158**. Nenhuma tradução/registo novo neste bloco.
- `git diff --check` passou. Não houve alteração de código de aplicação; por isso navegador/API ao vivo não foram necessários para validar uma mudança de runtime.

## Cobertura e próximo conjunto

| Idioma | Antes | Depois | Novos registros |
|---|---:|---:|---:|
| PT-BR | 16/30; 1.233/5.158 | 16/30; 1.233/5.158 | 0 |
| EN | 8/30; 141/5.158 | 8/30; 141/5.158 | 0 |

O fluxo de UI/seed já entrega texto PT-BR e a etapa é apresentada por ID estável, mas são localizações herdadas, não contribuição nova do Bloco 20. Próximo conjunto de prompt/contexto só é elegível quando houver base aplicável para adaptar o material upstream; então a fixture congelada permite comparação diferencial com o mesmo percurso. Itens de instrumento, critérios clínicos, descrições de intervenção e comportamento terapêutico permanecem fora desta integração e exigem revisão específica. Nenhum conteúdo foi apresentado como clinicamente validado.
