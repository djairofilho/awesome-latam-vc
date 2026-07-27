---
{
  "schema_version": "1.0",
  "id": "editorial:methodology:en",
  "slug": "methodology",
  "locale": "en",
  "translation_of": null,
  "translation_status": "canonical",
  "title": "Methodology",
  "summary": "How Awesome LatAm VC turns source-backed Markdown profiles into a structured, auditable directory.",
  "last_reviewed": "2026-07-27",
  "references": [
    {
      "title": "Canonical metadata and translation contract",
      "url": "https://github.com/djairofilho/awesome-latam-vc/blob/main/research/seo-geo/contract/README.md"
    }
  ]
}
---
# Methodology

Awesome LatAm VC publishes structured views of the repository's canonical
Markdown profiles. The build reads each profile in place, uses its validated
front matter for normalized facts and keeps its cited prose as the editorial
record. The site does not create facts that are absent from those files.

## How the directory is built

Each entity has a stable identifier and slug. Metadata records entity type,
geography, stages, focuses, URLs, sources and a verification date. The Markdown
body provides the factual context behind those fields. Git history preserves
reviewable changes.

## What the data means

Normalized values support navigation and comparison; they do not replace an
entity's own language. A declared thesis remains separate from portfolio or
activity observations. An explicit absence value means the information was not
publicly disclosed in the recorded evidence, not that the project estimated it.

## Quality controls

Schemas reject invalid identities and enums. Collection checks reject duplicate
profiles, broken translation relationships and protected-field divergence.
Build checks ensure every discovered canonical profile is rendered.

## References

- [Canonical metadata and translation contract](https://github.com/djairofilho/awesome-latam-vc/blob/main/research/seo-geo/contract/README.md)
