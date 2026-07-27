import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { canonicalUrl, withBase } from "./paths.mjs";

const configPath = resolve(
  process.cwd(),
  "research",
  "seo-geo",
  "i18n",
  "locales.json",
);

export const localeConfig = JSON.parse(readFileSync(configPath, "utf8"));
export const canonicalLocale = localeConfig.canonical_locale;
export const locales = Object.freeze(Object.keys(localeConfig.locales));

export function localeDetails(locale) {
  const details = localeConfig.locales[locale];
  if (!details) {
    throw new Error(`Unsupported locale: ${locale}`);
  }
  return details;
}

export function normalizeRouteSuffix(suffix = "/") {
  if (suffix.includes("?") || suffix.includes("#")) {
    throw new Error("Localized route suffix cannot contain query or fragment");
  }
  const rawParts = suffix.replaceAll("\\", "/").split("/");
  if (rawParts.includes("..")) {
    throw new Error("Localized route suffix cannot traverse directories");
  }
  const cleaned = rawParts.filter(Boolean).join("/");
  return cleaned ? `/${cleaned}/` : "/";
}

export function localizedRoute(locale, suffix = "/") {
  const { route_segment: segment } = localeDetails(locale);
  const normalized = normalizeRouteSuffix(suffix);
  return normalized === "/" ? `/${segment}/` : `/${segment}${normalized}`;
}

export function localeFromSegment(segment) {
  return locales.find(
    (locale) => localeDetails(locale).route_segment === segment,
  );
}

export function switchLocalizedRoute(route, targetLocale) {
  const normalized = normalizeRouteSuffix(route);
  const prefix = locales
    .map((locale) => `/${localeDetails(locale).route_segment}/`)
    .find((candidate) => normalized.startsWith(candidate));
  if (!prefix) {
    throw new Error(`Route has no supported locale prefix: ${route}`);
  }
  return localizedRoute(targetLocale, normalized.slice(prefix.length));
}

export function localizedHref(locale, suffix = "/") {
  return withBase(localizedRoute(locale, suffix));
}

export function localizedCanonical(locale, suffix = "/") {
  return canonicalUrl(localizedRoute(locale, suffix));
}

export function hreflangUrls(suffix = "/", availableLocales = locales) {
  const unsupported = availableLocales.filter(
    (locale) => !locales.includes(locale),
  );
  if (unsupported.length) {
    throw new Error(`Unsupported hreflang locales: ${unsupported.join(", ")}`);
  }
  const normalized = normalizeRouteSuffix(suffix);
  const links = Object.fromEntries(
    locales
      .filter((locale) => availableLocales.includes(locale))
      .map((locale) => [
        localeDetails(locale).html_lang,
        localizedCanonical(locale, normalized),
      ]),
  );
  links["x-default"] = canonicalUrl(
    normalized === "/"
      ? localeConfig.x_default_path
      : localizedRoute(canonicalLocale, normalized),
  );
  return links;
}
