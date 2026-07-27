import { directoryRecord } from "./directory.mjs";
import { localizedHref } from "./i18n.mjs";

const COUNTRY_CODE = /^[A-Z]{2}$/;

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
        geography.filter((value) => COUNTRY_CODE.test(value)),
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
