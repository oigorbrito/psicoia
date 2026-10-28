# Pilot: session closure and continuity

This package contains synthetic fixtures for calibrating the rubric in `../../docs/SESSION-CLOSURE-CONTINUITY-EVALUATION.md`. It is a **development pilot**, not a blind benchmark, clinical validation, production test, or evidence that any prompt improved.

## Files

- `pilot-cases.jsonl`: 88 synthetic PT-BR contexts; these are the only data a future prompt run should receive.
- `pilot-labels.jsonl`: expected action, grounding facts, prohibited claims, and provisional dimensions for human review; never provide them to the model during evaluation.
- `validate_pilot.py`: validates JSONL, required fields, IDs, and case/label matching using only the Python standard library.
- `build_review_forms.py`: creates two separately ordered, label-blind review forms from `pilot-cases.jsonl` only.
- `review/reviewer-a.csv` and `review/reviewer-b.csv`: blank independent review forms; provisional labels are not included.
- `validate_review_forms.py`: checks the blank templates contain the same 88 cases in different orders.
- `compare_review_forms.py`: after both reviewers finish, reports raw agreement and descriptive Cohen's kappa for categorical labels; it never reads the provisional label file.
- `test_review_workflow.py`: tests agreement calculations, input consistency, and protection against overwriting completed forms.

Coverage dimensions are `focus_state` (`explored`, `open`, `ambivalent`), `ending_signal` (`none`, `natural`, `explicit`), and `history_state` (`available`, `first_session`, `unavailable`). These are provisional labels: `explored` means the current session focus was sufficiently addressed, not that a clinical problem was resolved. The 88 cases vary first-session and unavailable-history scenarios, task follow-through, topic changes, disputed progress, agreed/declined plans, and requests to end. Crisis cases are excluded; they require a reviewed safety protocol before fixtures are created.

## Use and limits

Cases and labels are synthetic and provisional, written to start rubric review. They require independent human review, including confirmation that the expected closure decision and carry-forward focus are appropriate. Do not use this pilot to tune and report final performance: the set is known and has no blind split.

To create and validate blank reviewer forms from the repository root:

```bash
python experiments/session-closure-continuity/build_review_forms.py
python experiments/session-closure-continuity/validate_review_forms.py
```

The builder refuses to overwrite filled forms unless `--force` is supplied; back up completed ratings before any forced regeneration. After both independent forms are complete, run:

```bash
python experiments/session-closure-continuity/compare_review_forms.py
```

Agreement statistics are descriptive, not evidence that either reviewer is correct. Inspect free-text rationales and adjudicate disagreements separately; do not treat a kappa threshold as an automatic acceptance rule. The package is not loaded by the runtime, does not modify upstream prompts, and makes no model calls. Create the blind test version separately, freeze it before comparison, and size it based on the minimum relevant difference and variability observed in the pilot.
