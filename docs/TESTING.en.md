# Testing and evidence

See also the [harness scope and limitations](HARNESS.en.md).

## Local commands

From the candidate worktree root:

```bash
python scripts/harness.py
python -m pytest -q --import-mode=importlib
python -m pytest -q tests/test_harness.py tests/test_localized_documentation.py
```

The `--import-mode=importlib` option avoids an import collision between `evidence-repo-template/tests/test_harness.py` and `tests/test_harness.py`. Without it, `python -m pytest -q` fails during collection with `import file mismatch` for the `test_harness` module; this collection failure is documented, not fixed.

The web test suite and localized-catalog validator are not included because they belong to pending localization changes. Do not run their commands as though those features were active in this candidate.

Report a command as passing only if it was run on the current worktree. Structural tests do not establish translation quality, clinical safety, or retrieval equivalence.

## States

- `PASS`: a local check was run or local evidence observed and met its specific criterion.
- `GAP`: an applicable local criterion was not met.
- `UNKNOWN_EXTERNAL`: depends on external state that was not consulted or cannot be verified locally.
- `NOT_APPLICABLE`: the documented trigger is not active.
- `NOT_RUN`: an applicable check was not run.

## Scope

The harness does not run the full test suite or validate hosted configurations. Consult the report from each run; do not treat the presence of tests or workflows as evidence that they ran successfully.
