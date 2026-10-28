# Independent pilot review guide

## Purpose and scope

Use this guide to review the **case labels** in the synthetic pilot. Do not evaluate a model response or change prompts. Check whether the expected action, focus state, ending signal, and history state are supported by each case; also check the grounding facts, what may be carried forward, and which claims should be avoided.

The cases are synthetic, not clinical, and do not constitute clinical validation. This pilot contains no crisis cases.

## Blinding and independence

1. Each reviewer receives only their CSV (`reviewer-a.csv` or `reviewer-b.csv`) and this guide. Do not share `pilot-labels.jsonl`, the rest of the repository, or the other reviewer's answers before both forms are submitted.
2. Complete the cases without discussing decisions with the other reviewer. The forms use different case orders.
3. Use `observacoes` to record ambiguity, an alternative interpretation, or an inconsistency; still choose the most defensible category in each categorical field.
4. Do not edit the input text. If you notice a scenario-construction defect, describe it in `observacoes`.
5. After both forms are submitted, calculate agreement and examine disagreements. Agreement does not prove the labels are correct. Resolve disagreements by consulting the case and this guide; only then compare adjudicated decisions with the provisional labels.

## Categorical-field codebook

### `decisao_esperada`: `close` or `continue`

- `close`: end the counselor's current turn. Respect an explicit request to stop/end or a clear natural signal of sufficiency, even if the focus remains open. Without an ending signal, use `close` when the specific session objective has been sufficiently addressed.
- `continue`: do not end yet when there is no ending signal and the specific objective remains materially unexplored. An incomplete or ambivalent response alone does not mean the session must continue: consider the stated objective and what the person requested.
- `close` does not mean the problem was resolved, therapy ended, or a future plan was agreed.

### `estado_do_foco`: `explored`, `open`, or `ambivalent`

- `explored`: the specific objective stated for the session was sufficiently addressed. This can be true even when the broader issue remains unresolved; for example, the objective may be to identify what remains uncertain.
- `open`: the objective has not been sufficiently addressed, central information is missing, or a relevant new topic remains unexplored.
- `ambivalent`: competing positions or wishes remain present for the person, and that ambivalence is central to the focus state. Do not force a decision.
- Do not equate `explored` with clinical improvement, lasting resolution, or completion of every issue.

### `sinal_de_encerramento`: `none`, `natural`, or `explicit`

- `explicit`: a direct request to stop/end or a clearly communicated time boundary.
- `natural`: a clear contextual signal that the conversation may end—for example, the person says it was sufficient or that they discussed what they wanted—without a direct instruction to stop.
- `none`: no clear ending signal. A thank-you or pause alone is not enough without a closing context.
- Classify the signal independently of whether the focus is open; the final closure decision is a separate field.

### `estado_do_historico`: `available`, `first_session`, or `unavailable`

- `available`: a nonempty prior summary or prior agreement is present in the case itself.
- `first_session`: `indice_da_sessao` is 1 and no prior-session context is present.
- `unavailable`: the index indicates a later session, but both the prior summary and prior agreement are absent.
- Use only what is in the form; do not invent content from missing sessions. Record contradictory combinations in `observacoes`.

## Text fields

- `fatos_de_ancoragem`: short, observable facts from the dialogue or supplied prior context. Separate facts from inferences; do not turn one occurrence into a stable pattern.
- `continuidade_a_preservar`: one specific unresolved focus, or an explicit statement that no plan/action was agreed. Do not prescribe generic homework or decide for the person.
- `afirmacoes_nao_sustentadas`: plausible conclusions that the case does not demonstrate—for example, a future outcome, complete resolution, or missing history.
- `justificativa`: explain the decision using case evidence and the codebook; do not diagnose or make a clinical assessment.
- `observacoes`: optional; record uncertainty, an alternative interpretation, or a construction defect.

## Calibration examples (not part of the pilot)

1. **Objective addressed, no ending signal:** objective: “identify what information the person would like to request”; the person states a specific request and raises no new unresolved issue. Plausible labels: `close`, `explored`, `none`.
2. **Open focus, no ending signal:** objective: “understand what made a conversation difficult”; the person still cannot identify what happened and does not signal an ending. Plausible labels: `continue`, `open`, `none`.
3. **Request to end with an open focus:** the person has not clarified the issue but directly says they need to stop now. Plausible labels: `close`, `open`, `explicit`.
4. **Ambivalence explored with a natural ending:** the objective is to explore two preferences; the person names both, does not choose, and says the conversation was sufficient. Plausible labels: `close`, `ambivalent`, `natural`.

These examples illustrate distinct dimensions; they are not clinical rules and do not replace reading each case's objective and dialogue.

## After review

Run `compare_review_forms.py` only after both forms are complete. Report raw agreement, Cohen's kappa (when defined), category counts, and disagreements; interpret kappa as descriptive, not as automatic approval. Read the rationales and adjudicate disagreements in a documented way. Do not edit the provisional-label file to hide disagreement; preserve the individual reviews and record adjudicated decisions separately.
