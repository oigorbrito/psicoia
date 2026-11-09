# Migration and localization roadmap

This roadmap prioritizes work based on recorded local evidence. It is **not a delivery promise, release guarantee, clinical evaluation, or compliance claim**. Priorities may change as evidence changes; items without an owner, estimate, and completion criteria must not be treated as commitments. The migration rule is literal copying: preserve upstream code and introduce no improvements, fixes, or functional changes. Only approved translation of user-facing content (PT-BR primary, English secondary) and visible PsicoIA branding where it does not affect identifiers or attribution are allowed..

**Scoped exception authorized in this task:** implement a new Android client under `android/` with supporting tests and documentation. This does not authorize changes to existing upstream application behavior, catalog wording/IDs, clinical evaluation prompts, or publication. See [Android offline client](ANDROID_OFFLINE.pt-BR.md).

## Priority 0 — preserve and integrate with provenance

**Status: initial safeguard and inventory complete; integration pending.** This snapshot has 1,390 untracked paths; `master`, `original`, and `origin/main` have histories with no common ancestor. `origin/main` contains the evidence template, while `original` tracks PsychAgent upstream. A working-tree archive was created outside the repository at `../psicoia-worktree-before-integration.tar.gz` (52 MB), plus a Git bundle at `../psicoia-git-refs-before-integration.bundle` (54 MB). The archive listing and bundle were verified. SHA-256: tree `bf5ea3b95581ded2e29ff1a97243a23d63759f7a65c0086d097f6fc18b597bc0`; bundle `0fef368c5132d1bba52e8b8b08905f47df510ae837999adce8cc6150276ec939`. Both are on the same local volume; they are not independent protection against disk failure.

- The working tree and Git refs/history have been safeguarded in separate verified files; retain them until integration review is complete. For disaster recovery, also copy them to another volume or secure location.
- Choose the integration base and reconcile the template with PsicoIA code/docs without overwriting useful content or altering upstream source code.
- Review the complete inclusion list; exclude caches, editor files, temporaries, secrets, and generated artifacts.
- Keep upstream as a reference; do not rebase unrelated histories or force-push.

**Completion evidence:** base, commits/SHAs, and included/excluded files are recorded; integration is reviewable and no work is lost.

## Priority 1 — classify upstream differences

**Status: group-level triage complete; line-by-line review pending.** Against snapshot `469f45ef468b968b3fccd1936d7e6a0a574e4c5c`, the current byte comparison finds 1,289 of 1,393 upstream-tracked paths identical; 104 differ and none are missing. The local tree also contains 74 additional files (excluding caches/editor clutter); two catalogs have a `.partial` suffix. See the updated inventory for categories and pending decisions.

- Classify each differing path as approved translation, prose branding change, upstream file addition/removal, or unknown.
- Treat any logic, dependency, data, technical interface, or identifier difference as a deviation: do not include it as part of the literal copy; revert it or obtain separate authorization before changing it.
- Review prompts, configs, data, profiles, catalogs, and technical contracts while preserving them against unauthorized changes.
- Update `docs/MIGRACAO-UPSTREAM.pt-BR.md` and `docs/INVENTARIO-DIFERENCAS-UPSTREAM.pt-BR.md` with decisions and evidence, including unresolved items.

**Completion evidence:** reproducible inventory with a rationale for each material difference; items lacking evidence remain pending.

## Priority 1 — licensing and provenance

**Status: locally confirmed gap.** The harness found no recognized license file; the consulted upstream snapshot also has no `LICENSE`, `COPYING`, or `LICENSES` path. This does not determine ownership or authorize redistribution.

- Review rights and terms for code, models, datasets, profiles, images, prompts, and other dependencies.
- Obtain appropriate guidance/authorization before selecting or declaring a license for the migrated work.
- Do not add a license for convenience or publish content with uncertain provenance.

**Completion evidence:** documented decision backed by evidence and applicable license text, or explicit distribution restrictions.

## Priority 2 — technical validation

**Status: partially verified on both local worktrees; neither is release-ready.** Local `master`: Pytest 47 passed, 2 subtests passed; `compileall` passed; web tests 7/7 passed; `npm ci --ignore-scripts` and `npm run build` passed. Catalog validators report PT-BR 16/30 (1,233/5,158 records) and English 8/30 (141/5,158); the test expects 24 complete locale `.json` files and excludes two `.json.partial` drafts. An isolated web-requirements environment passes `pip check` and application import (20 routes); the global environment's `pip check` fails because unrelated installed `rpy 0.1.1` requires `openai<2` while global OpenAI is 2.54.0. The web requirements allow any `openai>=1.0.0`; fresh resolution selected 3.41.0, so SDK major-version compatibility remains to be reviewed. `npm audit` reports 9 advisories (6 high, 2 moderate, 1 low, 0 critical), including direct `vite`; the dry-run shows that the Vite remediation requires a major upgrade (8.3.5) and does not eliminate advisories without that review. No automatic dependency update was applied. `pip-audit` on the isolated web environment found 14 advisory records for transitive `starlette==0.37.2`; pinned `fastapi==0.110.2` requires Starlette `<0.38`, so remediation requires a coordinated framework upgrade and regression testing. Security review also found inherited demo defaults: unsalted fast SHA-256 password hashes, no token-expiry check, credentialed wildcard CORS, `0.0.0.0` with `--reload` in the server example, and bearer tokens in browser localStorage. These defaults were present upstream and were not changed; the web app is not production-safe as-is. Integration candidate `integration/psicoia`: default pytest collection fails on duplicate `test_harness` module names in the root and `evidence-repo-template`; `--import-mode=importlib` passes 9 tests. Its `npm ci --ignore-scripts` + build and backend import smoke pass (20 routes); no frontend unit-test files are present there. Harness exit code is 0 but reports `GAP` for license and web UI tests plus `UNKNOWN_EXTERNAL` controls; on local `master`, it reports `GAP` for license and `UNKNOWN_EXTERNAL`, with Python/web test files present. The harness output is not a compliance result. These checks do not establish translation quality or retrieval validity.

- The former 23/24 mismatch was traced to a stale expected count: the test scans complete locale `.json` files, and all 24 satisfy its source-contract criterion. The expectation was corrected; no catalog content changed.
- Resolve the integration branch's default pytest collection collision; do not treat the importlib override as a fix. Run the harness and add/define web unit tests before claiming full integration validation.
- Run builds and startup/documentation checks when dependencies and environment are available; record failures and limitations.

**Completion evidence:** commands and results recorded on the integrated tree, with unresolved failures identified rather than hidden.

## Priority 2 — controlled localization

**Status: PT-BR primary; code-level language implementation pending separate review.** PT-BR remains the primary/default language and English secondary. The local implementation that propagates `output_language`, changes web contracts, or selects catalogs by locale is pending: do not expand, integrate, or remove it until specific review, and preserve the existing local work. Current structural validation reports PT-BR at 16/30 catalogs (1,233/5,158 records) and English at 8/30 (141/5,158). All 60 files under `prompts/eval/` contain Chinese text.

- Continue with approved documentation and presentation text, keeping PT-BR primary. Do not expand code/contract changes for localization while the `output_language` exception is pending.
- Preserve contracts, examples that are research data, and technical names. Replace `PsychAgent` with `PsicoIA` only in presentation prose referring to the destination product; retain academic and upstream attribution.
- Treat translated evaluation prompts as behavior changes, requiring a fixed benchmark, schema checks, and human review before replacing source prompts.
- For catalogs, create/update embeddings per language and validate retrieval before enabling localized retrieval text.
- Update counts only from reproducible validation; structural coverage is not completed linguistic review.

**Completion evidence:** declared scope and coverage, with validations appropriate to content type; do not claim complete localization without an audit.

## Priority 3 — external controls and publication

**Status: publication blocked.** No `LICENSE`/`COPYING` was found locally or in the upstream snapshot; rights/provenance for code, model, data, profiles, images, and prompts remain unresolved. The web lockfile has 9 npm advisories including 6 high; the Python web stack has 14 Starlette advisory records, and inherited demo authentication/CORS defaults need separate security review. Dependency fixes require compatibility testing before distribution. `gitleaks` found 0 findings in the current working tree and 0 in Git history. `.gitignore` now excludes `.vs/`, `.env*`, logs, and the local `nul` artifact. Remote `main` was rechecked at `0ca22eb238828a84034535494d00c66396e12110` on 2026-10-29; no open PR was reported. Hosted repository settings, MFA, branch rules, active users, published releases, private reporting channel, and deployment remain externally unverified.

- Query authoritative platform evidence before documenting these states.
- Establish private vulnerability reporting, support, and release procedures before making related guarantees.
- Enable CI/hosted controls only after reviewing permissions, action pinning, and repository policy.

**Completion evidence:** external evidence with source and verification date, or keep the item explicitly `UNKNOWN_EXTERNAL`.

## Updating this roadmap

Update after material changes to branch/base, licensing, localization scope, test results, or external status. Record facts; do not invent dates or turn goals into promises.
