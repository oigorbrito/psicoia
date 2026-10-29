# Pilot: session closure and continuity

This package contains synthetic fixtures for calibrating the rubric in `../../docs/SESSION-CLOSURE-CONTINUITY-EVALUATION.md`. It is a **development pilot**, not a blind benchmark, clinical validation, production test, or evidence that any prompt improved.

## Files

- `pilot-cases.jsonl`: 88 synthetic PT-BR contexts; these are the only data a future prompt run should receive.
- `pilot-labels.jsonl`: expected action, grounding facts, prohibited claims, and provisional dimensions for human review; never provide them to the model during evaluation.
- `validate_pilot.py`: validates JSONL, required fields, IDs, history/action consistency, and duplicate dialogue fixtures; reports marginal and cross-dimension coverage using only the Python standard library.
- `build_review_forms.py`: creates two separately ordered, label-blind review forms from `pilot-cases.jsonl` only.
- `review/templates/reviewer-a.csv` and `review/templates/reviewer-b.csv`: tracked blank templates; provisional labels are not included.
- `prepare_review_assignments.py`: copies blank templates into `review/responses/` without overwriting existing reviewer responses; response files are Git-ignored.
- `package_review_assignments.py`: creates two separate, Git-ignored handoff ZIPs, each containing only that reviewer's blank CSV and the PT-BR guide.
- `review/REVIEW-GUIDE.md` (`.pt-BR.md`): bilingual codebook and process instructions for independent case-label review.
- `validate_review_forms.py`: checks the blank templates match the current case text, contain the same 88 cases, and use different orders.
- `compare_review_forms.py`: after both reviewers finish, reports raw agreement and descriptive Cohen's kappa for categorical labels; it never reads the provisional label file.
- `build_adjudication_sheet.py`: after both forms are complete, creates a separate, blank adjudication sheet for categorical disagreements only.
- `test_review_workflow.py`: tests agreement calculations, input consistency, and protection against overwriting completed forms.

Coverage dimensions are `focus_state` (`explored`, `open`, `ambivalent`), `ending_signal` (`none`, `natural`, `explicit`), and `history_state` (`available`, `first_session`, `unavailable`). These are provisional labels: `explored` means the current session focus was sufficiently addressed, not that a clinical problem was resolved. The 88 cases vary first-session and unavailable-history scenarios, task follow-through, topic changes, disputed progress, agreed/declined plans, and requests to end. Crisis cases are excluded; they require a reviewed safety protocol before fixtures are created.

## Use and limits

Cases and labels are synthetic and provisional, written to start rubric review. They require independent human review, including confirmation that the expected closure decision and carry-forward focus are appropriate. Do not use this pilot to tune and report final performance: the set is known and has no blind split.

Provide each external reviewer only their assigned ZIP from `review/packages/`; each archive contains one CSV and the PT-BR guide, not `pilot-labels.jsonl` or the repository. The Git ignore rule is only a commit safeguard, not access control or secure storage.

To create and validate blank reviewer forms from the repository root:

```bash
python experiments/session-closure-continuity/build_review_forms.py
python experiments/session-closure-continuity/validate_review_forms.py
python experiments/session-closure-continuity/prepare_review_assignments.py
python experiments/session-closure-continuity/package_review_assignments.py
```

The builder refuses to overwrite filled templates unless `--force` is supplied; the assignment-preparation and packaging scripts refuse to overwrite existing response files or ZIPs. Give each reviewer only their corresponding ZIP. Returned CSVs belong in `review/responses/`. After both independent forms are complete, run:

```bash
python experiments/session-closure-continuity/compare_review_forms.py
```

Agreement statistics are descriptive, not evidence that either reviewer is correct. To prepare a blank adjudication sheet for categorical disagreements, run `python experiments/session-closure-continuity/build_adjudication_sheet.py` after both forms are complete. It does not read provisional labels; review free-text differences separately. Do not treat a kappa threshold as an automatic acceptance rule. The package is not loaded by the runtime, does not modify upstream prompts, and makes no model calls. Create the blind test version separately, freeze it before comparison, and size it based on the minimum relevant difference and variability observed in the pilot.
