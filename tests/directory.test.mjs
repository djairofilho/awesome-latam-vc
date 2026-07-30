import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import {
  deriveFacetCounts,
  deriveFacetValues,
  directoryRecord,
  filterDirectoryRecords,
  foldSearchText,
  pagefindFilters,
  parseDirectoryState,
  serializeDirectoryState,
} from "../src/lib/directory.mjs";
import {
  LANDING_THRESHOLD,
  deriveLandingPolicy,
  landingDecision,
} from "../src/lib/landing-policy.mjs";

const entityDocument = JSON.parse(
  readFileSync(new URL("../data/entities.json", import.meta.url), "utf8"),
);
const records = entityDocument.entities.map(directoryRecord);

test("directory records and facet counts derive from all 275 entities", () => {
  assert.equal(records.length, 275);
  assert.equal(new Set(records.map(({ id }) => id)).size, 275);

  const facets = deriveFacetValues(records);
  const counts = deriveFacetCounts(records);
  assert.deepEqual(facets.entity_type, [
    "accelerator",
    "angel_network",
    "fund",
    "funding_platform",
    "public_program",
  ]);
  assert.equal(
    Object.values(counts.entity_type).reduce(
      (total, count) => total + count,
      0,
    ),
    275,
  );
  for (const dimension of Object.keys(facets)) {
    for (const value of facets[dimension]) {
      assert.ok(counts[dimension][value] > 0);
    }
  }
});

test("search is insensitive to accents and case", () => {
  assert.equal(foldSearchText("  Inovação MÉXICO  "), "inovacao mexico");
  const accented = records.find((record) =>
    record.searchText.includes("inovacao"),
  );
  assert.ok(accented);
  assert.deepEqual(
    filterDirectoryRecords(records, { query: "INOVACAO" }).map(
      ({ id }) => id,
    ),
    filterDirectoryRecords(records, { query: "inovação" }).map(
      ({ id }) => id,
    ),
  );
});

test("combined filters use OR within a facet and AND across facets", () => {
  const state = {
    entity_type: ["fund", "accelerator"],
    geography: ["BR"],
    stage: ["seed"],
  };
  const filtered = filterDirectoryRecords(records, state);
  assert.ok(filtered.length > 0);
  for (const record of filtered) {
    assert.ok(
      record.entity_type.includes("fund") ||
        record.entity_type.includes("accelerator"),
    );
    assert.ok(record.geography.includes("BR"));
    assert.ok(record.stage.includes("seed"));
  }

  assert.deepEqual(pagefindFilters(state), {
    entity_type: { any: ["accelerator", "fund"] },
    geography: "BR",
    stage: "seed",
  });
});

test("contextual counts ignore only their own active facet", () => {
  const state = {
    entity_type: ["fund"],
    geography: ["BR"],
  };
  const counts = deriveFacetCounts(records, state);
  const brazilianFunds = filterDirectoryRecords(records, state);
  assert.equal(
    counts.entity_type.fund,
    filterDirectoryRecords(records, { geography: ["BR"] }).filter((record) =>
      record.entity_type.includes("fund"),
    ).length,
  );
  assert.equal(
    counts.geography.BR,
    filterDirectoryRecords(records, { entity_type: ["fund"] }).filter(
      (record) => record.geography.includes("BR"),
    ).length,
  );
  assert.equal(brazilianFunds.length, counts.entity_type.fund);
});

test("directory state has a stable shareable query-string contract", () => {
  const state = parseDirectoryState(
    new URLSearchParams(
      "focus=climate&q=inova%C3%A7%C3%A3o&type=fund&type=accelerator&geo=BR",
    ),
  );
  assert.deepEqual(state, {
    query: "inovação",
    entity_type: ["accelerator", "fund"],
    geography: ["BR"],
    stage: [],
    focus: ["climate"],
  });
  assert.equal(
    serializeDirectoryState(state).toString(),
    "q=inova%C3%A7%C3%A3o&type=accelerator&type=fund&geo=BR&focus=climate",
  );
});

test("landing policy never creates empty or unlimited filter pages", () => {
  assert.equal(LANDING_THRESHOLD, 3);
  assert.deepEqual(
    landingDecision({ dimension: "country", count: 1 }),
    {
      generate: true,
      indexable: true,
      reason: "catalog_navigation",
    },
  );
  assert.deepEqual(
    landingDecision({ dimension: "stage", count: 2 }),
    {
      generate: false,
      indexable: false,
      reason: "below_threshold",
    },
  );
  assert.deepEqual(
    landingDecision({ dimension: "focus", count: 3 }),
    {
      generate: false,
      indexable: false,
      reason: "missing_editorial_introduction",
    },
  );
  assert.deepEqual(
    landingDecision({
      dimension: "focus",
      count: 3,
      introduction: "Editorial copy reviewed for this locale.",
    }),
    {
      generate: true,
      indexable: true,
      reason: "editorial_landing",
    },
  );
});

test("no stage or focus landing is indexable without supplied editorial copy", () => {
  const facetCounts = deriveFacetCounts(records);
  const policy = deriveLandingPolicy({
    category: facetCounts.entity_type,
    country: Object.fromEntries(
      Object.entries(facetCounts.geography).filter(([value]) =>
        /^[A-Z]{2}$/.test(value),
      ),
    ),
    stage: facetCounts.stage,
    focus: facetCounts.focus,
  });

  assert.ok(
    Object.values(policy.category).every(({ indexable }) => indexable),
  );
  assert.ok(Object.values(policy.country).every(({ indexable }) => indexable));
  assert.ok(
    Object.values(policy.stage).every(({ indexable }) => !indexable),
  );
  assert.ok(
    Object.values(policy.focus).every(({ indexable }) => !indexable),
  );
});
