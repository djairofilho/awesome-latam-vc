# Catalog metadata migration plan

## Scope

- issue: #110;
- parent epic: #107;
- source contract: issue #109;
- locale created in this issue: English (`en`) only;
- discovery: every individual profile under `funds/` and `ecosystem/`.

Directory indexes and future translated profiles are outside this migration.

## Deterministic mapping

1. Derive `entity_type` from the canonical catalog directory.
2. Derive the stable slug from the existing filename.
3. Preserve the exact visible H1 as `name`.
4. Normalize visible geography, stage and focus values to closed contract
   values.
5. Copy website, founder route, source links and verification date from the
   visible body.
6. Use `null`, `not_disclosed`, `not_applicable` or `NOT_DISCLOSED` when the
   profile explicitly lacks a value.
7. Record every absence or non-normalizable region in the mapping report.
8. Prepend JSON front matter without changing the normalized Markdown body.

## Commit boundaries

The contract adaptation, validator and migration tool form the first atomic
commit. Migrated profiles and their frozen inventory, mapping and hashes form a
second atomic commit.

## Gates

- full catalog coverage;
- unique IDs and slugs;
- valid entity types and normalized enums;
- no orphan or duplicate profile;
- exact visible source and verification-date preservation;
- identical body hashes before and after;
- deterministic generator and frozen hashes;
- current indexes remain valid and equivalent;
- no Portuguese or Spanish translation is created.
