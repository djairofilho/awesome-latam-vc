import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = resolve(fileURLToPath(new URL("..", import.meta.url)));
const SOURCE_ROOTS = Object.freeze([
  "funds",
  "ecosystem",
  "translations",
  "research/seo-geo/content/editorial",
]);
const URL_PATTERN = /https:\/\/[^\s<>"'`)\]}]+/gu;
const CONCURRENCY = 12;
const RETRIES = 3;
const TIMEOUT_MS = 12_000;
const RESTRICTED_STATUSES = new Set([401, 403, 405, 406, 409, 429]);

function files(directory) {
  return readdirSync(directory).flatMap((name) => {
    const path = join(directory, name);
    return statSync(path).isDirectory() ? files(path) : [path];
  });
}

function sourceFiles() {
  return SOURCE_ROOTS.flatMap((directory) =>
    existsSync(join(ROOT, directory))
      ? files(join(ROOT, directory)).filter((path) => path.endsWith(".md"))
      : [],
  );
}

function trimUrl(url) {
  return url.replace(/[.,;:!?]+$/u, "");
}

function extractUrls(path) {
  const source = readFileSync(path, "utf8");
  return [...source.matchAll(URL_PATTERN)].map((match) => trimUrl(match[0]));
}

async function request(url, method) {
  return fetch(url, {
    method,
    redirect: "follow",
    signal: AbortSignal.timeout(TIMEOUT_MS),
    headers: { "user-agent": "awesome-latam-vc-release-audit" },
  });
}

async function check(url) {
  let lastError;
  let lastStatus;
  for (let attempt = 1; attempt <= RETRIES; attempt += 1) {
    let response;
    try {
      response = await request(url, "HEAD");
    } catch (error) {
      lastError = error;
    }
    if (!response || response.status >= 400) {
      try {
        response = await request(url, "GET");
        await response.body?.cancel();
      } catch (error) {
        lastError = error;
      }
    }
    if (response) {
      lastStatus = response.status;
      if (response.status < 400) {
        return { url, outcome: "ok", status: response.status };
      }
      if (RESTRICTED_STATUSES.has(response.status)) {
        return { url, outcome: "restricted", status: response.status };
      }
      lastError = new Error(`HTTP ${response.status}`);
    }
    if (attempt < RETRIES) {
      await new Promise((resolve) => setTimeout(resolve, attempt * 500));
    }
  }
  return {
    url,
    outcome: [404, 410].includes(lastStatus) ? "broken" : "unverified",
    ...(lastStatus ? { status: lastStatus } : {}),
    error: lastError instanceof Error ? lastError.message : String(lastError),
  };
}

const sourcesByUrl = new Map();
for (const path of sourceFiles()) {
  for (const url of extractUrls(path)) {
    const sources = sourcesByUrl.get(url) ?? [];
    sources.push(path.slice(ROOT.length + 1).replaceAll("\\", "/"));
    sourcesByUrl.set(url, sources);
  }
}

const queue = [...sourcesByUrl.keys()].sort();
const results = [];
async function worker() {
  while (queue.length > 0) {
    const url = queue.shift();
    if (!url) {
      return;
    }
    results.push(await check(url));
  }
}
await Promise.all(Array.from({ length: CONCURRENCY }, worker));
results.sort((left, right) => left.url.localeCompare(right.url));

const broken = results
  .filter(({ outcome }) => outcome === "broken")
  .map((result) => ({
    ...result,
    sources: [...new Set(sourcesByUrl.get(result.url))],
  }));
const summary = {
  checked_at: new Date().toISOString(),
  unique_urls: results.length,
  ok: results.filter(({ outcome }) => outcome === "ok").length,
  restricted: results.filter(({ outcome }) => outcome === "restricted").length,
  unverified: results
    .filter(({ outcome }) => outcome === "unverified")
    .map((result) => ({
      ...result,
      sources: [...new Set(sourcesByUrl.get(result.url))],
    })),
  broken,
};
process.stdout.write(`${JSON.stringify(summary, null, 2)}\n`);
if (broken.length > 0) {
  process.exitCode = 1;
}
