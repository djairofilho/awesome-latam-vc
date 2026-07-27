import type { CollectionEntry } from "astro:content";
import { readFileSync } from "node:fs";
import { relative, sep } from "node:path";

const repositoryRoot = process.cwd();

export const categoryLabels = {
  fund: "Venture funds",
  accelerator: "Accelerators",
  angel_network: "Angel networks",
  funding_platform: "Funding platforms",
  public_program: "Public programs",
} as const;

export type Category = keyof typeof categoryLabels;

const categoryByPath: Record<string, Category> = {
  funds: "fund",
  accelerators: "accelerator",
  "angel-networks": "angel_network",
  "funding-platforms": "funding_platform",
  "public-programs": "public_program",
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

export function catalogItem(entry: CollectionEntry<"profiles">) {
  const sourcePath = normalizedSourcePath(entry);
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
    name: entry.data.name ?? fallbackName(entry),
    summary: entry.data.summary,
    category,
    categoryLabel: categoryLabels[category],
    country,
    sourcePath,
    sourceUrl: `https://github.com/djairofilho/awesome-latam-vc/blob/main/${sourcePath
      .split("/")
      .map(encodeURIComponent)
      .join("/")}`,
    hasStructuredMetadata: Boolean(entry.data.entity_id),
  };
}
