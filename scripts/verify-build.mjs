import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative } from "node:path";

const root = process.cwd();
const astroCli = join(root, "node_modules", "astro", "bin", "astro.mjs");
const dist = join(root, "dist");

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

build("production");
const first = snapshot();
const productionHtml = indexHtml();
const catalogHtml = readFileSync(join(dist, "catalog", "index.html"), "utf8");
const notFoundHtml = readFileSync(join(dist, "404.html"), "utf8");
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
  `Verified ${Object.keys(first).length} deterministic static files under /awesome-latam-vc/.`,
);
