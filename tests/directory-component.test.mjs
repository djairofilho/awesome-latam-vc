import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import {
  mkdirSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";

test("directory component exposes keyboard and assistive-technology states", () => {
  const component = readFileSync(
    "src/components/DirectoryExplorer.astro",
    "utf8",
  );
  const controller = readFileSync(
    "src/scripts/directory-explorer.mjs",
    "utf8",
  );
  const styles = readFileSync("src/styles/global.css", "utf8");

  assert.match(component, /role="search"/);
  assert.match(component, /type="search"/);
  assert.match(component, /type="checkbox"/);
  assert.match(component, /type="reset"/);
  assert.match(component, /role="status"/);
  assert.match(component, /aria-live="polite"/);
  assert.match(component, /aria-atomic="true"/);
  assert.match(component, /aria-busy="false"/);
  assert.match(component, /<noscript>/);
  assert.match(controller, /dataset\.loadingMessage/);
  assert.match(controller, /dataset\.emptyMessage/);
  assert.match(controller, /dataset\.errorMessage/);
  assert.match(controller, /window\.history\.replaceState/);
  assert.match(styles, /input:focus-visible/);
  assert.match(styles, /\.directory-results li\[hidden\]/);
});

test("Pagefind creates separate indexes for every supported locale", () => {
  const fixtureRoot = mkdtempSync(join(tmpdir(), "pagefind-locales-"));
  const pagefindCli = join(
    process.cwd(),
    "node_modules",
    "pagefind",
    "lib",
    "runner",
    "bin.cjs",
  );
  try {
    for (const [locale, copy] of [
      ["en", "Innovation funding"],
      ["pt-br", "Financiamento para inovação"],
      ["es", "Financiación para innovación"],
    ]) {
      const directory = join(fixtureRoot, locale);
      mkdirSync(directory, { recursive: true });
      writeFileSync(
        join(directory, "index.html"),
        `<!doctype html><html lang="${locale}"><body>${copy}</body></html>`,
        "utf8",
      );
    }
    execFileSync(
      process.execPath,
      [pagefindCli, "--site", fixtureRoot],
      { cwd: process.cwd(), stdio: "pipe" },
    );
    const entry = JSON.parse(
      readFileSync(
        join(fixtureRoot, "pagefind", "pagefind-entry.json"),
        "utf8",
      ),
    );
    assert.deepEqual(Object.keys(entry.languages).sort(), [
      "en",
      "es",
      "pt-br",
    ]);
  } finally {
    rmSync(fixtureRoot, { recursive: true, force: true });
  }
});
