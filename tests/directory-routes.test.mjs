import assert from "node:assert/strict";
import test from "node:test";
import {
  categoryRouteSuffix,
  countryDisplayName,
  countryRouteSuffix,
  directoryCountryCodes,
  directoryRecordForProfile,
  profileHistoryUrl,
  profileRouteSuffix,
} from "../src/lib/directory-routes.mjs";

const profile = {
  id: "fund:example",
  slug: "example",
  name: "Example",
  summary: "Example fund.",
  aliases: [],
  operator: null,
  category: "fund",
  baseGeography: { kind: "country", code: "BR" },
  countriesCovered: ["BR", "LATAM"],
  stages: ["seed"],
  focuses: ["climate"],
};

test("directory route suffixes stay symmetric across locales", () => {
  assert.equal(profileRouteSuffix("example"), "/profiles/example/");
  assert.equal(categoryRouteSuffix("fund"), "/categories/fund/");
  assert.equal(countryRouteSuffix("BR"), "/countries/br/");
  assert.equal(
    directoryRecordForProfile(profile, "pt-BR").href,
    "/awesome-latam-vc/pt-br/profiles/example/",
  );
});

test("country landings only derive real ISO country codes", () => {
  const record = directoryRecordForProfile(profile, "en");
  assert.deepEqual(directoryCountryCodes([record]), ["BR"]);
  assert.equal(countryDisplayName("pt-BR", "BR"), "Brasil");
  assert.equal(countryDisplayName("es", "MX"), "México");
});

test("profile history links encode every canonical path segment", () => {
  assert.equal(
    profileHistoryUrl("funds/brasil/fundo com espaço.md"),
    "https://github.com/djairofilho/awesome-latam-vc/commits/main/funds/brasil/fundo%20com%20espa%C3%A7o.md",
  );
});
