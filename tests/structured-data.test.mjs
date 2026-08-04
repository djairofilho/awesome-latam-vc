import assert from "node:assert/strict";
import test from "node:test";
import {
  breadcrumbListJsonLd,
  datasetJsonLd,
  jsonLdDocument,
  organizationJsonLd,
  serializeJsonLd,
  webSiteJsonLd,
} from "../src/lib/structured-data.mjs";

test("website and dataset use canonical GitHub Pages URLs", () => {
  const website = webSiteJsonLd();
  const dataset = datasetJsonLd(229);

  assert.equal(website["@type"], "WebSite");
  assert.equal(
    website.url,
    "https://djairofilho.github.io/awesome-latam-vc/",
  );
  assert.equal(dataset["@type"], "Dataset");
  assert.deepEqual(dataset.variableMeasured, {
    "@type": "PropertyValue",
    name: "Entity count",
    value: 229,
  });
  assert.equal(dataset.version, "2026-08-04");
  assert.equal(dataset.dateModified, "2026-08-04");
  assert.equal(
    dataset.license,
    "https://creativecommons.org/publicdomain/zero/1.0/",
  );
  assert.deepEqual(
    dataset.distribution.map((item) => item.contentUrl),
    [
      "https://djairofilho.github.io/awesome-latam-vc/data/entities.json",
      "https://djairofilho.github.io/awesome-latam-vc/data/entities.csv",
    ],
  );
});

test("breadcrumbs preserve visible page hierarchy", () => {
  const breadcrumbs = breadcrumbListJsonLd([
    { name: "Overview", path: "/" },
    { name: "Catalog", path: "/catalog/" },
  ]);

  assert.equal(breadcrumbs["@type"], "BreadcrumbList");
  assert.deepEqual(
    breadcrumbs.itemListElement.map(({ position, name }) => ({
      position,
      name,
    })),
    [
      { position: 1, name: "Overview" },
      { position: 2, name: "Catalog" },
    ],
  );
});

test("organization types follow canonical profile semantics", () => {
  const shared = {
    name: "Example",
    summary: "Example summary.",
    sourceUrl: "https://github.com/example/profile.md",
    officialWebsite: null,
  };
  assert.equal(
    organizationJsonLd({ ...shared, category: "fund" })["@type"],
    "Organization",
  );
  assert.equal(
    organizationJsonLd({
      ...shared,
      category: "public_program",
      operator: null,
    })["@type"],
    "GovernmentOrganization",
  );
  assert.equal(
    organizationJsonLd({
      ...shared,
      category: "public_program",
      operator: "Example agency",
    }),
    null,
  );
});

test("JSON-LD graph rejects HTML breakouts during serialization", () => {
  const document = jsonLdDocument([{ "@type": "WebSite" }]);
  assert.equal(document["@context"], "https://schema.org");
  assert.deepEqual(document["@graph"], [{ "@type": "WebSite" }]);

  const serialized = serializeJsonLd([
    { "@type": "Organization", name: "</script><script>" },
  ]);
  assert.doesNotMatch(serialized, /</);
  assert.equal(
    JSON.parse(serialized)["@graph"][0].name,
    "</script><script>",
  );
});
