# Guia de revisão independente do piloto

## Objetivo e escopo

Use este guia para revisar **os rótulos dos casos** do piloto sintético de fechamento e continuidade. Não avalie uma resposta de modelo e não altere prompts. A revisão verifica se a ação esperada, o estado do foco, o sinal de encerramento e o estado do histórico estão sustentados pelo caso; também verifica os fatos de ancoragem, o que pode ser levado adiante e as afirmações que devem ser evitadas.

Os casos não são clínicos nem representam validação clínica. Não há casos de crise neste piloto.

## Cegamento e independência

1. Cada avaliador recebe somente seu CSV (`reviewer-a.csv` ou `reviewer-b.csv`) e este guia. Não compartilhe `pilot-labels.jsonl`, o restante do repositório nem as respostas do outro avaliador antes da entrega de ambos os formulários.
2. Preencha os casos sem discutir decisões com o outro avaliador. A ordem dos casos difere entre os formulários.
3. Use `observacoes` para registrar ambiguidade, interpretação alternativa ou qualquer inconsistência; ainda assim, escolha a categoria mais defensável nos campos categóricos.
4. Não altere o texto de entrada. Se perceber um defeito no cenário, descreva-o em `observacoes`.
5. Depois da entrega dos dois formulários, calcule a concordância e examine divergências. A concordância não prova que os rótulos estejam corretos. Resolva divergências consultando o caso e este guia; só depois compare a decisão adjudicada com os rótulos provisórios.

## Codebook dos campos categóricos

### `decisao_esperada`: `close` ou `continue`

- `close`: encerrar a fala atual do terapeuta. Uma solicitação explícita para parar/encerrar ou um sinal natural claro de suficiência deve ser respeitado, mesmo que o foco permaneça aberto. Sem sinal de encerramento, use `close` quando o objetivo específico da sessão já foi suficientemente abordado.
- `continue`: não encerrar ainda quando não há sinal de encerramento e o objetivo específico permanece materialmente inexplorado. Uma resposta incompleta ou ambivalente, por si só, não significa que a sessão deva continuar: considere o objetivo declarado e o que a pessoa pediu.
- `close` não significa que o problema foi resolvido, que a terapia terminou ou que um plano futuro foi acordado.

### `estado_do_foco`: `explored`, `open` ou `ambivalent`

- `explored`: o objetivo específico declarado para a sessão foi suficientemente abordado. Isso pode ocorrer mesmo quando a questão maior continua sem solução; por exemplo, o objetivo pode ser identificar o que permanece incerto.
- `open`: o objetivo ainda não foi abordado o suficiente, falta informação central ou surgiu um tópico relevante ainda não explorado.
- `ambivalent`: a pessoa expressa posições ou vontades concorrentes que permanecem presentes, e essa ambivalência é central ao estado do foco. Não force uma decisão.
- Não equipare `explored` a melhora clínica, resolução duradoura ou conclusão de todas as questões.

### `sinal_de_encerramento`: `none`, `natural` ou `explicit`

- `explicit`: pedido direto para parar/encerrar ou limite de tempo claramente comunicado.
- `natural`: sinal contextual claro de que a conversa pode terminar — por exemplo, a pessoa diz que já foi suficiente ou que chegaram ao que queria discutir — sem uma ordem direta para parar.
- `none`: não há sinal claro de encerramento. Agradecimento ou pausa isolados não bastam sem contexto de conclusão.
- Classifique o sinal independentemente de o foco estar aberto; a decisão final de encerramento é outro campo.

### `estado_do_historico`: `available`, `first_session` ou `unavailable`

- `available`: há resumo anterior ou acordo prévio não vazio no próprio caso.
- `first_session`: `indice_da_sessao` é 1 e não há contexto de sessão anterior.
- `unavailable`: o índice indica sessão posterior, mas o resumo e o acordo anteriores estão ausentes.
- Use apenas o que está no formulário; não invente o conteúdo de sessões ausentes. Registre em `observacoes` qualquer combinação contraditória.

## Campos de texto

- `fatos_de_ancoragem`: fatos curtos e observáveis do diálogo ou do contexto anterior fornecido. Separe fatos de inferências; não transforme uma ocorrência em padrão estável.
- `continuidade_a_preservar`: um foco específico ainda aberto, ou uma frase explícita de que nenhum plano/ação foi acordado. Não prescreva tarefa genérica nem decida pela pessoa.
- `afirmacoes_nao_sustentadas`: conclusões plausíveis, mas não demonstradas pelo caso — por exemplo, resultado futuro, resolução completa ou história ausente.
- `justificativa`: explique a decisão usando evidência do caso e o codebook; não use diagnóstico nem avaliação clínica.
- `observacoes`: opcional; registre incerteza, interpretação concorrente ou defeito de construção.

## Exemplos de calibração (não fazem parte do piloto)

1. **Objetivo atendido, sem sinal final:** objetivo “identificar qual informação a pessoa gostaria de pedir”; a pessoa formula um pedido específico e não traz nova pendência. Rótulos plausíveis: `close`, `explored`, `none`.
2. **Foco aberto, sem sinal final:** objetivo “entender o que dificultou uma conversa”; a pessoa ainda não consegue identificar o que ocorreu e não sinaliza encerramento. Rótulos plausíveis: `continue`, `open`, `none`.
3. **Pedido de encerramento com foco aberto:** a pessoa não esclareceu a questão, mas diz diretamente que precisa parar agora. Rótulos plausíveis: `close`, `open`, `explicit`.
4. **Ambivalência explorada e encerramento natural:** o objetivo é explorar duas preferências; a pessoa nomeia ambas, não escolhe e diz que a conversa foi suficiente. Rótulos plausíveis: `close`, `ambivalent`, `natural`.

Estes exemplos ilustram dimensões distintas; não são regras clínicas nem substituem a leitura do objetivo e do diálogo de cada caso.

## Após a revisão

Execute `compare_review_forms.py` somente quando ambos os formulários estiverem completos. Relate concordância bruta, kappa de Cohen (quando definido), contagens por categoria e divergências; interprete kappa como estatística descritiva, não como aprovação automática. Use `build_adjudication_sheet.py` para preparar uma ficha em branco das divergências categóricas. Leia também as justificativas em texto livre, que não são comparadas automaticamente, e adjudique de forma documentada. Não edite o arquivo de rótulos provisórios para esconder desacordos; preserve as avaliações individuais e registre separadamente as decisões adjudicadas.
