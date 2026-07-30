import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import test from "node:test";

const root = process.cwd();
const audit = join(root, "research", "epic-257", "central-america");

const json = (path) => JSON.parse(readFileSync(path, "utf8"));
const jsonl = (path) =>
  readFileSync(path, "utf8")
    .trim()
    .split(/\r?\n/)
    .filter(Boolean)
    .map((line) => JSON.parse(line));

test("Central America freeze covers every country and keeps regulators identity-only", () => {
  const contract = json(join(audit, "contract.json"));
  const coverage = json(join(audit, "coverage-matrix.json"));
  const candidates = jsonl(join(audit, "candidates.jsonl"));
  const regulators = jsonl(join(audit, "regulatory-query-log.jsonl"));

  assert.deepEqual(
    coverage.countries.map(({ country }) => country).sort(),
    contract.scope_countries.toSorted(),
  );
  assert.equal(candidates.length, 22);
  assert.equal(contract.regulatory_query_percentage, 9.1);
  assert.equal(contract.regulatory_target_met, true);
  assert.ok(regulators.every((row) => row.effect === "identity_only"));
  assert.ok(regulators.every((row) => !row.used_for_discovery && !row.used_for_eligibility));
});

test("only the three reconciled Central America funds are published", () => {
  const candidates = jsonl(join(audit, "candidates.jsonl"));
  const eligible = candidates
    .filter(({ decision }) => decision === "eligible")
    .map(({ candidate_id }) => candidate_id)
    .sort();

  assert.deepEqual(eligible, ["ca-infinita", "ca-invertup", "ca-venture-club-latam"]);
  assert.equal(
    candidates.find(({ candidate_id }) => candidate_id === "ca-barrilete").decision,
    "insufficient_evidence",
  );

  for (const slug of ["infinita-vc", "invertup", "venture-club-latam"]) {
    for (const locale of ["en", "pt-BR", "es"]) {
      const prefix = locale === "en" ? root : join(root, "translations", locale);
      const body = readFileSync(join(prefix, "funds", "regional", `${slug}.md`), "utf8");
      assert.match(body, new RegExp(`"id": "fund:${slug}:${locale}"`));
    }
  }
});

test("Central America freeze hashes resolve and remain unchanged", () => {
  const freeze = json(join(audit, "freeze-manifest.json"));
  assert.equal(freeze.status, "frozen");
  for (const entry of freeze.files) {
    const actual = createHash("sha256")
      .update(readFileSync(join(root, entry.path)))
      .digest("hex");
    assert.equal(actual, entry.sha256, entry.path);
  }
});
