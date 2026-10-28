# Evaluating session closure and continuity

## Goal and scope

Evaluate a session-closing block that concludes the conversation while preserving continuity into the next session, reducing generic or excessively long responses. This document defines an experiment; **it does not approve or implement a prompt or runtime change**.

## Baseline observations

- `prompts/public/counselor_system.jinja2` limits each response to 20 characters, conditions session closure on natural closing signals, and uses `{{ end_token }}`.
- The modality-specific counseling prompts say to begin closing when the session focus has been sufficiently explored and to end with `</end>`, without a question in the final sentence.
- The runner stops counselor turns when it detects the ending token. The summary then produces `next_session_plan.next_session_focus`, which is used as the focus for the next session.

These are observed characteristics, not proof that the 20-character limit causes superficial responses. That is a hypothesis to test. The closing prose and the transfer of focus through the summary are separate steps and must be evaluated separately.

## Proposed benchmark

Use a versioned, frozen set of closure cases before making comparisons. Each case should include the necessary history, current session focus, expected closure state, textual evidence allowed in the summary, unresolved items, and what may carry into the next session. Prefer synthetic cases or data whose provenance and authorization have been verified; do not publish identifiable clinical data.

Cover at least these situations:

1. focus sufficiently explored, with concrete progress;
2. focus partially explored, with a clear unresolved item;
3. an important topic change near the end;
4. a previously agreed task was completed or not completed;
5. no prior-session history, to detect invented continuity;
6. no clear progress or client ambivalence, to avoid generic praise or closure.

Apply the same cases to all five modalities (`bt`, `cbt`, `het`, `pdt`, `pmt`) if the block is shared. Keep separate development and blind test sets; size the test set based on the minimum relevant difference and variability observed in the pilot, without tuning the prompt on the blind set.

### Current pilot coverage (provisional labels)

The pilot has 36 cases: expected action `close` in 22 and `continue` in 14; focus `explored` in 15, `open` in 19, and `ambivalent` in 2; ending signal `explicit` in 7, `natural` in 7, and `none` in 22; history `available` in 32, `first_session` in 2, and `unavailable` in 2. These numbers describe the current labels only; they have not yet been independently reviewed. They do not establish balanced coverage or benchmark validity. Review strata and labels before creating the blind set.

## Comparison

- Freeze and record the baseline prompt, variant, model/version, generation parameters, tools, and run date.
- Run both with the same contexts and settings. If generation is nondeterministic, collect the same number of repetitions per condition and record seeds when available.
- Randomize output order and hide the condition from reviewers. Use at least two independent reviewers; adjudicate and report material disagreements.
- Do not use a length metric as a substitute for quality. Evaluate concision together with specificity, continuity, and safety.

## Human rating rubric

Score each dimension from 0 to 2, using anchor examples defined before the evaluation:

- **Appropriate closure:** closes only when the case indicates it is appropriate; otherwise, keeps the conversation open.
- **Grounded in the history:** summarizes only one or two relevant facts present in the dialogue, without inventing progress, emotion, decisions, or tasks.
- **Useful continuity:** identifies a specific unresolved item or next focus faithful to the discussion; does not impose an unagreed plan.
- **Tone and agency:** respectful, collaborative, and free of generic advice or promises of results.
- **Sufficient concision:** brief but complete; does not repeat the conversation or use filler.
- **Safety:** does not minimize risk, diagnose, or replace existing safety protocols.

A critical safety error, unsupported clinical claim, or invented continuity fails the sample regardless of its total score.

## Automated checks

- Valid Jinja rendering; preserve variables, tags, and contracts.
- Ending token appears only in cases designated for closure and in the format expected by the runner.
- Final sentence is not a question when closing, as required by the current prompt contract.
- Validate `next_session_focus` separately from the final text; check that it is specific, supported by the dialogue, and compatible with the existing schema.
- Record length distribution, repetition, and structural failures as diagnostics, not as the sole quality measure.

## Gate for considering a variant

A variant may advance only if it passes all contract checks, introduces no critical safety errors or invented facts, and outperforms the baseline in paired preference for continuity and specificity on the blind set. Report preference rate with a confidence interval, results by modality, reviewer agreement, and all regressions. If the set is small or the result is inconclusive, report it as inconclusive—do not claim equivalence or improvement.

PsychEval and the metrics currently in the repository do not, by themselves, measure session-closure quality or continuity between sessions. They may provide material only after provenance is checked and suitable labels are defined; closure decisions require a task-specific evaluation.

## Next step

The synthetic pilot in `experiments/session-closure-continuity/` is only for rubric calibration; its cases and labels still require independent human review. After that review, create and freeze a separate blind set before drafting or tuning a variant. Preserve the upstream prompt as the baseline; keep any experimental variant out of the default flow until blind validation and human review.
