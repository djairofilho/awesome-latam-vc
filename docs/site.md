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

## Validation

```text
npm run verify
```

The command checks TypeScript and Astro templates, runs unit tests, builds
production twice to detect nondeterminism, verifies canonical and base-prefixed
URLs, confirms that preview output contains `noindex`, and audits the generated
HTML for document and accessibility errors.

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
