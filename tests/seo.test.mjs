import assert from "node:assert/strict";
import test from "node:test";
import {
  indexablePaths,
  indexableRouteGroups,
  robotsText,
  sitemapXml,
  socialLocale,
} from "../src/lib/seo.mjs";

test("indexable route inventory includes profiles and curated landings", () => {
  const paths = indexablePaths();
  assert.ok(paths.includes("/en/profiles/kaszek/"));
  assert.ok(paths.includes("/pt-br/categories/fund/"));
  assert.ok(paths.includes("/es/countries/br/"));
  assert.ok(paths.includes("/en/about/methodology/"));
  assert.ok(!paths.includes("/pt-br/about/methodology/"));
  for (const path of indexablePaths()) {
    assert.doesNotMatch(path, /[?#]/);
  }
  assert.doesNotMatch(
    indexablePaths().join("\n"),
    /(?:^|\n)\/catalog\/|404|\/stages\/|\/focuses\//,
  );
});

test("sitemap is multilingual, absolute and deterministic", () => {
  const first = sitemapXml();
  const second = sitemapXml();
  assert.equal(first, second);
  assert.match(first, /xmlns:xhtml="http:\/\/www\.w3\.org\/1999\/xhtml"/);
  assert.equal(
    (first.match(/<loc>/g) ?? []).length,
    indexablePaths().length,
  );
  for (const path of indexablePaths()) {
    assert.match(
      first,
      new RegExp(
        `<loc>https://djairofilho\\.github\\.io/awesome-latam-vc${path.replaceAll("/", "\\/")}</loc>`,
      ),
    );
  }
  for (const group of indexableRouteGroups()) {
    assert.ok(group.alternates.en);
    assert.ok(group.alternates["x-default"]);
    assert.equal(
      Object.keys(group.alternates).length,
      group.paths.length + (group.suffix === "/" ? 0 : 1),
    );
  }
});

test("sitemap includes editorial routes without inventing translations", () => {
  const suffix = "/about/methodology/";
  const editorialGroup = {
    suffix,
    paths: ["/en/about/methodology/"],
    alternates: {
      en: "https://djairofilho.github.io/awesome-latam-vc/en/about/methodology/",
      "x-default":
        "https://djairofilho.github.io/awesome-latam-vc/en/about/methodology/",
    },
  };
  const sitemap = sitemapXml([editorialGroup]);

  assert.match(
    sitemap,
    /<loc>https:\/\/djairofilho\.github\.io\/awesome-latam-vc\/en\/about\/methodology\/<\/loc>/,
  );
  assert.match(sitemap, /hreflang="en"/);
  assert.doesNotMatch(
    sitemap,
    /hreflang="(?:pt-BR|es)" href="[^"]*\/about\/methodology\/"/,
  );
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
