import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative } from "node:path";

const root = process.cwd();
const astroCli = join(root, "node_modules", "astro", "bin", "astro.mjs");
const pagefindCli = join(
  root,
  "node_modules",
  "pagefind",
  "lib",
  "runner",
  "bin.cjs",
);
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
  execFileSync(process.execPath, [pagefindCli], {
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
const catalogHtml = readFileSync(join(dist, "catalog", "index.html"), "utf8");
const notFoundHtml = readFileSync(join(dist, "404.html"), "utf8");
const pagefindEntry = JSON.parse(
  readFileSync(join(dist, "pagefind", "pagefind-entry.json"), "utf8"),
);
const sourceProfileCount = profileRoots
  .flatMap((directory) => files(join(root, directory)))
  .filter(
    (path) =>
      path.endsWith(".md") &&
      !/^README(?:\.[^.]+)?\.md$/i.test(path.split(/[\\/]/).at(-1)),
  ).length;
const renderedProfileCount = (
  catalogHtml.match(/View canonical Markdown/g) ?? []
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
  productionHtml.includes('href="/awesome-latam-vc/catalog/"'),
  "internal links must include the GitHub Pages base path",
);
assert(
  catalogHtml.includes(
    '<link rel="canonical" href="https://djairofilho.github.io/awesome-latam-vc/catalog/">',
  ),
  "catalog canonical is missing or incorrect",
);
assert(
  renderedProfileCount === sourceProfileCount,
  `catalog rendered ${renderedProfileCount} of ${sourceProfileCount} canonical profiles`,
);
assert(
  sourceProfileCount === entityDocument.dataset.entity_count,
  "site profile count and structured export count differ",
);
assert(
  pagefindEntry.languages?.en?.hash,
  "Pagefind must emit a language-specific English index",
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
  !/(?:href|src)="\/(?!awesome-latam-vc\/)/.test(productionHtml),
  "root-relative asset or link escaped the configured base path",
);

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
console.log(
  `Verified ${sourceProfileCount} profiles and ${Object.keys(first).length} deterministic static files under /awesome-latam-vc/.`,
);
