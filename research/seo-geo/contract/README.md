# Canonical metadata and translation contract

This contract is the shared input for catalog migration, localized routes,
filters, structured data and dataset exports in epic #107. It does not replace
the Markdown profiles: front matter carries normalized facts and the Markdown
body carries localized editorial content.

## Files

- `profile.schema.json`: JSON Schema 2020-12 for one localized profile.
- `enums.json`: closed enums and the protected/localized field policy.
- `examples/valid/`: a fund in all three locales and one canonical example for
  each ecosystem category.
- `examples/invalid-cases.json`: executable invalid examples for duplicates,
  slugs, types, orphan translations and protected values.
- `tools/seo_geo/validate_profiles.py`: collection validator.

The front matter is a JSON object between Markdown `---` delimiters. JSON is a
valid YAML 1.2 subset, avoids parser-dependent scalar coercion and remains
directly consumable by Astro.

## Identity model

Identity and language are independent:

| Field | Scope | Example |
| --- | --- | --- |
| `entity_id` | Stable entity identity, shared by every locale | `fund:500-latam` |
| `id` | Unique localized profile identity | `fund:500-latam:pt-BR` |
| `slug` | Stable route segment, shared by every locale | `500-latam` |
| `locale` | Body and localized metadata language | `pt-BR` |
| `translation_of` | Exact English canonical profile ID | `fund:500-latam:en` |

The collection must contain exactly one English canonical profile per entity.
Its `translation_of` is `null` and its status is `canonical`. Portuguese and
Spanish profiles point directly to that canonical ID and use `complete` or
`needs_review`.

Duplicate `id` values and duplicate `(entity_id, locale)` pairs are errors.
`entity_id` must equal `entity_type:slug`; `id` must equal
`entity_id:locale`.

## Required metadata

Every localized profile provides:

- schema version, localized `id`, stable `entity_id` and `slug`;
- proper name, entity type and locale relationship;
- localized summary and translation status;
- aliases and operator;
- normalized base geography and countries covered;
- normalized stages and focuses;
- official website and optional founder route;
- titled sources, source kinds and URLs;
- verification date;
- explicit protected terms that must remain in the body.

Entity types are closed to:

- `fund`;
- `accelerator`;
- `angel_network`;
- `funding_platform`;
- `public_program`.

Stages, locales, source kinds and geography kinds are defined in `enums.json`.
Countries use ISO 3166-1 alpha-2 codes. `LATAM`, `CARIBBEAN` and `GLOBAL` are
the only region sentinels. Focus values use lowercase `snake_case`; they are
normalized filter keys and never replace the factual wording in the body.

## Translation rules

The canonical profile is the only authority for protected metadata.
Translations may localize:

- `summary`;
- headings, labels and navigation text;
- descriptions, declared theses and editorial explanations in the body.

Translations must preserve exactly:

- entity identity, slug, proper name, aliases and operator;
- entity type and all normalized factual classifications;
- official and founder URLs;
- source titles, URLs and kinds;
- verification date;
- protected proper terms and brands;
- Markdown link destinations and raw URLs in the body;
- inline and fenced code;
- numbers, percentages, dates, currency codes and currency symbols.

The validator compares protected front matter structurally and protected body
tokens as multisets. This permits natural sentence reordering while rejecting
changed facts. Official source titles remain unchanged even when surrounding
prose is localized. `Not publicly disclosed` may be translated in prose only
when its meaning is unchanged; normalized metadata continues to use the same
enum.

There is no automatic or deploy-time translation. A `needs_review` profile is
valid during migration but is not release-complete.

## How the site consumes profiles

For each `entity_id`, the build:

1. loads protected metadata exclusively from the English canonical profile;
2. verifies the requested locale points to that exact canonical profile;
3. combines canonical protected metadata with the locale's `summary` and
   Markdown body;
4. emits the same slug under `/en/`, `/pt-br/` and `/es/`;
5. uses normalized values for filters, JSON-LD and exports;
6. uses factual localized text for visible descriptions;
7. links back to the corresponding Markdown source and Git history.

The build must fail on a missing canonical, duplicate identity, protected-field
divergence or invalid enum. Release completeness may additionally require
`translation_status: complete` for PT-BR and ES.

## Validation

Install the pinned research dependencies, then run:

```text
python tools/seo_geo/validate_profiles.py research/seo-geo/contract/examples/valid
python -m unittest discover -s tools/seo_geo/tests -p "test_*.py"
```

The invalid examples are exercised by the test suite and document the expected
failure for every acceptance boundary.
