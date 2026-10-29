# Resultado do Bloco 13 — identidade e localização

**Resultado: PARTIAL**

## Escopo, refs e limites

Trabalho realizado somente na worktree `D:/projetos/psicoia-reconciliation`, branch `reconciliation/psicoia-localization-closure`. HEAD inicial: `253a9d085c607b71e61dd09e32aca992f1e11e10`. Commit local de implementação: `355d74d` (`feat(web): localize PsicoIA interface for pt-BR and English`). Este relatório é o commit local imediatamente seguinte; o HEAD final exato consta no `git log` e no resumo de entrega. Não houve push, PR, merge, rebase destrutivo nem alteração em `main`.

A interface de demonstração foi localizada para PT-BR (padrão) e inglês (secundário), com preferência salva no navegador. A seleção usa o campo já existente `output_language` ao criar percurso/sessão, enviar mensagem e encerrar sessão. Essa implementação e a preferência local constituem uma exceção explícita, autorizada pela solicitação, à cópia literal; não foram introduzidos novos endpoints, campos, enums ou dependências.

## Arquivos e superfícies

- Marca e apresentação: `README.md`, `README.pt-BR.md`, `src/web/README.md`, `src/web/README.pt-BR.md`, `src/web/index.html` e mensagens operacionais em `run_backend.sh`/`run_frontend.sh`. PsicoIA é a identidade do destino. Referências a PsychAgent no artigo, checkpoint, pesquisa, links e proveniência foram mantidas.
- Interface: `src/web/src/i18n.jsx`, `src/web/src/locale.js`, `main.jsx`, `App.jsx`, `hooks/useMindCareApp.js`, componentes de navegação, autenticação, chat, timeline, modais e mensagens/status. Os nomes visíveis das abordagens usam rótulos localizados; IDs de abordagem/status permanecem inalterados.
- Testes: `src/web/tests/statusText.test.js` cobre rótulos PT-BR/EN, fallback de status, rótulos de abordagem e mapeamento da localidade para os valores preexistentes do enum de idioma.
- Estado e limites: `LOCALIZATION.md` e `LOCALIZATION.pt-BR.md` foram atualizados para descrever cobertura e lacunas atuais.

Permaneceram inalterados os contratos e nomes técnicos existentes, rotas/campos de API, enums, identificadores, variáveis de ambiente, caminhos de prompts/configuração, atribuição acadêmica, dados, catálogos, instrumentos/benchmarks, prompts operacionais/clínicos e alterações validadas dos Blocos 10–12 e da avaliação de recuperação do Bloco 13. Em particular, não foram modificados os arquivos E2E/fixtures imutáveis do Bloco 12 nem o relatório de resultado do benchmark de recuperação.

## Cobertura e lacunas reais

Cobertura localizada: navegação principal e móvel, autenticação, criação/conclusão de percursos, início/continuação/encerramento de sessão, estados vazios, rótulos/status, mensagens de interface, avisos informativos, seletor de idioma e textos de inicialização dos scripts. Há teste unitário nos dois idiomas e o build da web foi gerado com sucesso.

**A localização não está completa.** Permanecem, entre outros:

- rótulos de etapa e foco de sessão recebidos do backend, assim como mensagens/status não presentes no mapa de apresentação;
- strings de API recebidas diretamente que não tenham correspondência no mapa de tradução;
- conteúdo gerado pelo modelo: o idioma é solicitado pelo campo preexistente, mas a qualidade/obediência de respostas PT-BR e EN não foi verificada com modelo;
- conteúdo clínico, instrumentos, escalas, dados/benchmarks, prompts de geração/avaliação e catálogos. Esses materiais foram excluídos, não traduzidos incidentalmente; qualquer localização requer escopo, revisão de proveniência e validação próprios;
- revisão linguística independente e revisão profissional do conteúdo de saúde mental;
- fluxo visual interativo em navegador, alternância persistida com execução real, persistência/restart, acessibilidade e integração ponta a ponta da interface com backend/modelo.

## Verificações executadas

- `PYTHONPATH=src python -m pytest -q` — **47 passed**. A tentativa anterior sem `PYTHONPATH=src` não coletou um teste por não localizar o pacote `sample`; a execução configurada acima passou.
- `cd src/web && node --test tests/*.test.js` — **4 passed**.
- `cd src/web && npm run build` — **PASS**, Vite transformou 1.602 módulos.
- `python scripts/harness.py` — harness local executado: PASS para presença de instruções/testes; GAP para licença; UNKNOWN_EXTERNAL para controles externos. Não é auditoria nem executa testes.
- `python -m compileall -q src/web/backend`, `bash -n run_backend.sh run_frontend.sh` e `git diff --check` — **PASS**.
- `python tests/backend_e2e.py` — **não executado com sucesso**: o servidor de teste encerrou na inicialização por `ModuleNotFoundError: No module named 'sqlmodel'`; a limpeza temporária também encontrou log bloqueado no Windows. Nenhum pacote foi instalado nem download efetuado.

Não foram executados browser/E2E visual, integração com serviços pagos/chaves reais, geração real de modelo, avaliação clínica, validação ampla de catálogos/prompts ou testes de persistência/restart da UI. O teste de contrato de idioma existente está incluído na suíte Python, mas não substitui fluxo integrado.

## Worktrees e estado final

Os três arquivos não rastreados preexistentes foram preservados, sem inclusão no commit:

- `reports/block13/retrieval_analysis.json`
- `reports/block13/retrieval_phi4-mini_3.8b.json`
- `reports/block13/retrieval_qwen3.5_4b.json`

Também foram conferidos, sem alteração, `D:/projetos/psicoia` em `master` (`e13c895850dc074fd5618322c5e7c1cfda34a29c`) e `D:/projetos/psicoia-closure-experiment` em `experiment/session-closure-continuity` (`e087949ab4284b922be226828f6ebd494759222c`). Nenhum artefato de build foi adicionado ao Git. A entrega fica **PARTIAL**, pois há cobertura útil PT-BR/EN e verificações locais, mas a localização do backend/aplicação, validação visual e validação integrada não foram concluídas.
