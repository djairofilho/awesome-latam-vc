# Canonical catalog metadata migration

Issue #110 added canonical English front matter to every individual Markdown
profile present at the execution cutoff.

## Before / after

- profiles: 205 before, 205 after;
- profiles with front matter: 0 before, 205 after;
- visible sources: 447 before and after;
- Markdown body hash mismatches: 0.

Missing or non-normalizable values remain explicit in `mapping.jsonl`; no
website, founder route, geography, stage, focus or operator was inferred from a
portfolio observation.

## Reproduction

```text
python tools/seo_geo/migrate_catalog.py
python tools/seo_geo/migrate_catalog.py --check
python tools/seo_geo/validate_profiles.py --catalog
```
