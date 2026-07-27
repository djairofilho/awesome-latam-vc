import { spawn } from "node:child_process";
import { mkdirSync, readFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = resolve(fileURLToPath(new URL("..", import.meta.url)));
const BASE_URL = "http://127.0.0.1:4321/awesome-latam-vc";
const OUTPUT = join(ROOT, ".lighthouse");
const THRESHOLDS = Object.freeze({
  performance: 0.9,
  accessibility: 0.95,
  "best-practices": 0.95,
  seo: 0.95,
});
const REPRESENTATIVE_PATHS = Object.freeze(
  ["en", "pt-br", "es"].flatMap((locale) => [
    `/${locale}/`,
    `/${locale}/countries/br/`,
    `/${locale}/profiles/500-latam/`,
    `/${locale}/catalog/?q=capital`,
  ]),
);

function wait(milliseconds) {
  return new Promise((resolvePromise) => setTimeout(resolvePromise, milliseconds));
}

async function waitForServer() {
  for (let attempt = 0; attempt < 60; attempt += 1) {
    try {
      const response = await fetch(`${BASE_URL}/`);
      if (response.ok) {
        return;
      }
    } catch {
      // The preview server is still starting.
    }
    await wait(500);
  }
  throw new Error("Astro preview did not become ready");
}

function run(command, args, options = {}) {
  return new Promise((resolvePromise, reject) => {
    const child = spawn(command, args, {
      cwd: ROOT,
      shell: process.platform === "win32",
      stdio: "inherit",
      ...options,
    });
    child.once("error", reject);
    child.once("exit", (code) => {
      if (code === 0) {
        resolvePromise();
      } else {
        reject(new Error(`${command} exited with ${code}`));
      }
    });
  });
}

function safeName(path) {
  return path.replace(/[/?=&]+/gu, "-").replace(/^-|-$/gu, "");
}

mkdirSync(OUTPUT, { recursive: true });
const preview = spawn(
  process.platform === "win32" ? "npm.cmd" : "npm",
  ["run", "preview", "--", "--host", "127.0.0.1", "--port", "4321"],
  { cwd: ROOT, stdio: "ignore" },
);

try {
  await waitForServer();
  const results = [];
  for (const path of REPRESENTATIVE_PATHS) {
    const output = join(OUTPUT, `${safeName(path)}.json`);
    await run(
      process.execPath,
      [
        "node_modules/lighthouse/cli/index.js",
        `${BASE_URL}${path}`,
        "--quiet",
        "--output=json",
        `--output-path=${output}`,
        "--only-categories=performance,accessibility,best-practices,seo",
        "--chrome-flags=--headless --no-sandbox --disable-dev-shm-usage",
      ],
      { stdio: "ignore" },
    );
    const report = JSON.parse(readFileSync(output, "utf8"));
    const scores = Object.fromEntries(
      Object.keys(THRESHOLDS).map((category) => [
        category,
        report.categories[category].score,
      ]),
    );
    for (const [category, threshold] of Object.entries(THRESHOLDS)) {
      if (scores[category] < threshold) {
        throw new Error(
          `${path} ${category} score ${scores[category]} is below ${threshold}`,
        );
      }
    }
    results.push({ path, scores });
  }
  process.stdout.write(`${JSON.stringify({ thresholds: THRESHOLDS, results }, null, 2)}\n`);
} finally {
  preview.kill();
}
