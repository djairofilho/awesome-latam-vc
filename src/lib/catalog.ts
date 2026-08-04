import type { CollectionEntry } from "astro:content";
import { readFileSync } from "node:fs";
import { relative, sep } from "node:path";

const repositoryRoot = process.cwd();

export const categories = [
  "fund",
  "accelerator",
  "angel_network",
  "funding_platform",
  "public_program",
  "hub_incubator",
] as const;

export type Category = (typeof categories)[number];
export type ContentLocale = "en" | "pt-BR" | "es";

const categoryByPath: Record<string, Category> = {
  funds: "fund",
  accelerators: "accelerator",
  "angel-networks": "angel_network",
  "funding-platforms": "funding_platform",
  "public-programs": "public_program",
  "hubs-incubators": "hub_incubator",
};

function normalizedSourcePath(entry: CollectionEntry<"profiles">) {
  if (!entry.filePath) {
    return entry.id.replaceAll("\\", "/");
  }
  return relative(repositoryRoot, entry.filePath).split(sep).join("/");
}

function fallbackName(entry: CollectionEntry<"profiles">) {
  if (!entry.filePath) {
    return entry.id;
  }
  const source = readFileSync(entry.filePath, "utf8");
  return source.match(/^#\s+(.+)$/m)?.[1]?.trim() ?? entry.id;
}

export function catalogItem(
  entry: CollectionEntry<"profiles">,
  canonicalEntry?: CollectionEntry<"profiles">,
) {
  const sourcePath = normalizedSourcePath(entry);
  const canonicalSourcePath = canonicalEntry
    ? normalizedSourcePath(canonicalEntry)
    : sourcePath;
  const parts = sourcePath.split("/");
  const category =
    entry.data.entity_type ??
    categoryByPath[parts[0] === "funds" ? "funds" : parts[1]];
  if (!category) {
    throw new Error(`Unsupported canonical profile path: ${sourcePath}`);
  }
  const country = parts.at(-2)?.replaceAll("-", " ") ?? "regional";
  return {
    id: entry.data.entity_id ?? sourcePath.replace(/\.md$/, ""),
    slug: entry.data.slug ?? sourcePath.split("/").at(-1)?.replace(/\.md$/, ""),
    name: entry.data.name ?? fallbackName(entry),
    summary: entry.data.summary,
    aliases: entry.data.aliases ?? [],
    category,
    country,
    baseGeography: entry.data.base_geography,
    countriesCovered: entry.data.countries_covered ?? [],
    stages: entry.data.stages ?? [],
    focuses: entry.data.focuses ?? [],
    sourcePath,
    sourceUrl: `https://github.com/djairofilho/awesome-latam-vc/blob/main/${sourcePath
      .split("/")
      .map(encodeURIComponent)
      .join("/")}`,
    canonicalSourceUrl: `https://github.com/djairofilho/awesome-latam-vc/blob/main/${canonicalSourcePath
      .split("/")
      .map(encodeURIComponent)
      .join("/")}`,
    operator: entry.data.operator,
    officialWebsite: entry.data.official_website,
    founderRoute: entry.data.founder_route,
    sources: entry.data.sources ?? [],
    lastVerified: entry.data.last_verified,
    hasStructuredMetadata: Boolean(entry.data.entity_id),
  };
}

export function localizedCatalogItems(
  entries: CollectionEntry<"profiles">[],
  locale: ContentLocale,
) {
  const byEntity = new Map<
    string,
    Map<ContentLocale, CollectionEntry<"profiles">>
  >();

  for (const entry of entries) {
    const item = catalogItem(entry);
    const contentLocale = (entry.data.locale ?? "en") as ContentLocale;
    const variants = byEntity.get(item.id) ?? new Map();
    variants.set(contentLocale, entry);
    byEntity.set(item.id, variants);
  }

  return [...byEntity.values()].flatMap((variants) => {
    const entry = variants.get(locale) ?? variants.get("en");
    if (!entry) {
      return [];
    }
    const canonicalEntry = variants.get("en");
    const contentLocale = (entry.data.locale ?? "en") as ContentLocale;
    return [
      {
        ...catalogItem(entry, canonicalEntry),
        contentEntryId: entry.id,
        contentLocale,
        isFallback: contentLocale !== locale,
        availableLocales: [...variants.keys()].sort(),
      },
    ];
  });
}
