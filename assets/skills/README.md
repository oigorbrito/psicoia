# PsychAgent skill catalog localization

Skill catalogs live under `sect/<approach>/stageN/`. The unsuffixed `meta_skills.json` and `micro_skills.json` files remain the source catalogs and are the fallback when a locale-specific catalog is absent.

## Locale file names

For a localized catalog, use the same JSON structure and add the locale suffix before `.json`:

- `meta_skills.en.json` / `micro_skills.en.json`
- `meta_skills.pt-BR.json` / `micro_skills.pt-BR.json`

The loader selects the locale corresponding to `output_language`. Localization coverage is per stage and catalog; missing localized files continue to use the source catalog.

## Data and embedding invariants

- Keep catalog keys, `skill_id`, `parent_ids`, and `sect` exactly equal to the source data.
- Translate human-readable fields (`skill_name`, `skill_description`, `when_to_use`, and `trigger` where present) without changing the skill's meaning or clinical scope.
- Do not edit the source-language `micro_skills.pt` cache to store translated text or translated embeddings.
- Embeddings depend on the skill text and embedding model/provider. A localized catalog must use its own `micro_skills.<locale>.pt` cache; when that cache is absent or its SHA-256 fingerprint does not match the catalog and embedding configuration, the runtime backfills embeddings from the localized JSON and writes to the locale-specific cache.
- Do not claim retrieval equivalence across locales without evaluating retrieval quality.

Catalogs without localized files are intentionally not considered localized; they fall back to the source content until their translations are reviewed and added.

## Validation

Run `python scripts/validate_skill_catalog_locales.py --locale en` or `--locale pt-BR` to require complete coverage and validate catalog keys, IDs, relationships, and untranslated Han characters. During ongoing localization, add `--allow-missing` to report current coverage while still validating every locale file that exists.
