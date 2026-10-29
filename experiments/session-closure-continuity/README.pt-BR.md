# Piloto: fechamento e continuidade entre sessões

Este pacote contém fixtures sintéticos para calibrar a rubrica de `../../docs/SESSION-CLOSURE-CONTINUITY-EVALUATION.pt-BR.md`. É um **piloto de desenvolvimento**, não um benchmark cego, validação clínica, teste de produção ou evidência de que algum prompt melhorou.

## Arquivos

- `pilot-cases.jsonl`: 88 contextos sintéticos em PT-BR; estes são os únicos dados que uma futura execução de prompt deverá receber.
- `pilot-labels.jsonl`: ação esperada, fatos de ancoragem, itens que não podem ser afirmados e dimensões provisórias para revisão humana; nunca os forneça ao modelo durante a avaliação.
- `validate_pilot.py`: valida JSONL, campos obrigatórios, IDs, consistência entre histórico/ação e diálogos duplicados; também informa cobertura marginal e cruzada, usando apenas a biblioteca padrão do Python.
- `build_review_forms.py`: cria dois formulários cegos de revisão, com ordem separada, usando apenas `pilot-cases.jsonl`.
- `review/templates/reviewer-a.csv` e `review/templates/reviewer-b.csv`: modelos em branco rastreados pelo Git; não incluem os rótulos provisórios.
- `prepare_review_assignments.py`: copia os modelos em branco para `review/responses/` sem sobrescrever respostas existentes; os arquivos de resposta são ignorados pelo Git.
- `review/REVIEW-GUIDE.pt-BR.md` (`.md`): codebook bilíngue e instruções para revisão independente dos rótulos dos casos.
- `validate_review_forms.py`: verifica se os modelos em branco correspondem ao texto atual dos casos, contêm os mesmos 88 casos e usam ordens diferentes.
- `compare_review_forms.py`: após a conclusão pelos dois avaliadores, calcula concordância bruta e kappa de Cohen descritivo para os rótulos categóricos; não lê o arquivo de rótulos provisórios.
- `build_adjudication_sheet.py`: após o preenchimento dos dois formulários, cria uma ficha separada e em branco para divergências categóricas.
- `test_review_workflow.py`: testa o cálculo de concordância, a consistência dos casos e a proteção contra sobrescrever avaliações concluídas.

As dimensões de cobertura são `focus_state` (`explored`, `open`, `ambivalent`), `ending_signal` (`none`, `natural`, `explicit`) e `history_state` (`available`, `first_session`, `unavailable`). Elas são rótulos provisórios: `explored` significa que o foco desta sessão foi suficientemente abordado, não que o problema clínico foi resolvido. Os 88 casos variam tarefas realizadas ou não, primeira sessão, histórico indisponível, mudança de assunto, progresso contestado, planos acordados/recusados e pedidos de encerramento. Não incluem casos de crise; esses exigem um protocolo de segurança revisado antes de criar fixtures.

## Uso e limites

Os casos e rótulos são sintéticos e provisórios, escritos para iniciar a revisão da rubrica. Exigem revisão humana independente, inclusive para confirmar que o encerramento esperado e o foco a levar adiante são apropriados. Não use este piloto para ajustar e reportar desempenho final: o conjunto é conhecido e não tem separação cega.

Forneça aos avaliadores externos somente o CSV que lhes foi atribuído em `review/responses/` e `review/REVIEW-GUIDE.pt-BR.md` (ou o guia em inglês). Mantenha `pilot-labels.jsonl` e o restante do repositório fora do alcance deles até a entrega das duas revisões. A regra de exclusão do Git apenas reduz o risco de commit acidental; não é controle de acesso nem armazenamento seguro.

Para criar e validar formulários em branco a partir da raiz do repositório:

```bash
python experiments/session-closure-continuity/build_review_forms.py
python experiments/session-closure-continuity/validate_review_forms.py
python experiments/session-closure-continuity/prepare_review_assignments.py
```

O gerador se recusa a sobrescrever modelos preenchidos, a menos que receba `--force`; o preparador de atribuições também se recusa a sobrescrever respostas existentes. Preencha as cópias em `review/responses/`. Depois que ambos concluírem os formulários independentes, execute:

```bash
python experiments/session-closure-continuity/compare_review_forms.py
```

As estatísticas de concordância são descritivas e não provam que algum avaliador está correto. Após o preenchimento dos dois formulários, gere uma ficha em branco para divergências categóricas com `python experiments/session-closure-continuity/build_adjudication_sheet.py`. A ferramenta não lê os rótulos provisórios; analise separadamente divergências nas justificativas em texto livre. Não use um limiar de kappa como regra automática de aprovação. O pacote não é carregado pelo runtime, não altera prompts upstream e não faz chamadas a modelos. A versão de teste cego deve ser criada separadamente, congelada antes de qualquer comparação e dimensionada com base na diferença mínima relevante e na variabilidade do piloto.
