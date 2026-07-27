# Static site development and deployment

The Astro site reads canonical Markdown profiles in place from `funds/` and
`ecosystem/`. It does not copy, move or rewrite catalog content.

## Local development

Use Node.js 22.12 or newer:

```text
npm ci
npm run dev
```

Astro serves the project with the production base path
`/awesome-latam-vc/`. Internal links must use the shared base-path helper
instead of hard-coded root-relative URLs.

## Locale routes

The language-neutral root `/` is an `x-default` language chooser. It never
redirects based on browser language. Published interfaces live at `/en/`,
`/pt-br/` and `/es/`; switching language preserves the route suffix and entity.

Canonical profiles remain in `funds/` and `ecosystem/`. Portuguese and Spanish
translations mirror those paths below `translations/pt-BR/` and
`translations/es/`. During migration, a missing translation falls back to the
English profile; the i18n validator reports it as a warning. Release validation
requires every profile in all three locales.

Every localized page must set its matching HTML `lang`, canonical URL and
available `hreflang` alternatives. A fallback profile must be `noindex`, use
the English canonical and omit unavailable locale alternatives.

## Technical SEO policy

The generated `/sitemap.xml` contains only canonical, indexable HTML routes.
It excludes the `/catalog/` compatibility alias, the 404 document, preview
builds, query-string filter states and data downloads. `/robots.txt` allows
crawling and advertises the absolute production sitemap URL.

Every indexable page must have one unique title and description, one
self-referencing absolute canonical, reciprocal locale alternatives, and
matching Open Graph and Twitter metadata. Visible breadcrumbs and their
`BreadcrumbList` JSON-LD must describe the same hierarchy.

GitHub Markdown remains the source record and is linked as evidence; it is not
declared as the canonical URL of a site page. Filter combinations do not create
indexable URLs. Compatibility or duplicate HTML routes are `noindex` and point
to the selected canonical.

Entity IDs and slugs stay stable across languages. If a slug must change, add a
static compatibility page at the old route with `noindex` and a canonical link
to the new route, then update locale switching, breadcrumbs and the sitemap in
the same change. GitHub Pages cannot provide arbitrary server-side redirects,
so an old URL must never silently become a 404 during an intentional rename.

## Validation

```text
npm run verify
```

The command checks TypeScript and Astro templates, runs unit tests, builds
production twice to detect nondeterminism, verifies canonical and base-prefixed
URLs, confirms that preview output contains `noindex`, and audits the generated
HTML for document and accessibility errors. It also compares every indexable
page with the sitemap, checks social metadata and reciprocal alternatives,
smokes generated links, and starts a local preview to verify public URL status
codes plus the custom 404 response.

## GitHub Pages deployment

Pull requests run `.github/workflows/site-build.yml`. They validate preview
output but never call the Pages deployment action.

Pushes to `main` run `.github/workflows/deploy-pages.yml`. The build job must
finish before the deploy job can publish to the protected `github-pages`
environment. The repository Pages source must be set to **GitHub Actions**.

Production configuration:

- Site origin: `https://djairofilho.github.io`
- Base path: `/awesome-latam-vc`
- Public URL: `https://djairofilho.github.io/awesome-latam-vc/`
- Output: static files in `dist/`

After the first successful deployment, verify the public URL and set it as the
repository homepage. Do not set the homepage before a production deployment
responds successfully.

## Deployment diagnosis

If a deployment fails:

1. Inspect the build job before the deploy job.
2. Reproduce it with `npm ci && npm run verify`.
3. Confirm that repository Pages uses GitHub Actions.
4. Confirm that the `github-pages` environment permits the `main` branch.
5. Check generated links for the `/awesome-latam-vc/` prefix.
