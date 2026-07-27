import { spawn } from "node:child_process";
import { createServer } from "node:net";
import { join } from "node:path";

const root = process.cwd();
const astroCli = join(root, "node_modules", "astro", "bin", "astro.mjs");

async function availablePort() {
  const server = createServer();
  await new Promise((resolve, reject) => {
    server.once("error", reject);
    server.listen(0, "127.0.0.1", resolve);
  });
  const address = server.address();
  const port = typeof address === "object" && address ? address.port : null;
  await new Promise((resolve, reject) =>
    server.close((error) => (error ? reject(error) : resolve())),
  );
  if (!port) {
    throw new Error("Could not reserve a preview port");
  }
  return port;
}

async function waitForServer(url) {
  for (let attempt = 0; attempt < 80; attempt += 1) {
    try {
      const response = await fetch(url);
      if (response.status < 500) {
        return;
      }
    } catch {
      // The preview process is still starting.
    }
    await new Promise((resolve) => setTimeout(resolve, 100));
  }
  throw new Error(`Preview server did not start at ${url}`);
}

const port = await availablePort();
const origin = `http://127.0.0.1:${port}`;
const base = `${origin}/awesome-latam-vc`;
const preview = spawn(
  process.execPath,
  [astroCli, "preview", "--host", "127.0.0.1", "--port", String(port)],
  {
    cwd: root,
    env: { ...process.env, PUBLIC_SITE_ENV: "production" },
    stdio: ["ignore", "pipe", "pipe"],
  },
);
let stderr = "";
preview.stderr.on("data", (chunk) => {
  stderr += chunk;
});

try {
  await waitForServer(`${base}/`);
  const checks = [
    ["/", 200, "text/html"],
    ["/en/", 200, "text/html"],
    ["/pt-br/", 200, "text/html"],
    ["/es/", 200, "text/html"],
    ["/en/catalog/", 200, "text/html"],
    ["/pt-br/catalog/", 200, "text/html"],
    ["/es/catalog/", 200, "text/html"],
    ["/sitemap.xml", 200, "xml"],
    ["/robots.txt", 200, "text/plain"],
    ["/data/entities.json", 200, "application/json"],
    ["/data/entities.csv", 200, "text/csv"],
  ];
  for (const [path, status, contentType] of checks) {
    const response = await fetch(`${base}${path}`);
    if (response.status !== status) {
      throw new Error(`${path} returned ${response.status}, expected ${status}`);
    }
    if (!response.headers.get("content-type")?.includes(contentType)) {
      throw new Error(`${path} did not return ${contentType}`);
    }
  }

  const missing = await fetch(`${base}/route-that-does-not-exist/`);
  const missingBody = await missing.text();
  if (missing.status !== 404 || !missingBody.includes("This path is not in the catalog.")) {
    throw new Error("unknown routes must return the custom 404 experience");
  }
  console.log(`URL smoke passed for ${checks.length} public outputs and custom 404.`);
} finally {
  preview.kill();
  await new Promise((resolve) => {
    if (preview.exitCode !== null) {
      resolve();
      return;
    }
    preview.once("exit", resolve);
    setTimeout(resolve, 2000);
  });
}

if (preview.exitCode && preview.exitCode !== 0 && stderr) {
  throw new Error(stderr);
}
