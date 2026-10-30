# PsicoIA Block 17 — provenance and publication gate

**Decision: no publishable PR candidate is established.** Keep this work local pending rights-holder authorization and proof of ownership for local additions. No source code, clinical content, datasets, dependency files, or the existing Block 13 reports were changed.

## 1. Canonical source and attribution

Read-only verification on **2026-10-30 00:14 -0300**:

- Upstream repository: <https://github.com/ECNU-ICALK/PsychAgent.git>.
- `git ls-remote --symref upstream HEAD refs/heads/main` returned `main` at **`469f45ef468b968b3fccd1936d7e6a0a574e4c5c`**; the local `original` and `upstream/main` refs match that SHA. This establishes the exact source snapshot checked, not the identity or authority of its publisher.
- That source history has two commits: initial `638646b6f49f08c347815fe93fa6c9b80d112142` (2026-04-02) and `469f45ef468b968b3fccd1936d7e6a0a574e4c5c` (2026-04-06, “Update project state”). Both record author and committer `yutaoyang <yangyutao@yutaoyangdeMacBook-Pro.local>`. The inspected commits are unsigned (`%G?` = `N`); the local-machine email does not independently authenticate the person or rights.
- The source README and paper identify the work as **“PsychAgent: An Experience-Driven Lifelong Learning Agent for Self-Evolving Psychological Counselor.”** The paper lists Yutao Yang, Junsong Li, Qianjun Pan, Jie Zhou, Kai Chen, Qin Chen, Jingyuan Zhao, Ningning Zhou, Xin Li, and Liang He. The paper gives affiliations to East China Normal University and Shanghai AI Laboratory. The README acknowledges PsychEval and API/Jinja2/Pydantic tooling. These are attribution leads, not a per-file ownership map or proof that the listed authors hold every relevant right.
- Git contains no `AUTHORS`, `CONTRIBUTORS`, `NOTICE`, copyright/license sidecar, or signed provenance statement. No per-file authorship can be inferred merely from the two-commit snapshot.

## 2. License and notice evidence

### Upstream code and files

- At the checked upstream SHA, all **1,393 tracked paths** were inspected for license/notice filenames and the tracked content was searched for SPDX identifiers, copyright statements, “Licensed under,” and similar grant language. No `LICENSE`, `COPYING`, `NOTICE`, `PATENT`, or per-file license notice was found.
- The source README itself says the research release does not include a repository license. Public availability and the “public research release” wording are not a redistribution license.
- Among tracked PsicoIA paths, the only license-named file is `evidence-repo-template/LICENSE-SELECT.md`, which explicitly says it is a selection reminder, not a license. There is no project `LICENSE`, `COPYING`, or `LICENSES/` grant. No MIT license was created. A prior MIT preference in the roadmap is only a preference, not authority to grant MIT rights over upstream or third-party material.
- No license compatibility, patent grant, or redistribution authority for the upstream code was established. **Code rights remain unresolved.**

### Paper and separately licensed dependencies

- The official arXiv record, <https://arxiv.org/abs/2604.00931>, displayed a **CC BY 4.0** license link at verification time: <https://creativecommons.org/licenses/by/4.0/>. This is license evidence for the arXiv e-print, subject to its terms and any material excluded from that license. The local `paper/PsychAgent.pdf` was not hash-compared with the official e-print, and the license was not extrapolated to `paper/web/` screenshots, datasets, code, or other repository assets. The paper/figure files therefore are **not included in a cleared PR subset** on this evidence alone.
- `src/web/package-lock.json` contains 107 package entries, each with a license field: 98 MIT, 6 ISC, 1 BSD-3-Clause, 1 Apache-2.0, and 1 CC-BY-4.0. The CC-BY-4.0 entry is `caniuse-lite@1.0.30001760`; its locally installed package `LICENSE` contains the CC BY 4.0 terms. Direct locked packages include React/React DOM 18.3.1 (MIT), `lucide-react` 0.469.0 (ISC), Vite 5.4.21 (MIT), and `@vitejs/plugin-react` 4.7.0 (MIT). The installed `node_modules` tree is not tracked. This is dependency metadata, **not** a compatibility/obligations review; no third-party notices/SBOM are committed.
- `src/web/requirements.txt` pins FastAPI 0.110.2 (PyPI classifier: MIT), HTTPX 0.27.0 (BSD), SQLModel 0.0.21 (MIT), and Uvicorn 0.30.1 (BSD). Official metadata was queried at <https://pypi.org/pypi/fastapi/0.110.2/json>, <https://pypi.org/pypi/httpx/0.27.0/json>, <https://pypi.org/pypi/sqlmodel/0.0.21/json>, and <https://pypi.org/pypi/uvicorn/0.30.1/json>. The same file leaves OpenAI, PyYAML, and Jinja2 at open lower bounds; root setup instructions also list unpinned Pydantic, aiolimiter, tenacity, and pytest, with optional Torch. There is no project-wide Python lockfile or complete resolved transitive inventory. Exact license/notice obligations for that dependency set are therefore **not fully verified**.
- Dependency licenses do not grant rights in PsychAgent code, data, prompts, or models. The Hugging Face checkpoint is referenced but not present in the inspected repository; its separate terms were not verified.

## 3. Provenance matrix

| Component/files | Provenance observed | Current distribution classification |
|---|---|---|
| Original research code: `src/sample/`, `src/eval/`, `src/rft/`, `src/shared/`, `src/web/` and original scripts/configs | Present at upstream SHA `469f45e`; source Git history names `yutaoyang` | **No confirmed redistribution authorization.** Keep local; do not include in a PR. |
| Local modifications to upstream code/configs/prompts | `git diff original..HEAD`: 69 original paths modified, including software localization, behavior/prompt paths, and documentation/config changes | **Derivative of unlicensed/uncleared source.** Git attribution to `oigorbrito` does not clear the underlying rights. Keep local. |
| Original research data/assets: 1,032 profile files, skill catalogs, evaluation material, prompts, paper assets | Included in the upstream 1,393-path tree; no per-file rights map found | **Rights pending.** Clinical profiles, prompts, skill text, benchmarks, and datasets are excluded from any candidate. |
| New PsicoIA runtime/localization files (including additions under `src/`, web UI, tests, and scripts) | Added/modified in local Git commits authored as `oigorbrito <oigorbrito@gmail.com>`; commits are not signed and no assignment/ownership record was found | **Authorship signal only, not proof of title.** Runtime additions also depend on or modify upstream code. No subset is presently cleared. |
| New bilingual documentation, reports, policy/configuration and catalog sidecars | Local Git additions; some are original prose, some translate or summarize upstream material, and some contain research/clinical content | **Mixed provenance.** No per-file rights manifest or verified author/assignment; translated/derivative material additionally needs source authorization. Keep local pending review. |
| `evidence-repo-template/` (21 files) and the 22-file `origin/main` template | The current remote `origin/main` SHA is `0ca22eb238828a84034535494d00c66396e12110`; it contains a README and evidence template, not the PsychAgent source tree. Git author is `oigorbrito`; no license exists. | **No actual license grant.** `LICENSE-SELECT.md` is not a license. Do not treat this as a rights-cleared third-party or owned component. |
| npm/Python dependencies | Third-party package manifests/metadata listed above; no vendored dependency tree in Git | **Separate license obligations.** Preserve required notices and complete a resolved-version review before distributing source/build artifacts. |
| `paper/PsychAgent.pdf` / paper figure | Official arXiv page indicates CC BY 4.0 for the e-print; local-file identity/exclusions not compared | **Potentially covered only as the exact e-print material under CC BY 4.0.** Not used as blanket permission for Git assets or code; exclude from PR pending file-level confirmation and attribution handling. |
| `paper/web/` screenshots, checkpoint weights, service endpoints | Screenshots are repository assets; weights are not in the tree; configs include upstream/internal endpoint values | **Rights/operational review pending.** Exclude. Do not publish internal endpoint configuration without separate review. |
| Three untracked Block 13 retrieval reports | Pre-existing, untracked worktree files | **Preserved and excluded.** Not staged, modified, or considered for PR. |

## 4. Candidate for `main`

**No legally verifiable PR candidate.** The current remote `origin/main` was independently checked at `0ca22eb238828a84034535494d00c66396e12110` and contains 22 template paths. A direct diff from this Block 16 branch to that `main` is **1,500 additions, 1 modification, 0 deletions**; it would introduce the upstream source tree and other material whose rights are unresolved. Do not open or prepare that PR.

The minimum *future* candidate must be built from a rights-holder-approved file list and a separately verified local-authorship list. It must exclude every upstream/derivative code path and all unlicensed data, prompts, profiles, catalog translations, screenshots, and model artifacts unless each is expressly covered. Newly authored documentation/tests could be considered only after the human author confirms ownership and any copied-template/third-party provenance is resolved. This is a conditional checklist, not a current candidate.

## 5. Authorization request and blockers

A bilingual request draft is in [`docs/REDISTRIBUTION-AUTHORIZATION-REQUEST.pt-BR.md`](docs/REDISTRIBUTION-AUTHORIZATION-REQUEST.pt-BR.md) and [`docs/REDISTRIBUTION-AUTHORIZATION-REQUEST.en.md`](docs/REDISTRIBUTION-AUTHORIZATION-REQUEST.en.md). It asks the rights holder to identify covered code/assets and expressly address modification, translation, derivative works, and public republication. **It was not sent; no permission is claimed.**

Specific blockers:

1. No code license at the exact upstream commit and no written authority from the authors/institution or other rights holder.
2. No file-level ownership map for source code, assets, prompts, datasets, profiles, screenshots, or translations; paper authorship does not automatically establish code title.
3. No proof that Git identity `oigorbrito` alone establishes copyright ownership/assignment for the local additions.
4. No complete Python dependency lock, third-party notice bundle, or full license-compatibility/attribution review; the npm tree includes CC-BY-4.0 material.
5. No confirmation that the local paper PDF/figures match the covered arXiv e-print or that all embedded elements are covered.
6. No separate model/checkpoint license review; no weights are included.

## 6. Worktree, changes, and verification

- Base preserved: `reconciliation/psicoia-block16-localization-identity` at `774a48a93471351a6576f8a230d4003fa6954d26`.
- This Block 17 work is on a new local branch derived from that HEAD. The Block 16 functional branch and all existing code/history were left intact; no source or clinical components were edited.
- Read-only external checks: upstream/origin `git ls-remote`; official arXiv license page; PyPI package JSON metadata for four exact pinned versions. No push, PR, merge, publication, or remote write occurred.
- `PYTHONPATH="src;." python -m pytest -q tests/test_localized_documentation.py tests/test_harness.py` — **5 passed**; a targeted local-link check across the nine changed/new documents found **0 missing links**; `git diff --check` passed.
- `python scripts/harness.py` — file-presence checks passed; recognized-license-file `GAP`; hosted controls `UNKNOWN_EXTERNAL`. The harness does not run tests or determine legal rights.
- No full Python suite was rerun because this branch changes documentation only; no model benchmarks were run.
- Existing worktrees outside this branch and the three untracked retrieval reports were preserved.

## Next human decision

Obtain written authorization from the verified rights holder for a precisely enumerated set of upstream files and derivative/translation/republication rights; separately confirm who owns the local additions and resolve dependency notices. Until then, keep this branch local and do not create a public PR or add a project license.
