# Bloco 10 — inventário do contrato HTTP

Base: `reconciliation/psicoia-block10-candidate` derivada de `c43242e6027b0395ab0fe1d05d4ac2be8505dc63`. A enumeração vem de `src/web/main.py`, `src/web/backend/routes/{courses,visits}.py` e `src/web/backend/schemas.py`. Há 16 rotas de produto e 4 rotas de documentação OpenAPI (20 entradas em `app.routes`).

`Bearer` significa token persistido retornado por `/auth/register` ou `/auth/login`. Cursos e visitas sempre verificam propriedade pelo usuário autenticado. Erros listados são os observados/levantados na implementação; respostas inesperadas de infraestrutura podem produzir 5xx.

| # | Método e caminho | Entrada → saída | Auth | Dependências, persistência/efeitos, erros principais | Fluxo / relação com PsicoIA |
|---|---|---|---|---|---|
| 1 | `GET /health` | sem body → `status`, baseline/modelo/idioma configurados | não | Instancia backend/configuração; não consulta DB. Falha de configuração/provider de embedding pode impedir inicialização/health. | Diagnóstico de execução, não capacidade terapêutica. |
| 2 | `POST /auth/register` | `{username,password}` → `{token,user}` | não | SQLModel/SQLite; cria usuário e token. Usuário repetido: 400. | Identidade necessária para acessar cursos e visitas. |
| 3 | `POST /auth/login` | `{username,password}` → `{token,user}` | não | Consulta usuário, compara hash, persiste token. Credencial inválida: 401. Token não expira no modelo atual. | Entrada no fluxo do produto. |
| 4 | `GET /schools` | sem body → lista `SchoolInfo` | não | Catálogo estático em memória; sem escrita. | Escolha de modalidade terapêutica. |
| 5 | `GET /stages` | sem body → lista `StageInfo` | não | Catálogo estático em memória; sem escrita. | Etapas mostradas no ciclo de atendimento. |
| 6 | `GET /courses` | query opcional `school_id,status` → `CoursePreview[]` | Bearer | SQLModel; filtra pelo usuário e filtros informados. | Lista e recuperação de cursos. |
| 7 | `POST /courses` | `CreateCourseRequest` (modalidade, título/objetivos/notas opcionais, `auto_start_first_visit`) → curso detalhado e visita opcional | Bearer | SQLModel; cria curso/metas; auto-start chama serviço de visitas e backend de geração. Modalidade inexistente: 404; conflito de persistência: 409. | Criação do caso e, opcionalmente, primeira sessão. |
| 8 | `GET /courses/{course_id}` | path ID → `CourseDetail` | Bearer | SQLModel; leitura do curso, metas, visitas e estatísticas. Ausente: 404; outro dono: 403. | Recupera plano e estado agregado. |
| 9 | `PATCH /courses/{course_id}` | campos parciais de `UpdateCourseRequest` → `CourseDetail` | Bearer | SQLModel; atualiza curso e substitui metas quando `goals` é fornecido. Ausente: 404; outro dono: 403; contagem planejada abaixo de 1: 422. | Atualização persistente do plano. |
| 10 | `POST /courses/{course_id}/complete` | `{summary?}` → `CourseDetail` | Bearer | SQLModel; só completa sem visita aberta; em aberto: 409. Ausente: 404; outro dono: 403. | Fechamento do percurso. |
| 11 | `POST /courses/{course_id}/archive` | sem body → `CourseDetail` | Bearer | SQLModel; só arquiva curso concluído; estado incompatível: 409. | Arquivamento/limpeza do curso concluído. |
| 12 | `GET /courses/{course_id}/visits` | path ID → `VisitPreview[]` | Bearer | SQLModel; valida propriedade do curso. Ausente: 404; outro dono: 403. | Histórico de sessões. |
| 13 | `POST /courses/{course_id}/visits` | `{opening_note?}` → `VisitState` | Bearer | SQLModel/contexto da visita e callback de geração; abertura usa resposta de fallback em falha de geração. Curso não ativo ou sessão anterior aberta: 409; geração sem texto/fallback: 502. | Inicia sessão ligada ao curso. |
| 14 | `GET /visits/{visit_id}` | path ID → `VisitState` com mensagens/contexto | Bearer | SQLModel; valida propriedade via curso. Ausente: 404; outro dono: 403. | Recupera conversa e contexto persistidos. |
| 15 | `POST /visits/{visit_id}/messages` | `{text}` não vazio → `{visit,course_meta}` | Bearer | Persiste mensagem e chama backend/modelo; falha ou resposta vazia: 502 com rollback; sessão fechada: 409; outro dono: 403; texto vazio: 422. Resposta com marcador de término pode acionar fechamento automático. | Turno de diálogo da sessão. |
| 16 | `POST /visits/{visit_id}/close` | `{summary?}` → `{visit_id,status,ended_at,summary}` | Bearer | SQLModel/contexto e callback de pós-processamento. Pós-processamento com falha é capturado e a sessão ainda fecha; summary informado é preservado. Já fechada: 409; outro dono: 403. | Fecha e persiste sessão/contexto; enriquecimento por modelo não é garantido. |
| 17 | `GET /openapi.json` | sem body → documento OpenAPI | não | Gerado pelo FastAPI; sem persistência. | Descoberta de contratos. |
| 18 | `GET /docs` | sem body → UI Swagger | não | Documentação FastAPI; sem persistência. | Exploração manual de API. |
| 19 | `GET /docs/oauth2-redirect` | query de OAuth → documento/redirect Swagger | não | Rota auxiliar FastAPI; sem persistência. | Suporte da UI Swagger; não é autenticação da aplicação. |
| 20 | `GET /redoc` | sem body → UI ReDoc | não | Documentação FastAPI; sem persistência. | Exploração de contratos. |

## Fluxos agrupados e evidência

- **Identidade → curso → atualização → conclusão → arquivamento:** executado via HTTP de loopback e SQLite real; dados sobreviveram ao restart. Contratos negativos de token, duplicação de usuário, ownership e estado foram exercitados.
- **Curso → sessão → mensagem → fechamento:** executado via HTTP e SQLite reais, usando somente um servidor OpenAI-compatible sintético em loopback; falha de geração retornou 502 e a mensagem do usuário foi revertida. Isto demonstra wiring, persistência e tratamento do contrato, não integração com provedor real, qualidade de geração ou equivalência clínica.
- **Dependência real de modelo/embeddings:** não executada; os arquivos de runtime apontam para serviços fora do loopback, e não foram utilizadas chaves. O teste substituto usa catálogo vazio; não valida recuperação real.

O contrato de saída e os efeitos são os schemas/serviços da implementação nesta árvore. O commit candidato mantém o contrato upstream existente. A adaptação de `output_language` observada nos arquivos não rastreados da `master` não foi copiada: depende de mudanças de prompts/retrieval e requer autorização/validação comportamental específica; o teste correspondente na `master` não prova o wiring nem equivalência. Nenhuma alegação de equivalência diferencial é feita.
