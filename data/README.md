# Structured catalog exports

The files in this directory expose the canonical catalog metadata under the
[CC0 1.0 Universal public-domain dedication](https://creativecommons.org/publicdomain/zero/1.0/).
They are generated only from the JSON front matter of canonical Markdown
profiles under `funds/` and `ecosystem/`.

## Files

- `entities.json`: versioned dataset document validated by
  `entities.schema.json`.
- `entities.csv`: the same entities and ID order in RFC 4180-compatible CSV.
- `entities.schema.json`: JSON Schema Draft 2020-12 contract.

Both exports use UTF-8 without a byte-order mark and LF line endings. Rows and
entities are sorted by stable `entity_type:slug` IDs. Dataset version and date
are frozen to `2026-07-27`; every entity also carries its profile
`verified_on` date and official source records.

## Empty and compound values

- A JSON `null` in `operator`, `official_website`, or `founder_route` becomes an
  empty CSV cell. Empty cells never mean an inferred value.
- Arrays and source objects are stored in CSV cells as compact JSON. Consumers
  should JSON-decode `aliases`, `countries_covered`, `stages`, `focuses`, and
  `sources`.
- Empty arrays are encoded as `[]`, not as empty cells.
- Enum values are exported unchanged from the metadata contract.

## Reproduction and compatibility

```text
python tools/seo_geo/generate_entities.py
python tools/seo_geo/generate_entities.py --check
python -m unittest discover -s tools/seo_geo/tests -v
```

Adding a field is a schema change. Consumers should reject unknown
`schema_version` values and may use the dataset date as a snapshot version.
The generator validates all source profiles before writing either format.

The static site publishes the committed bytes at `/data/entities.json` and
`/data/entities.csv` under its configured base path. Its `Dataset` JSON-LD
points to those downloads and carries the same version, date, and CC0 license.
