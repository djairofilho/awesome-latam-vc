import {
  hreflangUrls,
  localeDetails,
  locales,
  localizedRoute,
} from "./i18n.mjs";
import { canonicalUrl } from "./paths.mjs";

export const SITEMAP_PATH = "/sitemap.xml";

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
  return ["/", "/catalog/"].map((suffix) => {
    const alternates = hreflangUrls(suffix);
    const paths = locales.map((locale) => localizedRoute(locale, suffix));
    if (suffix === "/") {
      paths.unshift("/");
    }
    return {
      suffix,
      paths,
      alternates,
    };
  });
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

export function sitemapXml() {
  const entries = indexableRouteGroups().flatMap(({ paths, alternates }) =>
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
