# Rascunhos de prompts de avaliação / Evaluation prompt drafts

## Português (Brasil)

**Estado: REVIEW_REQUIRED.** Existem rascunhos PT-BR e EN para as 60 fontes (60/60 por idioma; 120 arquivos de rascunho). Os originais permanecem inalterados. Todos os rascunhos aguardam revisão semântica e clínica especializada; não são traduções aprovadas e devem permanecer fora do fluxo clínico/avaliação ativo e do runtime.

As verificações estruturais podem detectar diferenças em placeholders, chaves, números, tags e formato, mas **não comprovam equivalência semântica, validade clínica nem preservação integral dos critérios**. A validação estrutural não substitui a revisão especializada.

### Problemas identificados nos originais — preservados nos rascunhos

- `prompts/eval/human_vs_llm_eval.txt`: o exemplo de saída JSON original é inválido. O conteúdo foi preservado, sem correção silenciosa.
- `prompts/eval/plan_consistency/OverallGoalConsistency.txt` e `PersonaConsistency.txt`: os critérios indicam nota padrão 5, mas uma orientação posterior diz para usar nota padrão 2 quando faltam informações. A contradição foi preservada.
- `prompts/eval/stai/STAI.txt`: o conteúdo identifica a escala como Web Form H (Client Behavior System), embora o nome do arquivo seja `STAI.txt`. A divergência de nome/conteúdo foi preservada.

## English

**Status: REVIEW_REQUIRED.** PT-BR and EN drafts exist for all 60 source prompts (60/60 per language; 120 draft files). The originals remain unchanged. Every draft is awaiting specialist semantic and clinical review; these are not approved translations and must remain outside active clinical/evaluation workflows and the runtime.

Structural checks can detect differences in placeholders, keys, numbers, tags, and format, but **do not establish semantic equivalence, clinical validity, or complete preservation of the criteria**. Structural validation does not replace specialist review.

### Issues identified in the originals — preserved in the drafts

- `prompts/eval/human_vs_llm_eval.txt`: the original illustrative JSON output is invalid. Its content was preserved without silent correction.
- `prompts/eval/plan_consistency/OverallGoalConsistency.txt` and `PersonaConsistency.txt`: the scoring criteria specify default score 5, while a later instruction says to use default score 2 when information is insufficient. This contradiction was preserved.
- `prompts/eval/stai/STAI.txt`: the content identifies the instrument as Web Form H (Client Behavior System), although the filename is `STAI.txt`. The filename/content discrepancy was preserved.
