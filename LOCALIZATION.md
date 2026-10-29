# Localization policy and status

## Language goals

Brazilian Portuguese (`pt-BR`) is the primary language; English (`en`) is secondary. The web interface has localized copy for major flows and a browser-persisted language selector, but coverage remains partial. The selected locale uses the existing `output_language` API field. Operational error/validation messages, descriptive OpenAPI metadata, and CLI help/output were localized without changing routes, field names, enums, persisted IDs, or response formats. Generation language instructions were localized narrowly; clinical guidance, behavior-sensitive content, evaluation prompts, and catalogs were not translated. The explicit Block 14 exception to literal copying is documented in [PSICOIA_BLOCK14_LOCALIZATION_CLOSURE.md](PSICOIA_BLOCK14_LOCALIZATION_CLOSURE.md). See also the [migration and translation policy](docs/MIGRATION-POLICY.md).

## Safe boundaries

- Localize approved presentation prose without changing API routes, request/response field names, enums, CLI options, environment variables, technical filenames, or data keys. Explicitly authorized functional exceptions must be small, isolated, documented, and tested.
- The web presentation layer maps stage/approach labels from stable IDs. Operational API messages are localized without changing response shape; preserved domain values and descriptions do not imply a fully localized interface.
- Keep Chinese stage aliases and recognized values unchanged where they are used to read legacy content or select application behavior.
- Treat prompt text as behavior-sensitive. Block 14 authorization covers only language instructions for responses and generated text values, preserving the remaining content, delimiters, and JSON keys. Do not translate clinical guidance, evaluation prompts, or benchmark content without specific authorization and validation.
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

- Web UI: navigation, authentication, course/session flows, statuses, and mapped errors are localized; stage labels are displayed from stable IDs. Session-focus values and unknown strings retain their source content. Real Chromium exercised locale selection/persistence, registration, course creation, and message sending through a local synthetic API, including `output_language` mapping for PT-BR and English. Provider text was synthetic; model language quality was not evaluated.
- API/CLI: authentication, operational errors, and validation retain status/response shape with PT-BR messages; OpenAPI field descriptions are also PT-BR. The sample/eval/RFT entrypoint help and OpenAPI title present PsicoIA without renaming modules, flags, or compatibility identifiers.
- Prompts: final language instructions for generated responses/text were adjusted in authorized paths without translating source clinical prompts, recommendations, scales, or evaluation prompts.
- Documentation: project and web guides are available in English and PT-BR; legacy `README_CN.md` keeps its path and points to the maintained guides. Academic attribution and PsychAgent references remain preserved.
- Evaluation prompts: all 60 files under `prompts/eval/` contain Chinese text. They are used by scoring methods, so translating them is a behavior-sensitive project requiring score comparisons on a fixed evaluation set and schema checks.
- Skill catalogs: local translation work reports PT-BR coverage of 16/30 catalogs and 1,233/5,158 records, and English coverage of 8/30 catalogs and 141/5,158 records. These translated catalogs are not included in this integration candidate; the counts describe structural coverage only and do not establish translation quality or retrieval equivalence.
- Chinese text in Markdown image paths is retained because those strings are file paths; changing them without renaming the assets and updating references would break links.

Localization remains partial: legacy domain/context values, unmapped strings, clinical content, all 60 evaluation prompts, and most catalog records remain outside scope. The integrated flow used only local synthetic responses; it does not validate model language quality, clinical equivalence, production readiness, or safety. See the Block 14 report for commands, limitations, and evidence states.
