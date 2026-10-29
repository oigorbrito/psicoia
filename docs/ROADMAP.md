# Migration and localization roadmap

This roadmap prioritizes work based on recorded local evidence. It is **not a delivery promise, release guarantee, clinical evaluation, or compliance claim**. Priorities may change as evidence changes; items without an owner, estimate, and completion criteria must not be treated as commitments. The migration rule is literal copying: preserve upstream code and introduce no improvements, fixes, or functional changes. Only approved translation of user-facing content (PT-BR primary, English secondary) and visible PsicoIA branding where it does not affect identifiers or attribution are allowed. See the [migration and translation policy](MIGRATION-POLICY.md).

## Priority 0 — preserve and integrate with provenance

**Status: local integration and governance/documentation commits created; no push.** The source tree snapshot has 1,390 untracked paths; `master`, `original`, and `origin/main` have histories with no common ancestor. The candidate is on branch `integration/psicoia` in a separate worktree, based on `origin/main`; commit `af5cc72` integrates `original` with `origin/main`. `origin/main` contains the evidence template, while `original` tracks PsychAgent upstream. A working-tree archive was created outside the repository at `../psicoia-worktree-before-integration.tar.gz` (52 MB), plus a Git bundle at `../psicoia-git-refs-before-integration.bundle` (54 MB). The archive listing and bundle were verified. SHA-256: tree `bf5ea3b95581ded2e29ff1a97243a23d63759f7a65c0086d097f6fc18b597bc0`; bundle `0fef368c5132d1bba52e8b8b08905f47df510ae837999adce8cc6150276ec939`. Both are on the same local volume; they are not independent protection against disk failure.

- The source tree and Git refs/history have been safeguarded in separate verified files; retain them until integration review is complete. For disaster recovery, also copy them to another volume or secure location.
- The separate candidate uses `origin/main` as its base; the merge of `original` code is in `af5cc72` and governance/documentation in `10a251f`, without changing the source worktree.
- Review the complete inclusion list; exclude caches, editor files, temporaries, secrets, and generated artifacts.
- Keep upstream as a reference; do not rebase unrelated histories or force-push.

**Completion evidence:** base, commits/SHAs, and included/excluded files are recorded; integration is reviewable and no work is lost.

## Priority 1 — classify upstream differences

**Status: Block 08 audited the 104 source-tree differences by class; semantic validation remains pending where noted.** Against upstream snapshot `469f45ef468b968b3fccd1936d7e6a0a574e4c5c`, 1,289 of 1,393 paths are identical, 104 differ and none are missing. AST normalization found 12 structural Python differences among 41 changed Python files. The source tree contains 74 local additions (excluding caches/editor clutter); two catalogs have a `.partial` suffix. See `PSICOIA_BLOCK08_RESULT.md` and the inventory for evidence and scope.

- Semantically review the prose in the eight localized READMEs and the 33 prompts, including placeholder/default changes and three removed `{{number}}` occurrences in the skill selector.
- Treat API, runtime, default, parsing, and retrieval changes as blocking deviations; do not include them without separate authorization and appropriate validation.
- Keep evaluation/repair prompts, data, profiles, catalogs, and technical contracts under specific review; structural tests do not prove clinical or behavioral equivalence.
- Record new decisions, validation, or evidence in `docs/MIGRACAO-UPSTREAM.pt-BR.md`; leave items without evidence pending.

**Completion evidence:** reproducible inventory with a rationale for each material difference; items lacking evidence remain pending.

## Priority 1 — licensing and provenance

**Status: user preference recorded; application blocked on provenance/authority.** The user selected MIT as the desired license. The harness still finds no recognized license file; the consulted upstream snapshot has no `LICENSE`, `COPYING`, or `LICENSES` path. The selection does not establish ownership or permission to relicense upstream code.

- Confirm authority to apply MIT to the intended content, including upstream code, models, datasets, profiles, images, prompts, and dependencies.
- Confirm the exact copyright holder and year for the notice.
- Do not create or declare `LICENSE` until these points are resolved; do not publish content with uncertain provenance.

**Completion evidence:** evidence of authority, confirmed holder/year, and applicable MIT text, or explicit distribution restrictions.

## Priority 2 — technical validation

**Status: locally verified on `reconciliation/psicoia-block08` (2026-10-29).** Default `python -m pytest -q`: 17 passed; the evidence template tests run separately: 4 passed. `src/web` Node tests: 2 passed; Vite build and backend import smoke passed (20 routes). The harness reports the unresolved license gap and unknown external controls. `npm audit` reports 9 advisories; `pip-audit` reports 14 Starlette advisory records. No dependency upgrade or production-security claim was made.

- `pytest.ini` scopes default collection to project tests and prevents the template `test_harness` name collision without deleting template content.
- Web unit tests cover pure domain/helper functions only; API flows, React UI, authentication/CORS, and localization quality remain untested. Catalog validators remain outside the candidate pending locale/retrieval review.
- Run builds and startup/documentation checks when dependencies and environment are available; record failures and limitations.

**Completion evidence:** commands and results recorded on the integrated tree, with unresolved failures identified rather than hidden.

## Priority 2 — controlled localization

**Status: PT-BR is the localization goal; code-level language implementation pending separate review.** English is secondary. The upstream UI and sample defaults remain unchanged in this candidate; the local implementation that propagates `output_language`, changes web contracts, or selects catalogs by locale is pending: do not expand, integrate, or remove it until specific review, and preserve the existing local work. Local structural validation reports PT-BR at 16/30 catalogs (1,233/5,158 records) and English at 8/30 (141/5,158); these catalogs are not included here. All 60 files under `prompts/eval/` contain Chinese text.

- Continue with approved documentation and presentation text, keeping PT-BR primary. Do not expand code/contract changes for localization while the `output_language` exception is pending.
- Preserve contracts, examples that are research data, and technical names. Replace `PsychAgent` with `PsicoIA` only in presentation prose referring to the destination product; retain academic and upstream attribution.
- Treat translated evaluation prompts as behavior changes, requiring a fixed benchmark, schema checks, and human review before replacing source prompts.
- For catalogs, create/update embeddings per language and validate retrieval before enabling localized retrieval text.
- Update counts only from reproducible validation; structural coverage is not completed linguistic review.

**Completion evidence:** declared scope and coverage, with validations appropriate to content type; do not claim complete localization without an audit.

## Priority 3 — external controls and publication

**Status: externally unknown.** Hosted GitHub settings, MFA, branch rules, active users, published releases, private reporting channel, and deployment were not proven by the local tree.

- Query authoritative platform evidence before documenting these states.
- Establish private vulnerability reporting, support, and release procedures before making related guarantees.
- Enable CI/hosted controls only after reviewing permissions, action pinning, and repository policy.

**Completion evidence:** external evidence with source and verification date, or keep the item explicitly `UNKNOWN_EXTERNAL`.

## Updating this roadmap

Update after material changes to branch/base, licensing, localization scope, test results, or external status. Record facts; do not invent dates or turn goals into promises.
