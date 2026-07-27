# Locale routing and translation completeness

This directory defines the framework-independent i18n contract for issue #112.
The English Markdown catalog remains canonical. Portuguese and Spanish files
live in parallel trees and mirror the canonical relative path:

```text
funds/brazil/example.md
translations/pt-BR/funds/brazil/example.md
translations/es/funds/brazil/example.md
```

The parallel roots let the PT-BR and Spanish translation batches work without
editing shared profile files. A translation never changes the canonical path,
entity identity or slug.

## Public routes

Every localized route starts with exactly one configured segment:

- `/en/`
- `/pt-br/`
- `/es/`

The suffix after the locale segment is identical when a visitor changes
language. The GitHub Pages base is applied separately, so
`/pt-br/catalog/` becomes
`/awesome-latam-vc/pt-br/catalog/` in deployed links.

The unprefixed `/` page is the `x-default` language chooser. It must work
without JavaScript and must not redirect based on browser language.

An exact localized page has:

- `lang` equal to the configured `html_lang`;
- a self-referencing canonical URL;
- hreflang links only for variants that actually exist;
- the same entity slug in every available locale.

During migration, a missing translation may display the English canonical
content at the requested route only as an explicit fallback. Such a response
is `noindex`, canonicals to the English route and does not emit an hreflang for
the missing locale. Release mode forbids this fallback.

For localized home pages, `x-default` points to the unprefixed chooser. For
deeper content without its own language-neutral chooser, `x-default` points to
the English variant of the same route.

## Completeness modes

The validator has two modes:

- migration mode reports missing translations and `needs_review` as warnings;
- release mode treats either condition as an error.

Both modes reject duplicate or orphan translations, locale/path mismatches,
slug divergence, incorrect `translation_of` references and protected-field or
protected-token changes.

Run the migration gate:

```text
python tools/seo_geo/validate_i18n.py
```

Run the launch gate:

```text
python tools/seo_geo/validate_i18n.py --release
```

The launch gate is intentionally red until issues #117 and #118 complete the
catalog. CI uses migration mode until the launch gate is activated.
