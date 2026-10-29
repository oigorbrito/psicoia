# PsicoIA Bloco 11 — geração local, idiomas e recuperação

**Estado: PARTIAL; não CLOSED.** Branch candidata `reconciliation/psicoia-block11-candidate`, sobre `95f6170ff58177bb61e52bef527125535c455816` (base anterior `c43242e6027b0395ab0fe1d05d4ac2be8505dc63`). Sem push, PR, publicação ou alteração em `main`. A worktree `D:/projetos/psicoia` e seus arquivos não rastreados foram preservados.

## Resultado funcional

- **PASS — execução local real:** Ollama executou `phi4-mini:3.8b` para geração via HTTP loopback. Vetores reais foram produzidos pela versão local de `llama-server` com `--embedding --pooling mean`, usando o GGUF já instalado e CPU. O Ollama `/v1/embeddings` retornava 501; o teste usou diretamente o `llama-server` existente, sem baixar modelos nem chamar serviços pagos.
- **PASS — PT-BR sintético:** em processo configurado com catálogo PT-BR, a requisição produziu resposta com marcadores PT-BR e o prompt final recebido pelo modelo continha o skill-alvo localizado, recuperado do catálogo sintético.
- **GAP — EN:** em processo configurado com catálogo EN, a chamada real gerou conteúdo em chinês apesar da instrução `Respond in English`. A resposta veio sem `</response>` e com `<think>` exposto no texto persistido. O skill-alvo também não apareceu no prompt final do conselheiro. O teste terminou com código 1 por esses dois critérios. A causa da seleção EN incorreta não foi isolada; a busca vetorial direta no fixture colocou o alvo em primeiro lugar, mas o pipeline completo não.
- **PASS — persistência:** duas respostas foram recuperadas do SQLite temporário após reiniciar o backend. Isto comprova persistência do texto, inclusive do texto EN malformado; não comprova correção do conteúdo.
- **PASS — falhas injetadas no proxy local:** falha de embeddings acionou fallback de geração local; falha de geração resultou em HTTP 502 e rollback da mensagem. São testes de falha controlados, não indisponibilidade observada em serviço externo.
- **GAP — localização/catálogos incompletos:** validador com `--allow-missing`: EN 8/30 catálogos e 141/5158 registros; PT-BR 16/30 e 1233/5158. O teste usou oito documentos CBT sintéticos por idioma, não o catálogo integral. Os 24 arquivos localizados copiados da `master` local correspondentes byte a byte foram comparados; isso não demonstra completude nem qualidade clínica.
- **NOT_RUN — troca de idioma por requisição dentro do mesmo processo:** para testar a seleção de catálogo existente, PT-BR e EN foram executados em processos separados, cada um com `runtime.output_language` correspondente. Não se demonstrou que uma instância carregada em um idioma troque o catálogo para requisições subsequentes de outro idioma.
- **NOT_RUN — comparação diferencial com upstream/candidato equivalente e baseline de performance/qualidade.** Não há ambientes comparáveis ou corpus de referência validado. Os resultados sintéticos não representam equivalência de recuperação, qualidade de aconselhamento ou validade clínica.

### Observações do teste local

Modelo: `phi4-mini:3.8b`, instalado antes do teste. O processo de chat estava descarregado antes da execução. O arquivo GGUF tinha 2.491.874.624 bytes; `/api/ps` observou 3.654.465.614 bytes carregados e 2.327.282.973 bytes de VRAM. O `llama-server` de embeddings iniciou em 11,2 s e retornou vetores de 16.384 dimensões. A saída de embeddings foi obtida por mean pooling de um modelo generativo geral, **não** por um modelo especializado/treinado para embeddings; portanto, é uma execução técnica de recuperação, não recomendação para uso operacional.

No fixture de oito itens, a similaridade cosseno bruta do alvo foi 0,902 (PT-BR; próximo 0,825) e 0,897 (EN; próximo 0,814). São uma consulta sintética por idioma, não métricas agregadas. A inicialização da API levou 25,7 s (PT-BR) e 22,9 s (EN); abrir a sessão levou 65,9 s e 39,5 s; enviar a mensagem levou 42,0 s e 41,5 s. Como o modelo de chat estava descarregado antes do teste, a abertura PT-BR inclui a carga fria; EN ocorreu com o modelo já aquecido. Portanto, essas durações não são uma comparação fria/quente controlada. Foram dez respostas de chat bem-sucedidas observadas por idioma: PT-BR 13.295 tokens de entrada/1.387 de saída; EN 14.038/1.407. Cada inicialização gerou embeddings para 8 registros em dois lotes (merge/retrieval), além de dois vetores de consulta. N=1 por idioma; não são p95 nem benchmark comparativo. Não houve medição de RAM do processo de embeddings.

## Testes e evidências

- `tests/backend_local_ollama_e2e.py` — execução real descrita acima; **código 1**, por GAP de idioma e contexto em EN. Fixtures sintéticos em `tests/fixtures/block11/`.
- `python -m pytest -q` — **33 passed** (Python global 3.12.10); `python -m pytest -q evidence-repo-template/tests/test_harness.py` — **4 passed**.
- `tests/backend_e2e.py` — **PASS**: 16 rotas HTTP com provedor sintético, SQLite/auth/restart e negativos; não é evidência de modelo real. `npm test` em `src/web` — **2 passed**. `npm run build` foi executado e falhou: `vite` ausente e `src/web/node_modules/vite` inexistente; dependências não foram baixadas.
- `python scripts/harness.py` — código 0; `PASS` apenas para presença de arquivos, `GAP` de licença e `UNKNOWN_EXTERNAL` para controles hospedados. Não é auditoria.
- `python scripts/validate_skill_catalog_locales.py --locale en --allow-missing` — 8/30; `--locale pt-BR --allow-missing` — 16/30. A validação EN estrita, sem `--allow-missing`, retornou erro pelos catálogos ausentes.
- `D:/temp/psicoia-block10-venv/Scripts/python.exe -m pip check` — sem dependências quebradas; `pytest` não está instalado nesse venv. O `pip check` global apontou conflito separado: `rpy 0.1.1` requer `openai<2`, mas esse Python global tem `openai 2.54.0`; a execução web usou o venv isolado.
- `py_compile` dos arquivos alterados e `git diff --check` — executados sem erro.

## Limites e próximos passos

A geração real e vetores locais existem, mas EN e recuperação ponta a ponta não passaram. A saída `<think>` e o erro de idioma são observações reproduzidas, não foram corrigidos: a política de migração proíbe correções funcionais sem autorização explícita. A tradução/alteração de prompts e a expansão de catálogos também exigem validação específica. Antes de qualquer `CLOSED`, autorizar e validar separadamente: tratamento de resposta incompleta/ocultação de `<think>`, consistência EN do prompt, troca de catálogo por idioma na mesma instância, recuperação EN com consulta reescrita, catálogos completos e avaliação comparável. Não declarar adequação clínica, equivalência nem prontidão operacional.
