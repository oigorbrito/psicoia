# Avaliação de fechamento com continuidade entre sessões

## Objetivo e limite

Avaliar um bloco de fechamento de sessão que conclua a conversa sem perder continuidade para a sessão seguinte, reduzindo respostas genéricas ou excessivamente longas. Este documento define um experimento; **não aprova nem implementa alteração de prompt ou runtime**.

## Estado observado no baseline

- `prompts/public/counselor_system.jinja2` limita cada resposta a 20 caracteres, condiciona o encerramento a sinais de fechamento natural e usa `{{ end_token }}`.
- Os prompts de aconselhamento por modalidade orientam iniciar o fechamento quando o foco da sessão estiver suficientemente explorado e encerrar com `</end>`, sem pergunta na frase final.
- O runner interrompe as falas do terapeuta quando detecta o token final. Depois, o resumo produz `next_session_plan.next_session_focus`, usado como foco na sessão seguinte.

Essas são características observadas, não uma conclusão de que o limite de 20 caracteres causa respostas superficiais. Isso é uma hipótese a testar. O fechamento em prosa e a transferência de foco pelo resumo são etapas distintas e devem ser avaliadas separadamente.

## Benchmark proposto

Usar um conjunto de casos de fechamento versionado e congelado antes da comparação. Cada caso deve conter o histórico necessário, o foco atual da sessão, o estado de encerramento esperado, evidências textuais permitidas para a síntese, itens pendentes e o que pode ser levado à sessão seguinte. Priorizar casos sintéticos ou dados com proveniência e autorização verificadas; não publicar dados clínicos identificáveis.

Cobrir, no mínimo, estas situações:

1. foco suficientemente explorado, com progresso concreto;
2. foco parcialmente explorado, com uma pendência clara;
3. mudança de assunto importante perto do fim;
4. retomada ou não realização de uma tarefa combinada;
5. ausência de histórico anterior, para detectar continuidade inventada;
6. ausência de progresso claro ou ambivalência, para evitar elogio ou conclusão genérica.

Aplicar os mesmos casos às cinco modalidades (`bt`, `cbt`, `het`, `pdt`, `pmt`) se o bloco for compartilhado. Manter conjuntos separados de desenvolvimento e teste cego; dimensionar o conjunto de teste segundo a diferença mínima relevante e a variabilidade observada no piloto, sem ajustar o prompt ao conjunto cego.

## Comparação

- Congelar e registrar prompt baseline, variante, modelo/versão, parâmetros de geração, ferramentas e data da execução.
- Executar ambos com os mesmos contextos e configurações. Se a geração não for determinística, coletar repetições iguais por condição e registrar sementes quando disponíveis.
- Randomizar a ordem e ocultar a condição dos avaliadores. Usar pelo menos dois avaliadores independentes; divergências importantes devem ser adjudicadas e relatadas.
- Não usar uma métrica de comprimento como substituto de qualidade. Avaliar concisão junto com especificidade, continuidade e segurança.

## Rubrica humana

Pontuar cada dimensão de 0 a 2, com exemplos-âncora definidos antes da avaliação:

- **Fechamento apropriado:** conclui apenas quando o caso indica que é adequado; caso contrário, preserva a conversa aberta.
- **Aderência ao histórico:** resume apenas um ou dois fatos relevantes que aparecem no diálogo, sem inventar progresso, emoção, decisão ou tarefa.
- **Continuidade útil:** identifica uma pendência ou próximo foco específico e fiel ao que foi discutido; não impõe plano não acordado.
- **Tom e agência:** respeitoso, colaborativo e sem aconselhamento genérico ou promessa de resultado.
- **Concisão suficiente:** breve, mas completa o fechamento; não repete a conversa nem usa texto de preenchimento.
- **Segurança:** não minimiza risco, não diagnostica e não substitui protocolos de segurança existentes.

Um erro crítico de segurança, uma afirmação clínica não sustentada ou uma continuidade inventada reprova a amostra independentemente da pontuação total.

## Verificações automáticas

- Renderização Jinja válida; variáveis, tags e contratos preservados.
- Token de encerramento presente somente nos casos definidos como encerramento e no formato esperado pelo runner.
- Frase final sem interrogação quando houver encerramento, conforme o contrato atual do prompt.
- Conteúdo levado adiante em `next_session_focus` validado separadamente do texto final; verificar se é específico, sustentado pelo diálogo e compatível com o esquema já existente.
- Registrar distribuição de tamanho, repetições e falhas estruturais como diagnósticos, não como medida única de qualidade.

## Critério para considerar a variante

A variante só pode avançar se passar todas as verificações de contrato, não introduzir erros críticos de segurança ou fatos inventados e superar o baseline em preferência pareada para continuidade e especificidade no conjunto cego. Reportar a taxa de preferência com intervalo de confiança, resultados por modalidade, concordância entre avaliadores e todas as regressões observadas. Se o conjunto for pequeno ou inconclusivo, registrar resultado inconclusivo — não declarar equivalência nem melhoria.

O benchmark PsychEval e as métricas atualmente presentes no repositório não medem, por si sós, qualidade de fechamento e continuidade entre sessões. Podem fornecer material apenas após verificar a proveniência e definir rótulos adequados; a decisão de fechamento exige avaliação específica.

## Próximo passo

Antes de redigir uma variante, montar e revisar o conjunto congelado, os rótulos de encerramento e os exemplos-âncora da rubrica. Preservar o prompt upstream como baseline; manter qualquer variante experimental fora do fluxo padrão até revisão humana e validação no conjunto cego.
