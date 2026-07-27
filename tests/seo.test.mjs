import assert from "node:assert/strict";
import test from "node:test";
import {
  indexablePaths,
  indexableRouteGroups,
  robotsText,
  sitemapXml,
  socialLocale,
} from "../src/lib/seo.mjs";

test("indexable route inventory excludes aliases, filters and errors", () => {
  assert.deepEqual(indexablePaths(), [
    "/",
    "/en/",
    "/pt-br/",
    "/es/",
    "/en/catalog/",
    "/pt-br/catalog/",
    "/es/catalog/",
  ]);
  for (const path of indexablePaths()) {
    assert.doesNotMatch(path, /[?#]/);
  }
  assert.doesNotMatch(indexablePaths().join("\n"), /(?:^|\n)\/catalog\/|404/);
});

test("sitemap is multilingual, absolute and deterministic", () => {
  const first = sitemapXml();
  const second = sitemapXml();
  assert.equal(first, second);
  assert.match(first, /xmlns:xhtml="http:\/\/www\.w3\.org\/1999\/xhtml"/);
  assert.equal((first.match(/<loc>/g) ?? []).length, 7);
  for (const path of indexablePaths()) {
    assert.match(
      first,
      new RegExp(
        `<loc>https://djairofilho\\.github\\.io/awesome-latam-vc${path.replaceAll("/", "\\/")}</loc>`,
      ),
    );
  }
  for (const group of indexableRouteGroups()) {
    for (const hreflang of ["en", "pt-BR", "es", "x-default"]) {
      assert.ok(group.alternates[hreflang]);
    }
  }
});

test("robots advertises the only public sitemap", () => {
  assert.equal(
    robotsText(),
    [
      "User-agent: *",
      "Allow: /",
      "",
      "Sitemap: https://djairofilho.github.io/awesome-latam-vc/sitemap.xml",
      "",
    ].join("\n"),
  );
});

test("Open Graph locales use regional forms", () => {
  assert.equal(socialLocale("en"), "en_US");
  assert.equal(socialLocale("pt-BR"), "pt_BR");
  assert.equal(socialLocale("es"), "es_419");
  assert.throws(() => socialLocale("fr"), /Unsupported social locale/);
});
