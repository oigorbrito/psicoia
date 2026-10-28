# PsychAgent skill catalog localization — planned, not enabled

Skill catalogs live under `sect/<approach>/stageN/`. The unsuffixed `meta_skills.json` and `micro_skills.json` files remain the upstream source catalogs. In this integration candidate, the locale-aware loader and translated catalogs are not included; the conventions below describe pending work and do not imply active locale selection.

## Locale file names

For a localized catalog, use the same JSON structure and add the locale suffix before `.json`:

- `meta_skills.en.json` / `micro_skills.en.json`
- `meta_skills.pt-BR.json` / `micro_skills.pt-BR.json`

The local candidate implementation is pending. Do not assume the upstream loader selects these locale files based on `output_language`. If locale selection is approved later, coverage must be tracked per stage and catalog, with an explicitly tested fallback.

## Data and embedding invariants

- Keep catalog keys, `skill_id`, `parent_ids`, and `sect` exactly equal to the source data.
- Translate human-readable fields (`skill_name`, `skill_description`, `when_to_use`, and `trigger` where present) without changing the skill's meaning or clinical scope.
- Do not edit the source-language `micro_skills.pt` cache to store translated text or translated embeddings.
- Embeddings depend on the skill text and embedding model/provider. Any future localized catalog must use its own `micro_skills.<locale>.pt` cache and must not reuse source-language embeddings. Cache generation and invalidation behavior are pending integration and validation.
- Do not claim retrieval equivalence across locales without evaluating retrieval quality.

Catalogs without localized files are intentionally not considered localized; they fall back to the source content until their translations are reviewed and added.

## Validation

The locale validator is local tooling and is not included in this integration candidate. If/when the catalog work is approved and added, run its validator and retrieval evaluation before enabling locale selection.
