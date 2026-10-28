# Localization policy and status

## Language goals

Brazilian Portuguese (`pt-BR`) is the primary target language; English (`en`) is secondary. In this integration candidate, the upstream web UI remains unchanged; the PT-BR locale implementation in the local source tree is pending separate review and is not included here. Migration requires a literal copy of upstream code: no improvements, fixes, or functional changes. The visible brand may change from PsychAgent to PsicoIA only in presentation prose referring to the destination product. Identifiers, serialized contracts, academic attribution, and upstream references remain unchanged. See the [migration and translation policy](docs/MIGRATION-POLICY.md).

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

- Integration candidate web UI: source behavior remains upstream and the locale selector/output-language implementation is pending. No locale UI tests have been run on this candidate.
- Documentation: English and PT-BR project and web guides are available. The former Chinese README path is retained as a compatibility pointer to the maintained guides.
- Evaluation prompts: all 60 files under `prompts/eval/` contain Chinese text. They are used by scoring methods, so translating them is a behavior-sensitive project requiring score comparisons on a fixed evaluation set and schema checks.
- Skill catalogs: local translation work reports PT-BR coverage of 16/30 catalogs and 1,233/5,158 records, and English coverage of 8/30 catalogs and 141/5,158 records. These translated catalogs are not included in this integration candidate; the counts describe structural coverage only and do not establish translation quality or retrieval equivalence.
- Chinese text in Markdown image paths is retained because those strings are file paths; changing them without renaming the assets and updating references would break links.

This snapshot is not a claim of complete project localization. Update these counts after each validated catalog or prompt release.
