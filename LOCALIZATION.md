# Localization policy and status

## Language goals

Brazilian Portuguese (`pt-BR`) is the primary language; English (`en`) is secondary. The web interface now has localized copy for major flows and a browser-persisted language selector, but coverage is incomplete. The selected locale is also sent through the existing `output_language` API field when creating courses/sessions, sending messages, and closing sessions. This work preserves identifiers, contracts, data, academic attribution, and upstream references; clinical content, operational prompts, and catalogs were not translated. Exception to literal copying explicitly authorized by this task: the local language selector and forwarding the selected language through the preexisting `output_language` field; no API routes, enums, or fields were added. See the [migration and translation policy](docs/MIGRATION-POLICY.md).

## Safe boundaries

- Translate approved UI/documentation prose into PT-BR and English without changing behavior, API routes, request/response field names, CLI options, environment variables, filenames, or data keys. Code migration is literal; improvements and fixes are out of scope.
- When an upstream system returns a localized or legacy string that is part of an API response, translate it at the presentation boundary rather than silently changing the backend contract. The local translation implementation is pending and is not part of this integration candidate.
- Keep Chinese stage aliases and recognized values unchanged where they are used to read legacy content or select application behavior.
- Treat prompt text as behavior-sensitive. A translated evaluation prompt can change ratings even when its JSON schema remains valid. Do not replace the source prompt until it has been compared against a benchmark and its output contract verified.
- Treat skill text as retrieval input. Localized skill catalogs require locale-specific embedding caches and retrieval evaluation. Never reuse source-language embeddings for translated text.
- Do not translate benchmark examples or clinical instrument items as incidental cleanup. Such changes need explicit scope, provenance review, and validation.

## Validation commands

From the repository root:

```bash
cd src/web && node --test tests/*.test.js
python scripts/validate_skill_catalog_locales.py --locale en --allow-missing
python scripts/validate_skill_catalog_locales.py --locale pt-BR --allow-missing
```

For a frontend production build, run `cd src/web && npm run build` after installing the frontend dependencies. Link checks should cover all localized Markdown guides. Keep command snippets, placeholders, JSON keys, and code fences equivalent across language versions.

## Current audit snapshot

- Web UI: main navigation, authentication, course creation/completion, session flows, statuses, and interface messages have localized copy. PT-BR/EN status and school labels and mapping to the existing `output_language` enum have unit tests. Stage labels and session-focus values returned by the backend remain in the source language; unmapped error/status strings may also remain untranslated. No interactive browser flow was run.
- Documentation: project and web guides are available in English and PT-BR; the main READMEs identify PsicoIA as the destination while preserving PsychAgent for provenance, paper, model, and research references.
- Evaluation prompts: all 60 files under `prompts/eval/` contain Chinese text. They are used by scoring methods, so translating them is a behavior-sensitive project requiring score comparisons on a fixed evaluation set and schema checks.
- Skill catalogs: local translation work reports PT-BR coverage of 16/30 catalogs and 1,233/5,158 records, and English coverage of 8/30 catalogs and 141/5,158 records. These translated catalogs are not included in this integration candidate; the counts describe structural coverage only and do not establish translation quality or retrieval equivalence.
- Chinese text in Markdown image paths is retained because those strings are file paths; changing them without renaming the assets and updating references would break links.

Localization remains partial. The backend still returns Chinese stage, approach, and context text; data, clinical content, generation/evaluation prompts, and catalogs remain outside this authorized scope. Frontend build and unit tests do not replace linguistic/professional review or integrated model-backed validation. Update this snapshot only when supported by corresponding evidence.
