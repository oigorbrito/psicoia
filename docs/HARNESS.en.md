# Local evidence harness

`scripts/harness.py` is a small checker specific to this repository. It is not a full implementation of OpenSSF OSPS, NIST SSDF, or DORA, and it does not produce certification, a security audit, or an achieved maturity level.

## How to run

From the repository root:

```bash
python scripts/harness.py
```

The command loads `policy/project-state.json`, checks a subset of its fields, and reports the OSPS reference and recorded target level. That level is a stated goal, not an assessment result.

## Current local checks

- `CONTRIBUTING.md` exists;
- a recognized license location exists (`LICENSE`, `COPYING`, or `LICENSES`);
- Python tests exist under `tests/test_*.py`;
- web UI tests exist under `src/web/tests/*.test.js`.

For each item, `PASS` only means that the expected file or file set was found. `GAP` means it was not found. The harness does not assess quality or run tests. A missing license is a reported gap, not an automatic license choice.

The harness classifies GitHub settings, MFA, active users, releases, a private security-reporting channel, and deployment as `UNKNOWN_EXTERNAL`. These items require an authoritative external check; local state cannot prove them.

## State validation and exit codes

The harness performs limited structural validation of project state: schema and baseline versions, target level, enumerated values, and types of some fields. The full schema is in `policy/project-state.schema.json`; the harness does not run an independent JSON Schema validator.

- Exit code `0`: state was read and results printed. `GAP` items may still be present; zero does not mean all checks passed.
- Exit code `2`: state is missing, is not valid JSON, or fails the harness's limited validation.

The command does not run pytest, Node tests, builds, catalog validation, or GitHub API queries. Run these separately as described in [`docs/TESTING.en.md`](TESTING.en.md) and record the actual results.

## Harness changes

When a control is added, removed, or changed, update this document and the corresponding tests. Each check should state what it observes and its limitations; evidence that was not consulted must remain unknown, not be presented as a pass.
