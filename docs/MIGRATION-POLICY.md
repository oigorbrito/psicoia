# Migration and translation policy

## Core rule

PsicoIA is a faithful migration of the PsychAgent upstream source, not an opportunity to refactor it. The code copy must remain literal: do not add improvements, optimizations, fixes, features, dependencies, broad formatting, architecture changes, or behavior changes during migration.

The canonical display name of the destination project is **PsicoIA**; the repository slug is **`psicoia`**. Replace the PsychAgent product brand with PsicoIA in user-facing presentation text when referring to the migrated product. Preserve academic attribution and the names of the paper, authors, published checkpoint/models, and upstream project when referring to their source.

## Allowed changes

1. Copy upstream code files without functional modifications.
2. Translate Chinese user-facing prose and approved documentation into Brazilian Portuguese (primary) and English (secondary), preserving meaning and safety.
3. Update the visible product name to PsicoIA only in presentation text, UI, and documentation.
4. Add isolated translation resources when necessary, without changing logic; any new mechanism requires explicit approval and tests.
5. Update branding/documentation links only to valid destination resources while preserving upstream references and academic citations.

## Prohibited within migration scope

- Change logic, control flow, behavior, APIs, schemas, signatures, dependencies, algorithms, or data.
- Rename modules, files, directories, classes, functions, variables, imports, routes, flags, environment variables, serialized keys, or model identifiers through a global name replacement.
- Fix bugs, modernize, reorganize, broadly reformat, or optimize code incidentally.
- Translate benchmarks, profiles, clinical instrument items, results, or other research data as part of migration.
- Replace behavior-sensitive prompts or retrieval text without specific approval and evaluation.

Technical identifiers containing `PsychAgent` remain unchanged whenever replacement could break compatibility or provenance. Any exception that changes code requires explicit authorization, a separate rationale, an isolated diff, and tests; it must not be described as a literal copy.

## Required process

1. Pin and record the source SHA before copying. Keep branch `original` as the upstream reference; do not edit its files.
2. Compare each migrated file with the recorded SHA. Every diff must fit one of the allowed categories above; functional differences block migration until reverted or separately approved.
3. For each localized Chinese string, preserve placeholders, markup, structure, functional punctuation, and identifiers; keep PT-BR and English versions aligned when both are in scope.
4. Separate migration, branding, and localization into distinct commits/reviews where practical. Do not mix an approved functional exception into the literal-copy commit.
5. Run relevant validation and record actual results. Passing tests do not prove complete equality; the diff against the upstream SHA is the evidence for code preservation.
6. Report untranslated files, pending decisions, exceptions, and limitations. Do not claim migration or localization is complete without a complete inventory.

## Relationship to other instructions

This policy implements the user's migration preference and complements `AGENTS.md`, `docs/ROADMAP.md`, and the `psicoia-migration-translation` skill. If instructions conflict, do not make an irreversible change: record the conflict and ask for clarification.
