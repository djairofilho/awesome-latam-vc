import { defineCollection } from "astro:content";
import { glob } from "astro/loaders";
import { z } from "astro/zod";

const geography = z.looseObject({
  kind: z.enum(["country", "region", "global"]),
  code: z.string(),
});

const source = z.looseObject({
  title: z.string(),
  url: z.url(),
  kind: z.string(),
});

const editorialReference = z.strictObject({
  title: z.string().min(1),
  url: z.url(),
});

const profiles = defineCollection({
  loader: glob({
    base: ".",
    pattern: [
      "funds/**/*.md",
      "ecosystem/accelerators/**/*.md",
      "ecosystem/angel-networks/**/*.md",
      "ecosystem/funding-platforms/**/*.md",
      "ecosystem/public-programs/**/*.md",
      "translations/pt-BR/funds/**/*.md",
      "translations/pt-BR/ecosystem/accelerators/**/*.md",
      "translations/pt-BR/ecosystem/angel-networks/**/*.md",
      "translations/pt-BR/ecosystem/funding-platforms/**/*.md",
      "translations/pt-BR/ecosystem/public-programs/**/*.md",
      "translations/es/funds/**/*.md",
      "translations/es/ecosystem/accelerators/**/*.md",
      "translations/es/ecosystem/angel-networks/**/*.md",
      "translations/es/ecosystem/funding-platforms/**/*.md",
      "translations/es/ecosystem/public-programs/**/*.md",
      "!**/README*.md",
    ],
  }),
  schema: z.looseObject({
    schema_version: z.string().optional(),
    id: z.string().optional(),
    entity_id: z.string().optional(),
    slug: z.string().optional(),
    name: z.string().optional(),
    entity_type: z
      .enum([
        "fund",
        "accelerator",
        "angel_network",
        "funding_platform",
        "public_program",
      ])
      .optional(),
    locale: z.enum(["en", "pt-BR", "es"]).optional(),
    translation_of: z.string().nullable().optional(),
    translation_status: z
      .enum(["canonical", "complete", "needs_review"])
      .optional(),
    summary: z.string().optional(),
    aliases: z.array(z.string()).optional(),
    operator: z.string().nullable().optional(),
    base_geography: geography.optional(),
    countries_covered: z.array(z.string()).optional(),
    stages: z.array(z.string()).optional(),
    focuses: z.array(z.string()).optional(),
    official_website: z.url().nullable().optional(),
    founder_route: z.url().nullable().optional(),
    sources: z.array(source).optional(),
    last_verified: z.string().optional(),
    protected_terms: z.array(z.string()).optional(),
  }),
});

const editorialPages = defineCollection({
  loader: glob({
    base: "research/seo-geo/content/editorial",
    pattern: "**/*.md",
  }),
  schema: z.strictObject({
    schema_version: z.literal("1.0"),
    id: z.string(),
    slug: z.enum([
      "methodology",
      "inclusion",
      "sources",
      "updates",
      "license",
      "limitations",
      "citation",
    ]),
    locale: z.enum(["en", "pt-BR", "es"]),
    translation_of: z.string().nullable(),
    translation_status: z.enum(["canonical", "complete", "needs_review"]),
    title: z.string().min(1).max(80),
    summary: z.string().min(1).max(240),
    last_reviewed: z.string(),
    references: z.array(editorialReference),
  }),
});

export const collections = { profiles, editorialPages };
