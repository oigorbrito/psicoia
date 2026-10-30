# Skill catalog locale status — partial and behavior-sensitive

The skill catalogs are research-derived retrieval inputs, not ordinary interface copy. The unsuffixed `meta_skills.json` and `micro_skills.json` files remain the source catalogs. The locale-aware loader uses an available sidecar for the selected language and retains the source catalog when a localized file is unavailable; missing localized catalogs are logged. A missing translation is not treated as a completed translation.

## Current structural coverage

- Brazilian Portuguese: 16 of 30 catalog files; 1,233 of 5,158 records.
- English: 8 of 30 catalog files; 141 of 5,158 records.

These counts describe file/record coverage only. They do not establish translation quality, clinical equivalence, retrieval quality, or locale parity. The strict locale validator continues to report missing catalogs.

## Locale file names and invariants

Localized files use the same JSON structure with a locale suffix before `.json`, for example `meta_skills.en.json` and `meta_skills.pt-BR.json`.

- Preserve catalog keys, `skill_id`, `parent_ids`, and `sect` exactly.
- Do not modify source catalogs or translate benchmark/clinical content as incidental cleanup.
- Localized human-readable fields require verified provenance/authorization and suitable translation and clinical review before additional translation or use.
- Embeddings depend on the catalog text and model/provider. A localized catalog must not reuse source-language embeddings; any locale-specific cache requires its own validated generation and invalidation path.
- Do not claim retrieval equivalence across locales without a separate retrieval evaluation.

## Validation

Run `python scripts/validate_skill_catalog_locales.py --locale en --allow-missing` and the corresponding `--locale pt-BR` command to inspect structural coverage. The strict validator fails while catalogs are missing. This validator does not assess translation quality or clinical validity. See [`../../LOCALIZATION.md`](../../LOCALIZATION.md) for the current status and limitations.
