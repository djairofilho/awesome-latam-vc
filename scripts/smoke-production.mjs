const BASE_URL = (
  process.env.PRODUCTION_BASE_URL ??
  "https://djairofilho.github.io/awesome-latam-vc"
).replace(/\/$/u, "");

const CHECKS = Object.freeze([
  ["/", "text/html"],
  ["/en/", "text/html"],
  ["/pt-br/", "text/html"],
  ["/es/", "text/html"],
  ["/en/catalog/", "text/html"],
  ["/pt-br/catalog/", "text/html"],
  ["/es/catalog/", "text/html"],
  ["/en/profiles/500-latam/", "text/html"],
  ["/pt-br/profiles/500-latam/", "text/html"],
  ["/es/profiles/500-latam/", "text/html"],
  ["/sitemap.xml", "xml"],
  ["/robots.txt", "text/plain"],
  ["/data/entities.json", "application/json"],
  ["/data/entities.csv", "text/csv"],
]);

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

async function fetchWithRetry(url, attempts = 4) {
  let lastError;
  for (let attempt = 1; attempt <= attempts; attempt += 1) {
    try {
      const response = await fetch(url, {
        headers: { "user-agent": "awesome-latam-vc-release-audit" },
      });
      if (response.status < 500 || attempt === attempts) {
        return response;
      }
      lastError = new Error(`${url} returned ${response.status}`);
    } catch (error) {
      lastError = error;
    }
    await new Promise((resolve) => setTimeout(resolve, attempt * 500));
  }
  throw lastError;
}

const results = [];
for (const [path, expectedContentType] of CHECKS) {
  const url = `${BASE_URL}${path}`;
  const response = await fetchWithRetry(url);
  const contentType = response.headers.get("content-type") ?? "";
  assert(response.status === 200, `${url} returned ${response.status}`);
  assert(
    contentType.includes(expectedContentType),
    `${url} returned ${contentType}, expected ${expectedContentType}`,
  );
  const body = await response.text();
  assert(body.length > 0, `${url} returned an empty body`);
  if (expectedContentType === "text/html") {
    assert(
      !body.includes('name="robots" content="noindex'),
      `${url} is unexpectedly noindex`,
    );
  }
  results.push({
    path,
    status: response.status,
    content_type: contentType.split(";")[0],
    bytes: Buffer.byteLength(body),
  });
}

const missingUrl = `${BASE_URL}/release-audit-route-that-does-not-exist/`;
const missing = await fetchWithRetry(missingUrl);
assert(missing.status === 404, `${missingUrl} returned ${missing.status}, expected 404`);

process.stdout.write(
  `${JSON.stringify(
    {
      checked_at: new Date().toISOString(),
      base_url: BASE_URL,
      checks: results,
      custom_404_status: missing.status,
    },
    null,
    2,
  )}\n`,
);
