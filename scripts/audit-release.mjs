import { execFileSync } from "node:child_process";
import {
  existsSync,
  readFileSync,
  readdirSync,
  statSync,
} from "node:fs";
import { join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = resolve(fileURLToPath(new URL("..", import.meta.url)));
const LOCALES = Object.freeze(["en", "pt-BR", "es"]);
const TRANSLATION_ROOTS = Object.freeze({
  "pt-BR": "translations/pt-BR",
  es: "translations/es",
});
const MOJIBAKE = /(?:Ã.|Â.|â€¦|â€“|â€”|ï¿½|\uFFFD)/u;

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

export function parseStructuredFrontmatter(source, sourcePath = "content") {
  const match = source.match(/^---\s*\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/u);
  assert(match, `${sourcePath} has no structured frontmatter`);
  try {
    return JSON.parse(match[1]);
  } catch (error) {
    throw new Error(`${sourcePath} frontmatter is not valid JSON: ${error.message}`);
  }
}

export function translationInventory(repositoryRoot, entities) {
  const canonicalIds = new Set(entities.map(({ id }) => id));
  assert(canonicalIds.size === entities.length, "canonical entity IDs are not unique");
  return Object.entries(TRANSLATION_ROOTS).map(([locale, root]) => {
    const ids = new Set();
    for (const entity of entities) {
      const path = join(repositoryRoot, root, entity.source_profile);
      assert(existsSync(path), `${locale} is missing ${entity.source_profile}`);
      const source = readFileSync(path, "utf8");
      assert(!MOJIBAKE.test(source), `${path} contains mojibake`);
      const metadata = parseStructuredFrontmatter(source, path);
      assert(metadata.locale === locale, `${path} has locale ${metadata.locale}`);
      assert(
        metadata.entity_id === entity.id,
        `${path} maps to ${metadata.entity_id}, expected ${entity.id}`,
      );
      assert(metadata.translation_status === "complete", `${path} is not complete`);
      assert(
        typeof metadata.translation_of === "string" &&
          metadata.translation_of.endsWith(":en"),
        `${path} has no canonical English translation target`,
      );
      assert(!ids.has(metadata.entity_id), `${locale} duplicates ${metadata.entity_id}`);
      ids.add(metadata.entity_id);
    }
    assert(ids.size === canonicalIds.size, `${locale} entity count diverges`);
    return { locale, count: ids.size };
  });
}

function htmlFiles(directory) {
  if (!existsSync(directory)) {
    return [];
  }
  return readdirSync(directory).flatMap((name) => {
    const path = join(directory, name);
    return statSync(path).isDirectory()
      ? htmlFiles(path)
      : path.endsWith(".html")
        ? [path]
        : [];
  });
}

export function builtProfileInventory(repositoryRoot, entities) {
  const slugByEntity = new Map(
    entities.map((entity) => {
      const canonical = readFileSync(join(repositoryRoot, entity.source_profile), "utf8");
      const metadata = parseStructuredFrontmatter(canonical, entity.source_profile);
      return [entity.id, metadata.slug];
    }),
  );
  const counts = Object.fromEntries(LOCALES.map((locale) => [locale, 0]));
  for (const [entityId, slug] of slugByEntity) {
    for (const locale of LOCALES) {
      const path = join(
        repositoryRoot,
        "dist",
        locale === "pt-BR" ? "pt-br" : locale,
        "profiles",
        slug,
        "index.html",
      );
      assert(existsSync(path), `${locale} has no built profile for ${entityId}`);
      const html = readFileSync(path, "utf8");
      assert(!MOJIBAKE.test(html), `${path} contains mojibake`);
      assert(
        new RegExp(`<html[^>]+lang="${locale}"`, "u").test(html),
        `${path} has the wrong html lang`,
      );
      assert(!/name="robots"[^>]+noindex/iu.test(html), `${path} is unexpectedly noindex`);
      counts[locale] += 1;
    }
  }
  return counts;
}

export function auditBuiltSite(repositoryRoot, entities) {
  const distRoot = join(repositoryRoot, "dist");
  assert(existsSync(distRoot), "dist/ is missing; run npm run build first");
  const profiles = builtProfileInventory(repositoryRoot, entities);
  const html = htmlFiles(distRoot);
  assert(html.length > entities.length * LOCALES.length, "built site is incomplete");
  const sitemap = readFileSync(join(distRoot, "sitemap.xml"), "utf8");
  const sitemapUrls = [...sitemap.matchAll(/<loc>([^<]+)<\/loc>/gu)].map((match) => match[1]);
  assert(new Set(sitemapUrls).size === sitemapUrls.length, "sitemap has duplicate URLs");
  assert(
    sitemapUrls.every((url) =>
      url.startsWith("https://djairofilho.github.io/awesome-latam-vc/"),
    ),
    "sitemap contains a non-production URL",
  );
  assert(existsSync(join(distRoot, "pagefind", "pagefind.js")), "Pagefind output is missing");
  return {
    html_files: html.length,
    sitemap_urls: sitemapUrls.length,
    profiles,
  };
}

export function measurementReadiness(status) {
  const providers = Object.entries(status.providers ?? {});
  assert(providers.length === 2, "measurement status must contain two providers");
  for (const [providerId, provider] of providers) {
    assert(
      provider.verification_status === "verified",
      `${providerId} ownership is not verified`,
    );
    assert(
      ["accepted", "processed"].includes(provider.sitemap_status),
      `${providerId} sitemap is not accepted`,
    );
  }
  assert(
    Object.values(status.public_endpoints ?? {}).every((code) => code === 200),
    "measurement public endpoints are not healthy",
  );
  return Object.fromEntries(
    providers.map(([providerId, provider]) => [
      providerId,
      {
        verification_status: provider.verification_status,
        sitemap_status: provider.sitemap_status,
      },
    ]),
  );
}

export function runReleaseAudit(repositoryRoot = ROOT) {
  const entityDocument = JSON.parse(
    readFileSync(join(repositoryRoot, "data", "entities.json"), "utf8"),
  );
  assert(entityDocument.entities.length > 0, "entity export is empty");
  const translations = translationInventory(repositoryRoot, entityDocument.entities);
  const built = auditBuiltSite(repositoryRoot, entityDocument.entities);
  const measurement = measurementReadiness(
    JSON.parse(
      readFileSync(
        join(
          repositoryRoot,
          "research",
          "seo-geo",
          "measurement",
          "provider-status.json",
        ),
        "utf8",
      ),
    ),
  );
  return {
    schema_version: "1.0",
    audited_on: new Date().toISOString().slice(0, 10),
    entities: entityDocument.entities.length,
    translations,
    built,
    measurement,
    critical_findings: 0,
    high_findings: 0,
  };
}

function run(command, args) {
  execFileSync(command, args, { cwd: ROOT, stdio: "inherit" });
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  run("python", ["tools/seo_geo/validate_i18n.py", "--release"]);
  run("python", [
    "tools/seo_geo/validate_editorial.py",
    "--require-complete-locales",
  ]);
  const report = runReleaseAudit();
  process.stdout.write(`${JSON.stringify(report, null, 2)}\n`);
}
