# Testing and evidence

See also the [harness scope and limitations](HARNESS.en.md).

## Local commands

From the candidate worktree root:

```bash
python scripts/harness.py
python -m pytest -q
python -m pytest -q evidence-repo-template/tests/test_harness.py
(cd src/web && npm test && npm run build)
```

`pytest.ini` limits default discovery to project tests in `tests/` and `src/web/tests/`; the template under `evidence-repo-template/` is run separately to avoid the duplicate `test_harness` module name.

Web tests cover Python domain functions and pure JavaScript helpers. They do not cover complete API flows, React components, authentication/CORS security, or localization quality. The localized-catalog validator remains outside this candidate while provenance, retrieval, and language quality are pending.

Report a command as passing only if it was run on the current worktree. Structural tests do not establish translation quality, clinical safety, or retrieval equivalence.

## States

- `PASS`: a local check was run or local evidence observed and met its specific criterion.
- `GAP`: an applicable local criterion was not met.
- `UNKNOWN_EXTERNAL`: depends on external state that was not consulted or cannot be verified locally.
- `NOT_APPLICABLE`: the documented trigger is not active.
- `NOT_RUN`: an applicable check was not run.

## Scope

The harness does not run the full test suite or validate hosted configurations. Consult the report from each run; do not treat the presence of tests or workflows as evidence that they ran successfully.
