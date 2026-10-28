# Piloto: fechamento e continuidade entre sessões

Este pacote contém fixtures sintéticos para calibrar a rubrica de `../../docs/SESSION-CLOSURE-CONTINUITY-EVALUATION.pt-BR.md`. É um **piloto de desenvolvimento**, não um benchmark cego, validação clínica, teste de produção ou evidência de que algum prompt melhorou.

## Arquivos

- `pilot-cases.jsonl`: 44 contextos sintéticos em PT-BR; estes são os únicos dados que uma futura execução de prompt deverá receber.
- `pilot-labels.jsonl`: ação esperada, fatos de ancoragem, itens que não podem ser afirmados e dimensões provisórias para revisão humana; nunca os forneça ao modelo durante a avaliação.
- `validate_pilot.py`: valida JSONL, campos obrigatórios, IDs e correspondência entre casos e rótulos, usando apenas a biblioteca padrão do Python.

As dimensões de cobertura são `focus_state` (`explored`, `open`, `ambivalent`), `ending_signal` (`none`, `natural`, `explicit`) e `history_state` (`available`, `first_session`, `unavailable`). Elas são rótulos provisórios: `explored` significa que o foco desta sessão foi suficientemente abordado, não que o problema clínico foi resolvido. Os 44 casos variam ainda tarefas realizadas ou não, primeira sessão, histórico indisponível, mudança de assunto, progresso contestado, planos acordados/recusados e pedidos de encerramento. Não incluem casos de crise; esses exigem um protocolo de segurança revisado antes de criar fixtures.

## Uso e limites

Os casos e rótulos são sintéticos e provisórios, escritos para iniciar a revisão da rubrica. Exigem revisão humana independente, inclusive para confirmar que o encerramento esperado e o foco a levar adiante são apropriados. Não use este piloto para ajustar e reportar desempenho final: o conjunto é conhecido e não tem separação cega.

O pacote não é carregado pelo runtime, não altera prompts upstream e não faz chamadas a modelos. A versão de teste cego deve ser criada separadamente, congelada antes de qualquer comparação e dimensionada com base na diferença mínima relevante e na variabilidade do piloto.
