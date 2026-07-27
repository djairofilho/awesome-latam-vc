import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import {
  hreflangUrls,
  localizedRoute,
  localeConfig,
  switchLocalizedRoute,
} from "../src/lib/i18n.mjs";
import { canonicalUrl, withBase } from "../src/lib/paths.mjs";

test("base-path helpers preserve the GitHub Pages subdirectory", () => {
  assert.equal(withBase("/"), "/awesome-latam-vc/");
  assert.equal(withBase("/catalog/"), "/awesome-latam-vc/catalog/");
  assert.equal(
    canonicalUrl("/catalog/"),
    "https://djairofilho.github.io/awesome-latam-vc/catalog/",
  );
});

test("locale routes preserve suffixes, canonicals and the Pages base", () => {
  assert.equal(
    localizedRoute("pt-BR", "/catalog/500-latam/"),
    "/pt-br/catalog/500-latam/",
  );
  assert.equal(
    switchLocalizedRoute("/pt-br/catalog/500-latam/", "es"),
    "/es/catalog/500-latam/",
  );
  assert.equal(
    canonicalUrl(localizedRoute("es", "/catalog/")),
    "https://djairofilho.github.io/awesome-latam-vc/es/catalog/",
  );
  assert.equal(localeConfig.site_base, "/awesome-latam-vc");
});

test("hreflang only advertises available variants and uses x-default safely", () => {
  assert.deepEqual(
    hreflangUrls("/catalog/example/", ["en", "pt-BR"]),
    {
      en: "https://djairofilho.github.io/awesome-latam-vc/en/catalog/example/",
      "pt-BR":
        "https://djairofilho.github.io/awesome-latam-vc/pt-br/catalog/example/",
      "x-default":
        "https://djairofilho.github.io/awesome-latam-vc/en/catalog/example/",
    },
  );
  assert.equal(
    hreflangUrls("/")["x-default"],
    "https://djairofilho.github.io/awesome-latam-vc/",
  );
});

test("interface labels are stored separately from profile content", () => {
  const catalog = readFileSync("src/i18n/ui.ts", "utf8");
  for (const locale of ["en", "pt-BR", "es"]) {
    assert.match(catalog, new RegExp(`(?:^|\\s)["']?${locale}["']?\\s*:`));
  }
  for (const phrase of ["Escolher idioma", "Elegir idioma", "Choose language"]) {
    assert.match(catalog, new RegExp(phrase));
  }
});

test("the content layer reads canonical profiles and mirrored translations", () => {
  const config = readFileSync("src/content.config.ts", "utf8");
  const contract = JSON.parse(
    readFileSync("research/seo-geo/contract/profile.schema.json", "utf8"),
  );
  for (const source of [
    "funds/**/*.md",
    "ecosystem/accelerators/**/*.md",
    "ecosystem/angel-networks/**/*.md",
    "ecosystem/funding-platforms/**/*.md",
    "ecosystem/public-programs/**/*.md",
    "translations/pt-BR/funds/**/*.md",
    "translations/pt-BR/ecosystem/accelerators/**/*.md",
    "translations/es/funds/**/*.md",
    "translations/es/ecosystem/accelerators/**/*.md",
  ]) {
    assert.match(config, new RegExp(source.replaceAll("*", "\\*")));
  }
  for (const field of contract.required) {
    assert.match(config, new RegExp(`\\b${field}:`), `missing ${field}`);
  }
  const catalog = readFileSync("src/lib/catalog.ts", "utf8");
  assert.match(catalog, /variants\.get\(locale\) \?\? variants\.get\("en"\)/);
});

test("editorial routes load validated content and expose available locales", () => {
  const config = readFileSync("src/content.config.ts", "utf8");
  assert.match(config, /research\/seo-geo\/content\/editorial/);
  assert.match(config, /editorialPages/);

  const route = readFileSync(
    "src/pages/[locale]/about/[slug].astro",
    "utf8",
  );
  assert.match(route, /getCollection\("editorialPages"\)/);
  assert.match(route, /availableLocales/);
  assert.match(route, /localizedRoute\(locale, routeSuffix\)/);
  assert.match(route, /View Markdown source|labels\.viewSource/);

  const layout = readFileSync("src/layouts/BaseLayout.astro", "utf8");
  const switcher = readFileSync(
    "src/components/LanguageSwitcher.astro",
    "utf8",
  );
  assert.match(layout, /hreflangUrls\(routeSuffix, availableLocales\)/);
  assert.match(switcher, /availableLocales\.includes\(locale\)/);
});

test("profile answer pattern keeps claims, observations and evidence separate", () => {
  const component = readFileSync("src/components/ProfileAnswer.astro", "utf8");
  const contract = JSON.parse(
    readFileSync(
      "research/seo-geo/content/profile-answer-contract.json",
      "utf8",
    ),
  );
  assert.deepEqual(contract.section_order, [
    "answer",
    "key_facts",
    "declared_thesis",
    "observed_signals",
    "sources",
    "verification",
  ]);
  assert.match(component, /slot name="declared-thesis"/);
  assert.match(component, /slot name="observed-signals"/);
  assert.match(component, /datetime=\{lastVerified\}/);
});

test("pull requests validate without deployment", () => {
  const workflow = readFileSync(".github/workflows/site-build.yml", "utf8");
  assert.match(workflow, /pull_request:/);
  assert.match(workflow, /npm run verify/);
  assert.doesNotMatch(workflow, /uses:\s+actions\/deploy-pages/);
  assert.match(workflow, /PUBLIC_SITE_ENV: preview/);
});

test("production deployment is restricted to main and github-pages", () => {
  const workflow = readFileSync(".github/workflows/deploy-pages.yml", "utf8");
  assert.match(workflow, /branches: \[main\]/);
  assert.match(workflow, /name: github-pages/);
  assert.match(workflow, /actions\/deploy-pages@v5/);
  assert.match(workflow, /PUBLIC_SITE_ENV: production/);
  assert.doesNotMatch(workflow, /pull_request:/);
});
