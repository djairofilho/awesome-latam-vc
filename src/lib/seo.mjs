import {
  existsSync,
  readdirSync,
  readFileSync,
  statSync,
} from "node:fs";
import { join, resolve } from "node:path";
import {
  hreflangUrls,
  localeDetails,
  locales,
  localizedRoute,
} from "./i18n.mjs";
import { canonicalUrl } from "./paths.mjs";

export const SITEMAP_PATH = "/sitemap.xml";
const repositoryRoot = process.cwd();
const entityDocument = JSON.parse(
  readFileSync(resolve(repositoryRoot, "data", "entities.json"), "utf8"),
);

function structuredMetadata(sourcePath) {
  const source = readFileSync(join(repositoryRoot, sourcePath), "utf8");
  const frontmatter = source.match(
    /^---\s*\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/,
  )?.[1];
  if (!frontmatter) {
    throw new Error(`Content has no structured frontmatter: ${sourcePath}`);
  }
  return JSON.parse(frontmatter);
}

function contentFiles(directory) {
  if (!existsSync(directory)) {
    return [];
  }
  return readdirSync(directory).flatMap((name) => {
    const path = join(directory, name);
    return statSync(path).isDirectory()
      ? contentFiles(path)
      : path.endsWith(".md")
        ? [path]
        : [];
  });
}

const socialLocales = Object.freeze({
  en: "en_US",
  "pt-BR": "pt_BR",
  es: "es_419",
});

export function socialLocale(locale = "en") {
  const value = socialLocales[locale];
  if (!value) {
    throw new Error(`Unsupported social locale: ${locale}`);
  }
  return value;
}

export function socialLocaleAlternates(locale) {
  return locales
    .filter((candidate) => candidate !== locale)
    .map(socialLocale);
}

export function indexableRouteGroups() {
  const sharedSuffixes = [
    "/",
    "/catalog/",
    ...[...new Set(
      entityDocument.entities.map(
        ({ entity_type }) => `/categories/${entity_type}/`,
      ),
    )].sort(),
    ...[...new Set(
      entityDocument.entities
        .flatMap((entity) => [
          entity.base_geography?.code,
          ...(entity.countries_covered ?? []),
        ])
        .filter((code) => /^[A-Z]{2}$/.test(code))
        .map((code) => `/countries/${code.toLowerCase()}/`),
    )].sort(),
  ];
  const sharedGroups = sharedSuffixes.map((suffix) => {
    const availableLocales = locales;
    const alternates = hreflangUrls(suffix, availableLocales);
    const paths = availableLocales.map((locale) =>
      localizedRoute(locale, suffix),
    );
    if (suffix === "/") {
      paths.unshift("/");
    }
    return {
      suffix,
      paths,
      alternates,
    };
  });
  const editorialPages = contentFiles(
    join(repositoryRoot, "research", "seo-geo", "content", "editorial"),
  ).map((path) =>
    structuredMetadata(path.slice(repositoryRoot.length + 1)),
  );
  const editorialGroups = [...new Set(editorialPages.map(({ slug }) => slug))]
    .sort()
    .map((slug) => {
      const suffix = `/about/${slug}/`;
      const availableLocales = locales.filter((locale) =>
        editorialPages.some(
          (page) => page.slug === slug && page.locale === locale,
        ),
      );
      return {
        suffix,
        paths: availableLocales.map((locale) =>
          localizedRoute(locale, suffix),
        ),
        alternates: hreflangUrls(suffix, availableLocales),
      };
    });
  const profileGroups = entityDocument.entities
    .map((entity) => {
      const slug = structuredMetadata(entity.source_profile).slug;
      const suffix = `/profiles/${slug}/`;
      const availableLocales = locales.filter((locale) => {
        if (locale === "en") {
          return true;
        }
        const contentRoot = localeDetails(locale).content_root;
        return Boolean(
          contentRoot &&
            existsSync(
              join(repositoryRoot, contentRoot, entity.source_profile),
            ),
        );
      });
      return {
        suffix,
        paths: availableLocales.map((locale) =>
          localizedRoute(locale, suffix),
        ),
        alternates: hreflangUrls(suffix, availableLocales),
      };
    })
    .sort(({ suffix: left }, { suffix: right }) =>
      left.localeCompare(right),
    );
  return [...sharedGroups, ...editorialGroups, ...profileGroups];
}

export function indexablePaths() {
  return indexableRouteGroups().flatMap(({ paths }) => paths);
}

function escapeXml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll('"', "&quot;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

export function sitemapXml(additionalRouteGroups = []) {
  const routeGroups = [
    ...indexableRouteGroups(),
    ...additionalRouteGroups,
  ];
  const entries = routeGroups.flatMap(({ paths, alternates }) =>
    paths.map((path) => {
      const links = Object.entries(alternates)
        .map(
          ([hreflang, href]) =>
            `    <xhtml:link rel="alternate" hreflang="${escapeXml(hreflang)}" href="${escapeXml(href)}" />`,
        )
        .join("\n");
      return [
        "  <url>",
        `    <loc>${escapeXml(canonicalUrl(path))}</loc>`,
        links,
        "  </url>",
      ].join("\n");
    }),
  );
  return [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">',
    ...entries,
    "</urlset>",
    "",
  ].join("\n");
}

export function robotsText() {
  return [
    "User-agent: *",
    "Allow: /",
    "",
    `Sitemap: ${canonicalUrl(SITEMAP_PATH)}`,
    "",
  ].join("\n");
}

export function localeMetadata(locale) {
  return {
    htmlLang: localeDetails(locale).html_lang,
    socialLocale: socialLocale(locale),
    socialLocaleAlternates: socialLocaleAlternates(locale),
  };
}

export function seoTitle(primary, qualifier = "") {
  const suffix = " | Awesome LatAm VC";
  const maximumPrimaryLength = 70 - suffix.length;
  const normalized = [primary, qualifier]
    .filter(Boolean)
    .join(" · ")
    .replace(/\s+/g, " ")
    .trim();
  const bounded =
    normalized.length > maximumPrimaryLength
      ? `${normalized.slice(0, maximumPrimaryLength - 1).trimEnd()}…`
      : normalized;
  return `${bounded}${suffix}`;
}

export function seoDescription(name, summary, fallback = "") {
  let normalized = `${name}. ${summary ?? ""}`.replace(/\s+/g, " ").trim();
  if (normalized.length < 50) {
    normalized = `${normalized} ${fallback}`.replace(/\s+/g, " ").trim();
  }
  if (normalized.length <= 170) {
    return normalized;
  }
  return `${normalized.slice(0, 169).trimEnd()}…`;
}
