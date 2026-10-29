# Bloco 13 — benchmark de recuperação v1

O conjunto `retrieval_eval_v1.json` é uma fixture sintética, não clínica e criada especificamente para este bloco. As consultas e os rótulos não reutilizam os exemplos dos Blocos 11/12. Os 12 documentos por idioma são versões paralelas de 12 tarefas domésticas, de hobby, viagem, culinária e escritório.

`criteria_v1.json` fixa os critérios antes da execução dos modelos. Cada idioma contém 12 consultas de teste e 4 consultas de calibração; a calibração só pode escolher o limiar de abertura de conjunto. Os resultados principais usam exclusivamente o conjunto de teste. As três primeiras consultas de teste (uma EN e duas PT-BR) também formam a amostra de integração real de idioma alternado PT-BR → EN → PT-BR.

A relevância graduada usa 3 para alvo direto, 2 para cada alternativa aceitável em consulta ambígua e 1 para documento semanticamente próximo, mas secundário. Consulta sem resposta tem mapa de relevância vazio. Recall@k conta consultas respondíveis com pelo menos um documento relevante no top-k; MRR usa o primeiro grau positivo; nDCG@5 usa ganho `2^relevância - 1`. ICs de Wilson são por proporção binária; diferenças entre modelos usam bootstrap pareado por consulta e semente fixa. Os intervalos são descritivos devido ao tamanho pequeno.

O limite de latência (p95 de embedding de consulta ≤2 s), indexação (≤120 s para 12 skills/idioma), inicialização fria (≤120 s) e resposta integrada (≤180 s por turno observado) é um orçamento experimental para o hardware medido, não um SLO de produto nem uma meta clínica.

Comando de benchmark e hardware/configuração efetivos devem ser registrados em `PSICOIA_BLOCK13_RESULT.md`. Não faça download de modelos. O candidato especializado só é avaliado se já estiver instalado e puder servir o mesmo endpoint local; ausência de candidato não é convertida em PASS.
