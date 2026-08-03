import { directoryRecord } from "./directory.mjs";
import { localizedHref } from "./i18n.mjs";

// Country landings describe the Latin American catalog, not every headquarters
// or global market mentioned by a multi-country profile.
const LATIN_AMERICA_COUNTRY_CODES = new Set([
  "AR",
  "BO",
  "BR",
  "CL",
  "CO",
  "CR",
  "CU",
  "DO",
  "EC",
  "GT",
  "HT",
  "HN",
  "MX",
  "NI",
  "PA",
  "PE",
  "PR",
  "PY",
  "SV",
  "UY",
  "VE",
]);

export function profileRouteSuffix(slug) {
  return `/profiles/${slug}/`;
}

export function categoryRouteSuffix(category) {
  return `/categories/${category}/`;
}

export function countryRouteSuffix(country) {
  return `/countries/${country.toLocaleLowerCase()}/`;
}

export function directoryRecordForProfile(profile, locale) {
  return {
    ...directoryRecord({
      id: profile.id,
      name: profile.name,
      summary: profile.summary,
      aliases: profile.aliases,
      operator: profile.operator,
      entity_type: profile.category,
      base_geography: profile.baseGeography,
      countries_covered: profile.countriesCovered,
      stages: profile.stages,
      focuses: profile.focuses,
    }),
    href: localizedHref(locale, profileRouteSuffix(profile.slug)),
  };
}

export function directoryCountryCodes(records) {
  return [
    ...new Set(
      records.flatMap(({ geography }) =>
        geography.filter((value) => LATIN_AMERICA_COUNTRY_CODES.has(value)),
      ),
    ),
  ].sort();
}

export function countryDisplayName(locale, country) {
  return (
    new Intl.DisplayNames([locale], { type: "region" }).of(country) ?? country
  );
}

export function profileHistoryUrl(sourcePath) {
  return `https://github.com/djairofilho/awesome-latam-vc/commits/main/${sourcePath
    .split("/")
    .map(encodeURIComponent)
    .join("/")}`;
}

export function profileMarkdownHref(href) {
  if (/^[a-z][a-z+.-]*:/i.test(String(href)) || String(href).startsWith("/")) {
    return href;
  }
  const match = String(href).match(/([^/#]+)\.md(#[^#]*)?$/);
  if (!match) {
    return href;
  }
  const slug = match[1]
    .normalize("NFKD")
    .replace(/\p{Diacritic}/gu, "")
    .toLocaleLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
  return `../${slug}/${match[2] ?? ""}`;
}
