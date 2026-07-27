import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative } from "node:path";

const root = process.cwd();
const astroCli = join(root, "node_modules", "astro", "bin", "astro.mjs");
const seoAudit = join(root, "scripts", "verify-seo.mjs");
const siteSmoke = join(root, "scripts", "smoke-site.mjs");
const dist = join(root, "dist");
const profileRoots = [
  "funds",
  "ecosystem/accelerators",
  "ecosystem/angel-networks",
  "ecosystem/funding-platforms",
  "ecosystem/public-programs",
];

function build(environment) {
  execFileSync(process.execPath, [astroCli, "build"], {
    cwd: root,
    env: { ...process.env, PUBLIC_SITE_ENV: environment },
    stdio: "inherit",
  });
}

function files(directory) {
  return readdirSync(directory)
    .flatMap((name) => {
      const path = join(directory, name);
      return statSync(path).isDirectory() ? files(path) : [path];
    })
    .sort();
}

function snapshot() {
  return Object.fromEntries(
    files(dist).map((path) => [
      relative(dist, path).replaceAll("\\", "/"),
      createHash("sha256").update(readFileSync(path)).digest("hex"),
    ]),
  );
}

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

function indexHtml() {
  return readFileSync(join(dist, "index.html"), "utf8");
}

function routeHtml(...segments) {
  return readFileSync(join(dist, ...segments, "index.html"), "utf8");
}

function jsonLd(html) {
  const matches = [
    ...html.matchAll(
      /<script type="application\/ld\+json">([\s\S]*?)<\/script>/g,
    ),
  ];
  assert(matches.length === 1, "page must contain exactly one JSON-LD block");
  return JSON.parse(matches[0][1]);
}

build("production");
const first = snapshot();
const productionHtml = indexHtml();
const compatibilityCatalogHtml = routeHtml("catalog");
const notFoundHtml = readFileSync(join(dist, "404.html"), "utf8");
const localeRoutes = {
  en: "en",
  "pt-BR": "pt-br",
  es: "es",
};
const localizedHomeHtml = Object.fromEntries(
  Object.entries(localeRoutes).map(([locale, segment]) => [
    locale,
    routeHtml(segment),
  ]),
);
const localizedCatalogHtml = Object.fromEntries(
  Object.entries(localeRoutes).map(([locale, segment]) => [
    locale,
    routeHtml(segment, "catalog"),
  ]),
);
const catalogHtml = localizedCatalogHtml.en;
const editorialSourceRoot = join(
  root,
  "research",
  "seo-geo",
  "content",
  "editorial",
);
const editorialSources = files(editorialSourceRoot).filter((path) =>
  path.endsWith(".md"),
);
const sourceProfileCount = profileRoots
  .flatMap((directory) => files(join(root, directory)))
  .filter(
    (path) =>
      path.endsWith(".md") &&
      !/^README(?:\.[^.]+)?\.md$/i.test(path.split(/[\\/]/).at(-1)),
  ).length;
const entityDocument = JSON.parse(
  readFileSync(join(root, "data", "entities.json"), "utf8"),
);
const websiteGraph = jsonLd(productionHtml);
const catalogGraph = jsonLd(catalogHtml);
const catalogTypes = catalogGraph["@graph"].map((node) => node["@type"]);
const expectedOrganizationCount = entityDocument.entities.filter(
  (entity) => entity.entity_type !== "public_program",
).length;
const expectedGovernmentOrganizationCount = entityDocument.entities.filter(
  (entity) =>
    entity.entity_type === "public_program" && entity.operator === null,
).length;
const organizationNodes = catalogGraph["@graph"].filter((node) =>
  ["Organization", "GovernmentOrganization"].includes(node["@type"]),
);
assert(
  productionHtml.includes(
    '<link rel="canonical" href="https://djairofilho.github.io/awesome-latam-vc/">',
  ),
  "production canonical is missing or incorrect",
);
assert(
  !productionHtml.includes('name="robots" content="noindex'),
  "production output must remain indexable",
);
assert(
  !/(?:window\.location|location\.replace|http-equiv="refresh")/i.test(
    productionHtml,
  ),
  "the x-default root must not redirect automatically",
);
assert(
  productionHtml.includes(
    '<link rel="alternate" hreflang="x-default" href="https://djairofilho.github.io/awesome-latam-vc/">',
  ),
  "the root must advertise its x-default URL",
);
assert(
  compatibilityCatalogHtml.includes(
    '<link rel="canonical" href="https://djairofilho.github.io/awesome-latam-vc/en/catalog/">',
  ) &&
    compatibilityCatalogHtml.includes(
      'name="robots" content="noindex, nofollow"',
    ),
  "the compatibility catalog route must canonicalize to English and remain noindex",
);
for (const [locale, segment] of Object.entries(localeRoutes)) {
  const home = localizedHomeHtml[locale];
  const catalog = localizedCatalogHtml[locale];
  assert(
    home.includes(`<html lang="${locale}">`),
    `${locale} home has an incorrect lang attribute`,
  );
  assert(
    home.includes(
      `<link rel="canonical" href="https://djairofilho.github.io/awesome-latam-vc/${segment}/">`,
    ),
    `${locale} home canonical is missing or incorrect`,
  );
  assert(
    catalog.includes(
      `<link rel="canonical" href="https://djairofilho.github.io/awesome-latam-vc/${segment}/catalog/">`,
    ),
    `${locale} catalog canonical is missing or incorrect`,
  );
  for (const targetSegment of Object.values(localeRoutes)) {
    assert(
      catalog.includes(
        `href="/awesome-latam-vc/${targetSegment}/catalog/"`,
      ),
      `${locale} catalog language switcher lost the catalog suffix`,
    );
  }
  const renderedProfileCount = (
    catalog.match(/data-profile-id=/g) ?? []
  ).length;
  assert(
    renderedProfileCount === sourceProfileCount,
    `${locale} catalog rendered ${renderedProfileCount} of ${sourceProfileCount} canonical profiles`,
  );
  assert(
    !/(?:href|src)="\/(?!awesome-latam-vc\/)/.test(home + catalog),
    `${locale} output contains a root-relative link outside the Pages base`,
  );
}
for (const sourcePath of editorialSources) {
  const locale = sourcePath.split(/[\\/]/).at(-2);
  const segment = localeRoutes[locale];
  const slug = sourcePath.split(/[\\/]/).at(-1).replace(/\.md$/, "");
  const html = routeHtml(segment, "about", slug);
  const route = `/${segment}/about/${slug}/`;
  assert(
    html.includes(`<html lang="${locale}">`),
    `${locale} editorial page has an incorrect lang attribute`,
  );
  assert(
    html.includes(
      `<link rel="canonical" href="https://djairofilho.github.io/awesome-latam-vc${route}">`,
    ),
    `${locale}:${slug} editorial canonical is missing or incorrect`,
  );
  assert(
    html.includes(
      "https://github.com/djairofilho/awesome-latam-vc/blob/main/research/seo-geo/content/editorial/",
    ),
    `${locale}:${slug} editorial page does not expose its Markdown source`,
  );
  for (const [targetLocale, targetSegment] of Object.entries(localeRoutes)) {
    const variantExists = editorialSources.some(
      (candidate) =>
        candidate.split(/[\\/]/).at(-2) === targetLocale &&
        candidate.split(/[\\/]/).at(-1) === `${slug}.md`,
    );
    assert(
      html.includes(
        `href="/awesome-latam-vc/${targetSegment}/about/${slug}/"`,
      ) === variantExists,
      `${locale}:${slug} language switcher does not match available variants`,
    );
  }
  assert(
    !/(?:href|src)="\/(?!awesome-latam-vc\/)/.test(html),
    `${locale}:${slug} contains a root-relative link outside the Pages base`,
  );
}
assert(
  sourceProfileCount === entityDocument.dataset.entity_count,
  "site profile count and structured export count differ",
);
assert(
  JSON.stringify(websiteGraph["@graph"].map((node) => node["@type"])) ===
    JSON.stringify(["WebSite"]),
  "home JSON-LD must contain one WebSite node",
);
assert(
  catalogTypes.includes("Dataset") &&
    catalogTypes.includes("BreadcrumbList") &&
    catalogTypes.includes("Organization") &&
    catalogTypes.includes("GovernmentOrganization"),
  "catalog JSON-LD is missing a required semantic type",
);
assert(
  catalogTypes.every((type) =>
    [
      "Dataset",
      "BreadcrumbList",
      "Organization",
      "GovernmentOrganization",
    ].includes(type),
  ),
  "catalog JSON-LD contains an unsupported top-level type",
);
assert(
  catalogTypes.filter((type) => type === "Organization").length ===
    expectedOrganizationCount &&
    catalogTypes.filter((type) => type === "GovernmentOrganization").length ===
      expectedGovernmentOrganizationCount,
  "organization JSON-LD counts diverge from canonical entity semantics",
);
assert(
  new Set(organizationNodes.map((node) => node["@id"])).size ===
    organizationNodes.length,
  "organization JSON-LD contains duplicate identifiers",
);
const datasetNode = catalogGraph["@graph"].find(
  (node) => node["@type"] === "Dataset",
);
assert(
  datasetNode.variableMeasured?.value === entityDocument.dataset.entity_count &&
    datasetNode.version === entityDocument.dataset.version &&
    datasetNode.dateModified === entityDocument.dataset.date &&
    datasetNode.license === entityDocument.dataset.license_url,
  "Dataset JSON-LD diverges from the structured export metadata",
);
assert(
  readFileSync(join(dist, "data", "entities.json")).equals(
    readFileSync(join(root, "data", "entities.json")),
  ) &&
    readFileSync(join(dist, "data", "entities.csv")).equals(
      readFileSync(join(root, "data", "entities.csv")),
    ),
  "published dataset downloads differ from committed exports",
);
assert(
  notFoundHtml.includes('name="robots" content="noindex, nofollow"'),
  "the 404 page must remain noindex in production",
);
assert(
  !/(?:href|src)="\/(?!awesome-latam-vc\/)/.test(
    productionHtml + compatibilityCatalogHtml,
  ),
  "root-relative asset or link escaped the configured base path",
);
execFileSync(process.execPath, [seoAudit], {
  cwd: root,
  stdio: "inherit",
});

build("production");
const second = snapshot();
assert(
  JSON.stringify(first) === JSON.stringify(second),
  "two clean production builds produced different files",
);

build("preview");
assert(
  indexHtml().includes('name="robots" content="noindex, nofollow"'),
  "preview output must include noindex",
);

build("production");
execFileSync(process.execPath, [siteSmoke], {
  cwd: root,
  stdio: "inherit",
});
console.log(
  `Verified ${sourceProfileCount} profiles and ${Object.keys(first).length} deterministic static files under /awesome-latam-vc/.`,
);
