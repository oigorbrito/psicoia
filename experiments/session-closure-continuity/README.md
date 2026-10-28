# Pilot: session closure and continuity

This package contains synthetic fixtures for calibrating the rubric in `../../docs/SESSION-CLOSURE-CONTINUITY-EVALUATION.md`. It is a **development pilot**, not a blind benchmark, clinical validation, production test, or evidence that any prompt improved.

## Files

- `pilot-cases.jsonl`: 36 synthetic PT-BR contexts; these are the only data a future prompt run should receive.
- `pilot-labels.jsonl`: expected action, grounding facts, prohibited claims, and provisional dimensions for human review; never provide them to the model during evaluation.
- `validate_pilot.py`: validates JSONL, required fields, IDs, and case/label matching using only the Python standard library.

Coverage dimensions are `focus_state` (`explored`, `open`, `ambivalent`), `ending_signal` (`none`, `natural`, `explicit`), and `history_state` (`available`, `first_session`, `unavailable`). These are provisional labels: `explored` means the current session focus was sufficiently addressed, not that a clinical problem was resolved. The 36 cases also vary task follow-through, topic changes, disputed progress, agreed/declined plans, and requests to end. Crisis cases are excluded; they require a reviewed safety protocol before fixtures are created.

## Use and limits

Cases and labels are synthetic and provisional, written to start rubric review. They require independent human review, including confirmation that the expected closure decision and carry-forward focus are appropriate. Do not use this pilot to tune and report final performance: the set is known and has no blind split.

The package is not loaded by the runtime, does not modify upstream prompts, and makes no model calls. Create the blind test version separately, freeze it before comparison, and size it based on the minimum relevant difference and variability observed in the pilot.
