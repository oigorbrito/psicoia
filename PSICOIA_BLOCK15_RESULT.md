# PsicoIA Block 15 — resultado da localização

**PT-BR — Resultado: PARTIAL.** `CLOSED_LOCALIZATION_SOFTWARE` não foi declarado. `CLINICAL_CONTENT_PENDING` permanece: os catálogos de habilidades e descrições de abordagem/etapa incluem conteúdo clínico ou potencialmente comportamental; a cobertura é incompleta, a revisão clínica não está documentada e a autorização de tradução não pôde ser confirmada na evidência local.

**EN — Outcome: PARTIAL.** `CLOSED_LOCALIZATION_SOFTWARE` is not declared. `CLINICAL_CONTENT_PENDING` remains: skill catalogs and approach/stage descriptions contain clinical or potentially behavior-sensitive content; coverage is incomplete, clinical review is undocumented, and translation authorization could not be verified from local evidence.

## Escopo, branch e preservação

- Worktree: `D:/projetos/psicoia-reconciliation`.
- Branch local: `reconciliation/psicoia-block15-localization-closure`, criada a partir de `8504a74ffd1783808d9c39e3ad1f76d8ecf1b3f9` (`reconciliation/psicoia-block14-localization`).
- Commit funcional deste bloco: `9cd264379671af9783f2b52394abbfb9ed4c1d74`.
- O commit final do relatório será o HEAD final; seu SHA é registrado na resposta de fechamento. Nenhum push, PR, merge, publicação ou alteração de `main` foi feito.
- Os três relatórios Block 13 que já estavam não rastreados permaneceram fora do staging e sem alteração: `reports/block13/retrieval_analysis.json`, `reports/block13/retrieval_phi4-mini_3.8b.json` e `reports/block13/retrieval_qwen3.5_4b.json`.
- O conteúdo/código da worktree separada `D:/projetos/psicoia` não foi alterado. A verificação final de worktrees será relatada no fechamento.

## Proveniência, licença e classificação dos catálogos

- `docs/ROADMAP.pt-BR.md` registra que a licença/proveniência do snapshot upstream permanece sem resolução. A inspeção local de `upstream/main` (`469f45ef468b968b3fccd1936d7e6a0a574e4c5c`) não encontrou `LICENSE`, `COPYING`, `NOTICE` ou `LICENSES/`. `evidence-repo-template/LICENSE-SELECT.md` é um lembrete de template, não uma licença do projeto. Isso é uma lacuna local e não uma determinação jurídica; não foi obtida confirmação externa de autoridade para traduzir conteúdo upstream.
- Os sidecars de catálogo já existentes remontam, no histórico local, ao commit `b3a87159a71d0573c72e61049bf275bcd51d277d`. `PSICOIA_BLOCK11_RESULT.md` descreve a cópia dos arquivos então existentes da branch local, mas não apresenta validação profissional/clínica nem uma fonte verificável da tradução. Foram preservados sem edição neste bloco.
- Embora chamados `meta_skills`, `skill_name` e `skill_description` descrevem estratégias/skills selecionadas e consumidas pelo pipeline; os catálogos micro também contêm `when_to_use` e `trigger`. Esses textos podem afetar o comportamento de geração. Não foi possível separar com segurança uma camada de metadados puramente operacional para tradução. Portanto, nenhum novo conteúdo de catálogo, prompt clínico, instrumento, benchmark ou skill foi traduzido.
- Os campos de API `/schools` e `/stages` incluem descrições e rótulos chineses em `src/web/backend/domain.py`. Permaneceram intactos por serem descrições clínicas/de abordagem ou parte do contexto comportamental. A interface traduz os rótulos conhecidos por IDs/keys estáveis; consumidores diretos da API ainda podem receber os textos de origem.

## Cobertura dos catálogos

Há 30 arquivos-fonte `.json` (cinco abordagens × três estágios × `meta_skills`/`micro_skills`) e 5.158 registros. As contagens abaixo são de arquivos e registros com sidecar locale, não percentuais de qualidade.

| Locale | Sidecars presentes | Registros localizados | Ausentes |
|---|---:|---:|---:|
| PT-BR | 16/30 | 1.233/5.158 | 14 arquivos; 3.925 registros sem sidecar |
| English | 8/30 | 141/5.158 | 22 arquivos; 5.017 registros sem sidecar |

Arquivos ausentes e número de registros-fonte correspondentes:

- **PT-BR:** `bt/stage2/micro_skills.json` (443); `cbt/stage1/micro_skills.json` (504), `cbt/stage2/meta_skills.json` (54) e `cbt/stage2/micro_skills.json` (609), `cbt/stage3/micro_skills.json` (259); `het/stage1/meta_skills.json` (42) e `het/stage1/micro_skills.json` (285), `het/stage2/meta_skills.json` (81) e `het/stage2/micro_skills.json` (409); `pdt/stage1/meta_skills.json` (28) e `pdt/stage1/micro_skills.json` (281), `pdt/stage2/meta_skills.json` (167) e `pdt/stage2/micro_skills.json` (670), `pdt/stage3/micro_skills.json` (93).
- **English:** `bt/stage1/meta_skills.json` (58) e `bt/stage1/micro_skills.json` (390), `bt/stage2/meta_skills.json` (95) e `bt/stage2/micro_skills.json` (443); `cbt/stage1/meta_skills.json` (31) e `cbt/stage1/micro_skills.json` (504), `cbt/stage2/meta_skills.json` (54) e `cbt/stage2/micro_skills.json` (609), `cbt/stage3/micro_skills.json` (259); `het/stage1/meta_skills.json` (42) e `het/stage1/micro_skills.json` (285), `het/stage2/meta_skills.json` (81) e `het/stage2/micro_skills.json` (409); `pdt/stage1/meta_skills.json` (28) e `pdt/stage1/micro_skills.json` (281), `pdt/stage2/meta_skills.json` (167) e `pdt/stage2/micro_skills.json` (670), `pdt/stage3/micro_skills.json` (93); `pmt/stage1/meta_skills.json` (12) e `pmt/stage1/micro_skills.json` (80), `pmt/stage2/meta_skills.json` (56) e `pmt/stage2/micro_skills.json` (370).

A checagem dos 30 arquivos-fonte não encontrou placeholders dos padrões `{{...}}`, `{%...%}`, `${...}` ou `<...>`. Os testes existentes verificam os contratos estruturais dos sidecars presentes (IDs, campos fixos e relações); isso não valida tradução, qualidade clínica, recuperação, embeddings ou equivalência. Não se criaram sidecars parciais/drafts.

## Auditoria CJK e comportamento explícito

A inspeção de texto CJK alcançou `src/web/src`, `src/web/backend`, `prompts/public`, `prompts/client`, `src/sample`, `src/eval`, `src/rft`, `scripts` e configurações/entrypoints operacionais. O conteúdo encontrado foi classificado, não traduzido indiscriminadamente:

- A interface contém chaves chinesas usadas como chaves de lookup do dicionário. Chaves sem tradução agora recebem um prefixo explícito de texto de origem em vez de serem apresentadas sem contexto.
- O painel de foco pode receber o foco chinês legado/default. O texto original continua visível, acompanhado de aviso de que contém chinês e não foi traduzido nem validado.
- Respostas do assistente ou mensagens de sistema que contenham Han são mantidas literalmente e identificadas como conteúdo no idioma de origem; não são silenciosamente descartadas nem apresentadas como PT-BR/inglês validado. Rótulos CJK de etapa/abordagem desconhecidos também recebem indicação de não traduzidos.
- A interface mostra aviso persistente de localização parcial, catálogo clínico incompleto e ausência de validação clínica/linguística do modelo. O backend registra por abordagem/estágio quando um catálogo localizado não existe e o carregador escolhe o catálogo no idioma de origem quando disponível. O fallback e os dados obrigatórios foram preservados; não houve supressão de conteúdo.
- Permanecem intencionalmente em chinês os prompts protegidos, contexto clínico, descrições de domínio/API, skills, conteúdo de avaliação e alguns valores/aliases legados. Os IDs, nomes de campos, rotas, enums e dados persistidos não foram traduzidos.

## Alterações deste bloco

1. `src/web/src/App.jsx`: aviso PT-BR/inglês de localização parcial e dos limites de catálogo/idioma do modelo.
2. `src/web/src/locale.js`, `src/web/src/i18n.jsx`: detecção de caracteres Han e fallback explícito para texto CJK sem chave localizada.
3. `src/web/src/components/chat/ChatMessages.jsx`, `src/web/src/components/layout/RightPanel.jsx`: avisos junto a conteúdo de foco/mensagem no idioma de origem, mantendo o conteúdo original visível.
4. `src/web/src/components/common/schoolText.js`, `src/web/src/components/common/stageText.js`: identificação de nomes/rótulos desconhecidos ainda no idioma de origem.
5. `src/sample/skill_manager.py`: aviso de log para cobertura localizada ausente, preservando a seleção/fallback já existente.
6. Testes para os rótulos CJK e aviso de lacuna do carregador.

Nenhuma rota, campo, enum, status HTTP, identificador, contrato de persistência, catálogo ou prompt foi alterado neste bloco. O idioma selecionado continua usando os valores existentes de `output_language` (`Português (Brasil)` / `English`).

### Arquivos alterados

- `src/sample/skill_manager.py`
- `src/web/src/App.jsx`
- `src/web/src/components/chat/ChatMessages.jsx`
- `src/web/src/components/common/schoolText.js`
- `src/web/src/components/common/stageText.js`
- `src/web/src/components/layout/RightPanel.jsx`
- `src/web/src/i18n.jsx`
- `src/web/src/locale.js`
- `src/web/tests/statusText.test.js`
- `tests/test_skill_catalog_locale_loading.py`
- `PSICOIA_BLOCK15_RESULT.md`

## Verificações

| Estado | Comando/atividade | Resultado e limites |
|---|---|---|
| PASS | `PYTHONPATH="src;$(cygpath -w /d/temp/psicoia-block14-venv/Lib/site-packages)" python -m pytest -q` | 53 testes passaram; um `PendingDeprecationWarning` do Starlette sobre `python_multipart`. A execução simples `python -m pytest -q` sem o `PYTHONPATH` falhou na coleta porque `sample` não estava no caminho de importação; a execução com o caminho usado pelo projeto passou. |
| PASS | `cd src/web && npm test` | 6 testes Node passaram. |
| PASS | `cd src/web && npm run build` | Build Vite concluído. |
| PASS | `D:/temp/psicoia-block14-venv/Scripts/python.exe tests/backend_e2e.py` | 16 rotas de negócio por HTTP loopback; autenticação/SQLite persistiram após reinicialização; validação, propriedade, ciclo de vida e rollback foram exercitados. O provedor e os catálogos eram sintéticos/vazios. |
| PASS | `python D:/temp/psicoia-block15-browser-validation.py` | Chromium real verificou alternância/persistência de locale, cadastro/login e erro de autenticação, criação de percurso, rótulos de estágio, valores existentes de `output_language`, aviso de foco chinês preservado e aviso junto a resposta chinesa sintética; viewport móvel de 390 px. O script é um arquivo temporário fora do repositório. Sem modelo real ou dados clínicos reais; o foco mostrado veio do contexto default já versionado e a resposta CJK de teste foi sintética. |
| PASS | `python -m src.sample.main --help`, `python -m src.eval.main --help`, `python -m src.rft.main --help` | Os três entrypoints retornaram ajuda; nomes técnicos/opções permaneceram preservados. |
| PASS | `python -m compileall -q src/web/backend src/sample src/eval src/rft`; `bash -n run_backend.sh run_frontend.sh`; `git diff --check` | Sem erros. Git apenas avisou sobre conversão de finais de linha LF/CRLF. |
| GAP | `python scripts/validate_skill_catalog_locales.py --locale pt-BR` e `--locale en` | Ambos terminam com código 1 por arquivos ausentes (14 PT-BR, 22 English); as contagens estão acima. As versões `--allow-missing` terminam sem outros erros, mas não satisfazem cobertura total. |
| GAP / UNKNOWN_EXTERNAL | `python scripts/harness.py` | GAP para arquivo de licença reconhecido; UNKNOWN_EXTERNAL para configurações GitHub/plataforma e implantação. O harness informa que verifica evidência local limitada, não executa testes nem verifica controles hospedados; não é auditoria. |
| NOT_RUN | Revisão de tradução por profissionais, autorização/licenciamento externo, validação clínica, qualidade com modelos reais, acessibilidade/navegadores além dos fluxos exercitados e implantação | Não executados; não há evidência para reivindicar equivalência, segurança, qualidade linguística do modelo ou prontidão de produção. |

## Estado e próximos passos

A localização operacional já implementada permanece em vigor; este bloco adiciona sinalização explícita de lacunas e não altera conteúdo clínico. A condição para declarar `CLOSED_LOCALIZATION_SOFTWARE` não foi atendida devido à cobertura dos catálogos e às superfícies protegidas ainda no idioma de origem. Manter `CLINICAL_CONTENT_PENDING`. Reabrir o trabalho de catálogo somente após verificar autoridade/proveniência e obter autorização/revisão apropriadas; preservar IDs/campos e validar separadamente recuperação e comportamento. Não declarar equivalência clínica, segurança ou qualidade de modelo a partir destes testes sintéticos.
