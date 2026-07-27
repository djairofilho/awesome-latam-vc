import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative } from "node:path";
import { canonicalUrl, SITE_BASE, SITE_ORIGIN } from "../src/lib/paths.mjs";

const root = process.cwd();
const dist = join(root, "dist");

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

function files(directory) {
  return readdirSync(directory).flatMap((name) => {
    const path = join(directory, name);
    return statSync(path).isDirectory() ? files(path) : [path];
  });
}

function routeForHtml(path) {
  const outputPath = relative(dist, path).replaceAll("\\", "/");
  if (outputPath === "index.html") {
    return "/";
  }
  if (outputPath.endsWith("/index.html")) {
    return `/${outputPath.slice(0, -"/index.html".length)}/`;
  }
  return outputPath === "404.html" ? "/404/" : `/${outputPath}`;
}

function matches(html, expression) {
  return [...html.matchAll(expression)];
}

function singleValue(html, expression, label, route) {
  const found = matches(html, expression);
  assert(found.length === 1, `${route} must contain exactly one ${label}`);
  return found[0][1];
}

function meta(html, attribute, key, route) {
  return singleValue(
    html,
    new RegExp(
      `<meta\\s+${attribute}="${key.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}"\\s+content="([^"]*)"\\s*\\/?>`,
      "g",
    ),
    `${key} meta tag`,
    route,
  );
}

function canonical(html, route) {
  return singleValue(
    html,
    /<link\s+rel="canonical"\s+href="([^"]+)"\s*\/?>/g,
    "canonical link",
    route,
  );
}

function outputForPath(pathname) {
  const relativePath = pathname.slice(SITE_BASE.length).replace(/^\/+/, "");
  if (!relativePath) {
    return join(dist, "index.html");
  }
  if (relativePath.endsWith("/")) {
    return join(dist, relativePath, "index.html");
  }
  return join(dist, relativePath);
}

const pages = files(dist)
  .filter((path) => path.endsWith(".html"))
  .map((path) => ({
    path,
    route: routeForHtml(path),
    html: readFileSync(path, "utf8"),
  }));
const indexable = pages.filter(
  ({ html }) => !/<meta\s+name="robots"\s+content="[^"]*noindex/i.test(html),
);

const titles = new Map();
const descriptions = new Map();
const canonicals = new Map();
const hreflangByCanonical = new Map();

for (const { route, html } of indexable) {
  const title = singleValue(html, /<title>([^<]+)<\/title>/g, "title", route);
  const description = meta(html, "name", "description", route);
  const canonicalUrlValue = canonical(html, route);
  assert(title.trim() === title && title.length >= 20 && title.length <= 70,
    `${route} title must be unique, trimmed and 20-70 characters`);
  assert(
    description.trim() === description &&
      description.length >= 50 &&
      description.length <= 170,
    `${route} description must be unique, trimmed and 50-170 characters`,
  );
  assert(
    canonicalUrlValue === canonicalUrl(route),
    `${route} canonical does not match its public URL`,
  );
  assert(!titles.has(title), `${route} duplicates title from ${titles.get(title)}`);
  assert(
    !descriptions.has(description),
    `${route} duplicates description from ${descriptions.get(description)}`,
  );
  assert(
    !canonicals.has(canonicalUrlValue),
    `${route} duplicates canonical from ${canonicals.get(canonicalUrlValue)}`,
  );
  titles.set(title, route);
  descriptions.set(description, route);
  canonicals.set(canonicalUrlValue, route);

  assert(meta(html, "property", "og:title", route) === title,
    `${route} Open Graph title diverges from the document title`);
  assert(meta(html, "property", "og:description", route) === description,
    `${route} Open Graph description diverges from meta description`);
  assert(meta(html, "property", "og:url", route) === canonicalUrlValue,
    `${route} Open Graph URL diverges from canonical`);
  assert(meta(html, "property", "og:type", route) === "website",
    `${route} Open Graph type must be website`);
  assert(meta(html, "name", "twitter:card", route) === "summary",
    `${route} Twitter card must be summary`);
  assert(meta(html, "name", "twitter:title", route) === title,
    `${route} Twitter title diverges from the document title`);
  assert(meta(html, "name", "twitter:description", route) === description,
    `${route} Twitter description diverges from meta description`);
  meta(html, "property", "og:locale", route);

  const alternates = matches(
    html,
    /<link\s+rel="alternate"\s+hreflang="([^"]+)"\s+href="([^"]+)"\s*\/?>/g,
  );
  assert(
    alternates.length >= 2 && alternates.length <= 4,
    `${route} must expose its available locales and x-default hreflang`,
  );
  assert(
    new Set(alternates.map(([, hreflang]) => hreflang)).size ===
      alternates.length,
    `${route} contains duplicate hreflang values`,
  );
  assert(
    alternates.every(([, hreflang]) =>
      ["en", "pt-BR", "es", "x-default"].includes(hreflang),
    ),
    `${route} contains an unsupported hreflang value`,
  );
  assert(alternates.some(([, lang]) => lang === "x-default"),
    `${route} is missing x-default hreflang`);
  for (const [, hreflang, href] of alternates) {
    assert(href.startsWith(`${SITE_ORIGIN}${SITE_BASE}/`),
      `${route} has a non-public ${hreflang} alternate`);
  }
  hreflangByCanonical.set(
    canonicalUrlValue,
    Object.fromEntries(
      alternates.map(([, hreflang, href]) => [hreflang, href]),
    ),
  );
}

for (const [canonicalUrlValue, alternates] of hreflangByCanonical) {
  assert(
    Object.values(alternates).includes(canonicalUrlValue),
    `${canonicalUrlValue} has no self-referencing hreflang`,
  );
  for (const alternateUrl of new Set(Object.values(alternates))) {
    const reciprocal = hreflangByCanonical.get(alternateUrl);
    assert(reciprocal, `${canonicalUrlValue} advertises a non-indexable alternate`);
    assert(
      JSON.stringify(reciprocal) === JSON.stringify(alternates),
      `${canonicalUrlValue} has a non-reciprocal hreflang cluster`,
    );
  }
}

const sitemap = readFileSync(join(dist, "sitemap.xml"), "utf8");
const sitemapUrls = matches(sitemap, /<loc>([^<]+)<\/loc>/g).map((match) => match[1]);
assert(
  sitemapUrls.length === new Set(sitemapUrls).size,
  "sitemap contains duplicate URLs",
);
assert(
  JSON.stringify([...sitemapUrls].sort()) ===
    JSON.stringify([...canonicals.keys()].sort()),
  "sitemap URLs do not exactly match indexable canonical pages",
);
for (const url of sitemapUrls) {
  const parsed = new URL(url);
  assert(!parsed.search && !parsed.hash, `sitemap URL has filter state: ${url}`);
  const output = outputForPath(parsed.pathname);
  assert(statSync(output).isFile(), `sitemap URL has no generated output: ${url}`);
}

const robots = readFileSync(join(dist, "robots.txt"), "utf8");
assert(
  robots ===
    `User-agent: *\nAllow: /\n\nSitemap: ${canonicalUrl("/sitemap.xml")}\n`,
  "robots.txt does not match the production crawling policy",
);

const notFound = pages.find(({ route }) => route === "/404/");
assert(notFound, "custom 404 output is missing");
assert(/name="robots"\s+content="noindex, nofollow"/.test(notFound.html),
  "custom 404 must be noindex");
assert(!/rel="canonical"/.test(notFound.html),
  "custom 404 must not claim a canonical URL");

for (const { route, html } of pages) {
  const hrefs = matches(html, /href="([^"]+)"/g).map((match) => match[1]);
  for (const href of hrefs) {
    if (href.startsWith("#")) {
      assert(
        html.includes(`id="${href.slice(1)}"`),
        `${route} links to missing fragment ${href}`,
      );
      continue;
    }
    const parsed = new URL(href, `${SITE_ORIGIN}${SITE_BASE}${route}`);
    if (parsed.origin !== SITE_ORIGIN || !parsed.pathname.startsWith(SITE_BASE)) {
      continue;
    }
    assert(
      statSync(outputForPath(parsed.pathname)).isFile(),
      `${route} links to missing generated URL ${parsed.pathname}`,
    );
  }
}

console.log(
  `SEO audit passed for ${indexable.length} indexable pages and ${sitemapUrls.length} sitemap URLs.`,
);
