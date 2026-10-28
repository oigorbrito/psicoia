---
name: localization-guardrails
description: Safely localize this repository's user-facing interface and documentation into English and Brazilian Portuguese. Use when translating UI text, user-visible messages, or project docs; preserve runtime behavior, APIs, data, and original English code identifiers.
compatibility: Requires repository access; frontend validation may require Node.js/npm and backend validation may require Python dependencies.
---

# Localization guardrails for PsychAgent

Perform conservative localization only. The repository's source code, identifiers, interfaces, and runtime behavior are not translation targets. Do not use localization as an opportunity to refactor, improve, rename, or redesign the application.

## Before editing

1. Identify the exact requested scope (for example, frontend UI, web backend messages, prompts, or documentation). Do not silently expand it to the entire repository.
2. Inspect the relevant files and determine whether text is user-visible or is part of a programmatic contract.
3. Check existing locale conventions and configuration before introducing any mechanism. Do not assume that a language selector or i18n framework exists.
4. Establish a baseline for relevant checks where practical; record pre-existing failures rather than attributing them to translation.

## Invariants: never translate or change

Preserve exactly unless the user explicitly requests otherwise:

- Python/JavaScript identifiers, filenames, module names, imports, CLI flags, environment-variable names, URLs, API routes, JSON/YAML keys, database fields, enum values, and serialized values.
- Prompt variables/placeholders and their syntax, including Jinja expressions such as `{{ ... }}` and `{% ... %}`.
- File paths, links, code samples, command-line examples, model names, citations, metrics, dataset values, and content used as machine-readable input.
- Data in `assets/`, `data/`, and evaluation/scoring material unless the user explicitly includes a specific data-backed feature in scope. Never translate psychological instrument items, benchmark examples, or research data as incidental cleanup. For an explicitly approved skill-catalog localization, preserve machine identifiers and relationships (such as `skill_id`, `parent_ids`, and `sect`) exactly; localize only human-readable fields.
- Existing defaults and control flow. Do not change response schemas, persistence, authentication, validation, or API error codes to accommodate translated wording.

When uncertain whether a string is a contract or user-facing copy, leave it unchanged and flag it for clarification.

## Locale and translation policy

- Target locales are English (`en`) and Brazilian Portuguese (`pt-BR`). Use Brazilian Portuguese, not European Portuguese.
- Preserve English as the source-language content where it is already the project's original wording. Do not mechanically translate established English copy.
- Translate only in-scope user-facing prose. Keep product names, therapy acronyms (BT, CBT, HET, PDT, PMT), technical terms, and identifiers stable unless a clear localized display label is appropriate.
- Keep the meaning, safety qualifiers, level of certainty, and clinical boundaries of the original. Never turn informational or research content into diagnosis, treatment advice, promises, or crisis guidance beyond the source.
- Use consistent terminology within the requested scope. Prefer clear, respectful, neutral language; avoid stigmatizing descriptions. Preserve placeholders and punctuation needed for interpolation.
- If adding locale resources, keep stable keys separate from translated values, ensure both locales provide the same required keys, and retain existing fallback/default behavior. Do not add a dependency or localization framework unless the user authorizes that implementation choice.
- Do not claim translated prompts preserve model behavior without testing. Prompt translation can affect outputs; treat it as a separately scoped, behavior-sensitive change.
- Skill-catalog localization is also behavior-sensitive: retrieval text contributes to embeddings. Never reuse embeddings generated from source-language text for translated text. Use language-specific embedding caches or regenerate and validate embeddings for each locale; do not overwrite the source-language cache.

## Safe workflow

1. Inventory only the files and strings in scope; distinguish visible copy from identifiers, data, and prompt templates. For skill catalogs, inspect loaders, embedding caches, and retrieval consumers before translating any fields.
2. Make the smallest textual changes possible. Prefer existing localization patterns; if none exist, propose or implement only the smallest explicitly approved mechanism.
3. Check interpolation, escaping, pluralization, line breaks, markup, accessibility labels, and encoding. Avoid changing surrounding logic while editing copy.
4. Review the diff for accidental changes to keys, values, data, examples, or behavior. Confirm that both locales have equivalent coverage if locale resources were added.
5. Run relevant validation: frontend build or tests for frontend changes; Python syntax/tests for backend changes; link/path checks for docs where feasible. Report checks that could not be run and existing failures honestly.

## Completion report

Summarize the scope and files changed, state that identifiers/contracts/data were preserved (only if verified), list validation performed and its outcome, and call out untranslated or ambiguous text left out of scope. Do not claim complete project localization unless the entire agreed scope was audited.