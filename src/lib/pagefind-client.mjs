import {
  normalizeDirectoryState,
  pagefindFilters,
} from "./directory.mjs";
import { withBase } from "./paths.mjs";

export const SEARCH_LOCALES = ["en", "pt-br", "es"];

export function normalizeSearchLocale(locale) {
  return String(locale ?? "").trim().toLocaleLowerCase();
}

export function pagefindBundlePath() {
  return withBase("/pagefind/");
}

export function pagefindModulePath() {
  return withBase("/pagefind/pagefind.js");
}

export async function loadPagefind({
  documentElement = document.documentElement,
  importer = (path) => import(/* @vite-ignore */ path),
} = {}) {
  const locale = normalizeSearchLocale(documentElement.lang);
  if (!SEARCH_LOCALES.includes(locale)) {
    throw new Error(`Unsupported Pagefind document language: ${locale}`);
  }

  const pagefind = await importer(pagefindModulePath());
  await pagefind.options({ bundlePath: pagefindBundlePath() });
  await pagefind.init();
  return pagefind;
}

export function normalizePagefindQuery(query) {
  return String(query ?? "").normalize("NFC").replace(/\s+/g, " ").trim();
}

export async function searchPagefind(pagefind, state = {}) {
  const normalized = normalizeDirectoryState(state);
  const query = normalizePagefindQuery(normalized.query);
  const options = { filters: pagefindFilters(normalized) };
  const response = query
    ? await pagefind.debouncedSearch(query, options, 200)
    : await pagefind.search(null, options);

  if (response === null) {
    return { cancelled: true, results: [], filters: {} };
  }
  const results = await Promise.all(
    response.results.map((result) => result.data()),
  );
  return {
    cancelled: false,
    results,
    filters: response.filters ?? {},
    totalFilters: response.totalFilters ?? {},
    unfilteredResultCount:
      response.unfilteredResultCount ?? response.results.length,
  };
}
