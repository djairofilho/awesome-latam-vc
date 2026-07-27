import assert from "node:assert/strict";
import test from "node:test";
import {
  loadPagefind,
  normalizePagefindQuery,
  normalizeSearchLocale,
  pagefindBundlePath,
  pagefindModulePath,
  searchPagefind,
} from "../src/lib/pagefind-client.mjs";

test("Pagefind paths preserve the GitHub Pages base", () => {
  assert.equal(
    pagefindBundlePath(),
    "/awesome-latam-vc/pagefind/",
  );
  assert.equal(
    pagefindModulePath(),
    "/awesome-latam-vc/pagefind/pagefind.js",
  );
});

test("Pagefind initializes against the current supported document locale", async () => {
  const calls = [];
  const pagefind = {
    async options(options) {
      calls.push(["options", options]);
    },
    async init() {
      calls.push(["init"]);
    },
  };
  const loaded = await loadPagefind({
    documentElement: { lang: "pt-BR" },
    importer: async (path) => {
      calls.push(["import", path]);
      return pagefind;
    },
  });

  assert.equal(loaded, pagefind);
  assert.equal(normalizeSearchLocale("pt-BR"), "pt-br");
  assert.deepEqual(calls, [
    ["import", "/awesome-latam-vc/pagefind/pagefind.js"],
    ["options", { bundlePath: "/awesome-latam-vc/pagefind/" }],
    ["init"],
  ]);
  await assert.rejects(
    loadPagefind({
      documentElement: { lang: "fr" },
      importer: async () => pagefind,
    }),
    /Unsupported Pagefind document language: fr/,
  );
});

test("Pagefind preserves accents while normalizing query whitespace", () => {
  assert.equal(
    normalizePagefindQuery("  inovação   México  "),
    "inovação México",
  );
});

test("Pagefind receives compound filters and hydrates result data", async () => {
  const calls = [];
  const pagefind = {
    async debouncedSearch(query, options, timeout) {
      calls.push({ query, options, timeout });
      return {
        results: [
          {
            async data() {
              return { url: "/pt-br/perfis/exemplo/", meta: { title: "A" } };
            },
          },
        ],
        filters: { geography: { BR: 1 } },
        unfilteredResultCount: 2,
      };
    },
  };
  const response = await searchPagefind(pagefind, {
    query: "  inovação ",
    entity_type: ["fund", "accelerator"],
    geography: ["BR"],
  });

  assert.deepEqual(calls, [
    {
      query: "inovação",
      options: {
        filters: {
          entity_type: { any: ["accelerator", "fund"] },
          geography: "BR",
        },
      },
      timeout: 200,
    },
  ]);
  assert.equal(response.cancelled, false);
  assert.equal(response.results[0].meta.title, "A");
  assert.deepEqual(response.filters, { geography: { BR: 1 } });
  assert.equal(response.unfilteredResultCount, 2);
});

test("Pagefind supports filter-only and cancelled searches", async () => {
  const filterOnly = {
    async search(query, options) {
      assert.equal(query, null);
      assert.deepEqual(options, { filters: { stage: "seed" } });
      return { results: [] };
    },
  };
  assert.equal(
    (await searchPagefind(filterOnly, { stage: ["seed"] })).cancelled,
    false,
  );

  const cancelled = {
    async debouncedSearch() {
      return null;
    },
  };
  assert.equal(
    (await searchPagefind(cancelled, { query: "fund" })).cancelled,
    true,
  );
});
