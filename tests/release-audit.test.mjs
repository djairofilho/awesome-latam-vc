import assert from "node:assert/strict";
import test from "node:test";
import {
  catalogCountReadiness,
  measurementReadiness,
  parseStructuredFrontmatter,
  translationInventory,
} from "../scripts/audit-release.mjs";
import { mkdtempSync, mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { tmpdir } from "node:os";

function profile(metadata, body = "# Example\n") {
  return `---\n${JSON.stringify(metadata, null, 2)}\n---\n${body}`;
}

test("structured frontmatter must be JSON", () => {
  assert.deepEqual(
    parseStructuredFrontmatter(profile({ locale: "pt-BR" })),
    { locale: "pt-BR" },
  );
  assert.throws(
    () => parseStructuredFrontmatter("---\nlocale: pt-BR\n---\n"),
    /not valid JSON/u,
  );
});

test("release inventory requires one complete translation per entity and locale", () => {
  const root = mkdtempSync(join(tmpdir(), "release-audit-"));
  const entity = { id: "fund:example", source_profile: "funds/br/example.md" };
  for (const [locale, directory] of [
    ["pt-BR", "translations/pt-BR"],
    ["es", "translations/es"],
  ]) {
    const path = join(root, directory, entity.source_profile);
    mkdirSync(join(path, ".."), { recursive: true });
    writeFileSync(
      path,
      profile({
        id: `fund:example:${locale}`,
        entity_id: entity.id,
        locale,
        translation_of: "fund:example:en",
        translation_status: "complete",
      }),
      "utf8",
    );
  }
  assert.deepEqual(translationInventory(root, [entity]), [
    { locale: "pt-BR", count: 1 },
    { locale: "es", count: 1 },
  ]);
});

test("release inventory rejects needs-review content", () => {
  const root = mkdtempSync(join(tmpdir(), "release-audit-"));
  const entity = { id: "fund:example", source_profile: "funds/br/example.md" };
  for (const [locale, directory] of [
    ["pt-BR", "translations/pt-BR"],
    ["es", "translations/es"],
  ]) {
    const path = join(root, directory, entity.source_profile);
    mkdirSync(join(path, ".."), { recursive: true });
    writeFileSync(
      path,
      profile({
        entity_id: entity.id,
        locale,
        translation_of: "fund:example:en",
        translation_status: locale === "pt-BR" ? "needs_review" : "complete",
      }),
      "utf8",
    );
  }
  assert.throws(() => translationInventory(root, [entity]), /not complete/u);
});

test("release catalog count must match every localized README", () => {
  const root = mkdtempSync(join(tmpdir(), "release-audit-"));
  const entities = [
    { entity_type: "fund" },
    { entity_type: "fund" },
    { entity_type: "accelerator" },
  ];
  for (const [filename, line] of [
    ["README.md", "The index currently covers 2 funds."],
    ["README.pt.md", "O índice atualmente reúne 2 fundos."],
    ["README.es.md", "El índice actualmente reúne 2 fondos."],
  ]) {
    writeFileSync(join(root, filename), `${line}\n`, "utf8");
  }
  assert.deepEqual(catalogCountReadiness(root, entities), {
    funds: 2,
    readmes: {
      "README.md": 2,
      "README.pt.md": 2,
      "README.es.md": 2,
    },
  });
  writeFileSync(
    join(root, "README.pt.md"),
    "O índice atualmente reúne 1 fundos.\n",
    "utf8",
  );
  assert.throws(
    () => catalogCountReadiness(root, entities),
    /README\.pt\.md publishes 1 funds, expected 2/u,
  );
});

test("measurement readiness requires verified ownership and accepted sitemaps", () => {
  const ready = {
    public_endpoints: { homepage: 200, sitemap: 200, robots: 200 },
    providers: {
      google_search_console: {
        verification_status: "verified",
        sitemap_status: "processed",
      },
      bing_webmaster_tools: {
        verification_status: "verified",
        sitemap_status: "accepted",
      },
    },
  };
  assert.deepEqual(measurementReadiness(ready), {
    google_search_console: {
      verification_status: "verified",
      sitemap_status: "processed",
    },
    bing_webmaster_tools: {
      verification_status: "verified",
      sitemap_status: "accepted",
    },
  });
  ready.providers.bing_webmaster_tools.verification_status =
    "pending_authenticated_owner";
  assert.throws(() => measurementReadiness(ready), /ownership is not verified/u);
});
