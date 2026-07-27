import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { canonicalUrl, withBase } from "../src/lib/paths.mjs";

test("base-path helpers preserve the GitHub Pages subdirectory", () => {
  assert.equal(withBase("/"), "/awesome-latam-vc/");
  assert.equal(withBase("/catalog/"), "/awesome-latam-vc/catalog/");
  assert.equal(
    canonicalUrl("/catalog/"),
    "https://djairofilho.github.io/awesome-latam-vc/catalog/",
  );
});

test("the content layer reads canonical profiles without moving them", () => {
  const config = readFileSync("src/content.config.ts", "utf8");
  const contract = JSON.parse(
    readFileSync("research/seo-geo/contract/profile.schema.json", "utf8"),
  );
  for (const source of [
    "funds/**/*.md",
    "ecosystem/accelerators/**/*.md",
    "ecosystem/angel-networks/**/*.md",
    "ecosystem/funding-platforms/**/*.md",
    "ecosystem/public-programs/**/*.md",
  ]) {
    assert.match(config, new RegExp(source.replaceAll("*", "\\*")));
  }
  for (const field of contract.required) {
    assert.match(config, new RegExp(`\\b${field}:`), `missing ${field}`);
  }
});

test("pull requests validate without deployment", () => {
  const workflow = readFileSync(".github/workflows/site-build.yml", "utf8");
  assert.match(workflow, /pull_request:/);
  assert.match(workflow, /npm run verify/);
  assert.doesNotMatch(workflow, /uses:\s+actions\/deploy-pages/);
  assert.match(workflow, /PUBLIC_SITE_ENV: preview/);
});

test("production deployment is restricted to main and github-pages", () => {
  const workflow = readFileSync(".github/workflows/deploy-pages.yml", "utf8");
  assert.match(workflow, /branches: \[main\]/);
  assert.match(workflow, /name: github-pages/);
  assert.match(workflow, /actions\/deploy-pages@v5/);
  assert.match(workflow, /PUBLIC_SITE_ENV: production/);
  assert.doesNotMatch(workflow, /pull_request:/);
});
