# PsicoIA Block 16 — identity and localization result

**Outcome: PARTIAL; no overall closure is claimed.** The audited PsicoIA product identity and selected non-clinical software-localization surfaces pass their separate gates. Catalog translation remains incomplete; clinical validation was not run; redistribution rights remain unknown.

## Independent gates

| Gate | State | Evidence and limits |
|---|---|---|
| `IDENTITY_CANONICAL` | `PASS` | PsicoIA is the displayed project identity in the audited READMEs, web title/header, OpenAPI metadata, CLI help, package metadata, project-state schema, and launcher output. PsychAgent remains only as research/model attribution or a compatibility-critical identifier/path. |
| `SOFTWARE_LOCALIZATION` | `PASS` | Audited non-clinical web flows, CLI help/output, the PT-BR API/OpenAPI contract, launcher message, and English/PT-BR guides are localized; supported API errors are mapped to English in the web layer. Chromium exercised both locales and targeted UI/API flows. This does not claim that every retained research or clinical string is translated. |
| `CATALOG_TRANSLATION` | `GAP` | PT-BR: 16/30 catalog files and 1,233/5,158 records. English: 8/30 files and 141/5,158 records. Strict validation exits non-zero for missing sidecars. No additional catalog text was translated. |
| `CLINICAL_VALIDATION` | `NOT_RUN` | No qualified clinical equivalence, safety, or real-model language-quality review was performed. |
| `REDISTRIBUTION_RIGHTS` | `UNKNOWN_EXTERNAL` | No legal determination or external rights confirmation was obtained. The harness still reports a recognized-license-file gap. |

These gates are independent. In particular, passing identity/software checks does not imply catalog completeness, clinical approval, safety, production readiness, or permission to redistribute.

## Work completed

- Established PsicoIA as the canonical product identity on the audited controlled surfaces. Clarified the ICALK badge as upstream research attribution rather than a claim of current maintenance; retained the paper, arXiv, model/checkpoint, repository, academic citation, and technical compatibility references.
- Updated stale configuration/catalog guidance to reflect the implemented locale-aware catalog loader, existing `output_language` values, and current coverage. Preserved all routes, request/response fields, enum values, persisted IDs, CLI options, environment-variable names, technical filenames, catalog content, and source assets.
- Updated display/log/error prose and module documentation to say PsicoIA where it referred to the local product. Preserved identifiers such as `PsychAgentRunner`, `PsychAgentPromptManager`, `psychagent_*`, `PSYCHAGENT_*`, source-format identifiers, and paths for compatibility/provenance.
- Removed upstream UI screenshots from the PsicoIA interface guides as product examples. The original `paper/web/` screenshots and research figure remain unmodified and are explicitly identified as upstream artifacts, not PsicoIA UI artwork. No new logo/icon was introduced; the existing generic UI glyph was left unchanged.
- Added regression checks covering identity text in bilingual/project guides, frontend source, CLI descriptions, launcher error output, OpenAPI-related metadata, and preserved compatibility identifiers.
- Kept untranslated source/session content visible with its existing disclosure; did not translate protected clinical prompts, evaluation prompts, benchmarks, or skill-catalog records.

## Verification performed

- `PYTHONPATH="src;." python -m pytest -q` — **56 passed**.
- `cd src/web && node --test tests/*.test.js` — **6 passed**.
- `cd src/web && npm run build` — **passed**, Vite transformed 1,603 modules.
- Real local HTTP/OpenAPI and Chromium validation used a temporary database and a synthetic local provider (`python D:/temp/psicoia-block15-browser-validation.py`; the harness is not committed). It verified the PsicoIA OpenAPI title, unchanged `output_language` enum, PT-BR/English rendering and locale persistence, authentication and localized auth error, registration, course creation, status/stage labels, existing API field mapping, CJK disclosure, sidebar collapse/expand, and a 390×844 viewport. All model/embedding responses were synthetic; no real keys, model downloads, paid services, or clinical data were used. This was targeted flow coverage, not exhaustive API/browser/accessibility testing.
- Ran actual `python -m src.sample --help`, `python -m src.eval --help`, `python -m src.rft --help`, and `python scripts/validate_skill_catalog_locales.py --help`; displayed identity and source attribution were inspected.
- `python scripts/validate_skill_catalog_locales.py --locale en --allow-missing` — 8/30 files, 141/5,158 records. PT-BR equivalent — 16/30 files, 1,233/5,158 records. Strict validator returned exit code 1 for each locale because catalogs are missing; this is a reported gap, not an approval.
- `python -m compileall -q src/sample src/eval src/rft src/shared src/web/backend`, `bash -n run_backend.sh run_frontend.sh`, and `git diff --check` — passed. Git emitted only line-ending normalization warnings for several edited text files.
- `python scripts/harness.py` — local file-presence checks passed; recognized license-file check is `GAP`; hosted GitHub controls are `UNKNOWN_EXTERNAL`. The harness explicitly does not run tests or verify platform settings and is not an audit or compliance determination.

## Scope and limitations

No real model language-quality test, clinical review, accessibility audit, broad cross-browser matrix, deployment test, legal review, or rights confirmation was performed. The catalog validator checks structure/coverage, not translation quality, clinical validity, or retrieval equivalence. Original clinical/research text and incomplete catalogs remain untranslated. The project therefore remains **PARTIAL**.

## Repository and commit state

- Worktree: `D:/projetos/psicoia-reconciliation`
- Branch: `reconciliation/psicoia-block16-localization-identity`
- Base: Block 15 final HEAD `077ddc059471436a59ad9e8abcba846707f4ac78`
- Functional commit: `861cff76853bb3b0c1d5b0aed440a32aed94c6d9`
- No push, pull request, merge, publication, or changes to the primary/default worktree were made.
- Other worktrees remained at `D:/projetos/psicoia` HEAD `e13c895850dc074fd5618322c5e7c1cfda34a29c` and `D:/projetos/psicoia-closure-experiment` HEAD `e087949ab4284b922be226828f6ebd494759222c`.
- The three pre-existing untracked Block 13 retrieval reports remain unstaged and untouched: `reports/block13/retrieval_analysis.json`, `reports/block13/retrieval_phi4-mini_3.8b.json`, and `reports/block13/retrieval_qwen3.5_4b.json`.
