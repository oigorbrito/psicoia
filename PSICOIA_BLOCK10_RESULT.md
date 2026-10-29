# PsicoIA Bloco 10 — fechamento funcional do backend

**Estado: PARTIAL.** Worktree recuperada em `D:/projetos/psicoia-reconciliation`; branch de trabalho `reconciliation/psicoia-block10-candidate`; base `c43242e6027b0395ab0fe1d05d4ac2be8505dc63`. Nenhum commit anterior foi reescrito e a `master`/seus arquivos não rastreados foram preservados. Commit final registrado ao concluir este relatório.

## Entrega e resultado

- Recuperado o registro de worktree obsoleto após verificar que o diretório-alvo não existia; `git worktree prune` removeu somente os registros `psicoia-reconciliation` e `psicoia-integration` cujos caminhos estavam ausentes. A branch `reconciliation/psicoia-block08` e seus commits foram preservados. A árvore recuperada inicialmente estava limpa e continha `PSICOIA_BLOCK08_RESULT.md`, testes e aplicação web.
- Adicionados `tests/backend_e2e.py` e `docs/PSICOIA_BLOCK10_API_CONTRACT.md`. A implementação web existente no candidato já continha as 16 rotas funcionais e seus serviços; não foi necessário copiar código comportamental da `master` para executar os fluxos locais selecionados.
- **PASS local:** autenticação, autorização por usuário, CRUD e transições de ciclo do curso, persistência SQL e sobrevivência a restart; execução dos contratos de 16 rotas via HTTP loopback com dados sintéticos. A rota de mensagens usa provedor OpenAI-compatible sintético local. Validações negativas verificaram rollback em erro de geração.
- **BLOCKED:** geração clínica e recuperação de skills com serviços/modelos reais. A configuração atual depende de chaves/endpoints externos; nenhuma chave real, modelo pago ou dado clínico foi usado. O substituto sintético e catálogo vazio não autorizam PASS para o fluxo real de modelo/embeddings.
- **NOT_RUN:** comparação diferencial de saída/latência contra serviço upstream executável; ambos os ambientes comparáveis (modelo e embeddings) não estavam disponíveis. Métrica de desempenho e memória não publicada por não haver workload diferencial válido. Não foi declarada equivalência.

## Rotas, testes e alterações da master

O inventário das 20 entradas de `app.routes` (16 de produto + 4 de documentação FastAPI), contratos, autenticação, persistência, erros e relação funcional está em [`docs/PSICOIA_BLOCK10_API_CONTRACT.md`](docs/PSICOIA_BLOCK10_API_CONTRACT.md).

A master disponível tem alterações não rastreadas de backend/frontend relacionadas a `output_language`. Não foram incorporadas neste bloco: o caminho atravessa schemas, serviços, engine, geradores/prompts e UI; mexer só no contrato HTTP criaria funcionalidade incompleta, e mudanças de prompt/retrieval exigem validação específica. Nenhuma dessas diferenças foi tratada como equivalência.

Defeito reproduzido/corrigido no backend de produção: **nenhum**. O teste de regressão de falha do provedor confirmou o comportamento implementado (502 e rollback), não um defeito. A captura silenciosa de falha no pós-processamento de fechamento permanece comportamento existente: a sessão fecha sem artefatos de modelo; exige decisão de produto antes de alterar.

## Comandos reproduzíveis

```bash
# Ambiente isolado criado fora da árvore de trabalho
python -m venv D:/temp/psicoia-block10-venv
D:/temp/psicoia-block10-venv/Scripts/python.exe -m pip install -r src/web/requirements.txt

# Na raiz do candidato
D:/temp/psicoia-block10-venv/Scripts/python.exe tests/backend_e2e.py
python -m pytest -q
python scripts/harness.py
node --test src/web/tests/*.test.js
```

Resultados nesta árvore: `backend_e2e.py` aprovado (rotas HTTP, SQLite/auth e restart; provedor sintético); `pytest` **17 passed**; harness exit 0 com `PASS` para presença de testes e `GAP` de licença (não é auditoria); testes Node executados separadamente. `requirements.txt` resolveu `openai>=1.0.0` para 3.41.0 no venv; compatibilidade com provedor real não foi validada. O teste de ponta a ponta usa servidor e banco locais temporários, e não usa dados clínicos.

**Próximas pendências:** validar com endpoint/modelo e embeddings autorizados, preencher catálogo sintético para medir retrieval sem dados clínicos, revisar a adaptação `output_language` separadamente e decidir se falha de resumo deve impedir fechamento. Portanto, este bloco não está CLOSED.
