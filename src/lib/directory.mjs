export const FACET_DIMENSIONS = [
  "entity_type",
  "geography",
  "stage",
  "focus",
];

const STATE_KEYS = {
  entity_type: "type",
  geography: "geo",
  stage: "stage",
  focus: "focus",
};

export function directoryParameterName(dimension) {
  if (!FACET_DIMENSIONS.includes(dimension)) {
    throw new TypeError(`Unsupported facet dimension: ${dimension}`);
  }
  return STATE_KEYS[dimension];
}

export function foldSearchText(value = "") {
  return value
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .toLocaleLowerCase()
    .replace(/\s+/g, " ")
    .trim();
}

function values(value) {
  if (Array.isArray(value)) {
    return value;
  }
  return value == null ? [] : [value];
}

export function directoryRecord(entity) {
  const geography = new Set([
    entity.base_geography?.code,
    ...values(entity.countries_covered),
  ]);
  geography.delete(undefined);
  geography.delete("NOT_DISCLOSED");

  const record = {
    id: entity.id,
    name: entity.name,
    summary: entity.summary ?? "",
    aliases: values(entity.aliases),
    operator: entity.operator ?? "",
    entity_type: values(entity.entity_type),
    geography: [...geography].sort(),
    stage: values(entity.stages),
    focus: values(entity.focuses),
  };
  record.searchText = foldSearchText(
    [
      record.name,
      record.summary,
      record.operator,
      ...record.aliases,
      ...record.geography,
      ...record.stage,
      ...record.focus,
    ].join(" "),
  );
  return record;
}

export function emptyDirectoryState() {
  return {
    query: "",
    entity_type: [],
    geography: [],
    stage: [],
    focus: [],
  };
}

function uniqueSorted(items) {
  return [...new Set(items.filter(Boolean))].sort();
}

export function normalizeDirectoryState(state = {}) {
  const normalized = emptyDirectoryState();
  normalized.query = String(state.query ?? "").trim();
  for (const dimension of FACET_DIMENSIONS) {
    normalized[dimension] = uniqueSorted(values(state[dimension]));
  }
  return normalized;
}

export function parseDirectoryState(searchParams) {
  const state = emptyDirectoryState();
  state.query = searchParams.get("q")?.trim() ?? "";
  for (const dimension of FACET_DIMENSIONS) {
    state[dimension] = uniqueSorted(
      searchParams
        .getAll(STATE_KEYS[dimension])
        .flatMap((value) => value.split(","))
        .map((value) => value.trim()),
    );
  }
  return state;
}

export function serializeDirectoryState(state) {
  const normalized = normalizeDirectoryState(state);
  const searchParams = new URLSearchParams();
  if (normalized.query) {
    searchParams.set("q", normalized.query);
  }
  for (const dimension of FACET_DIMENSIONS) {
    for (const value of normalized[dimension]) {
      searchParams.append(STATE_KEYS[dimension], value);
    }
  }
  return searchParams;
}

function matchesDimension(record, selected, dimension) {
  return (
    selected.length === 0 ||
    selected.some((value) => record[dimension].includes(value))
  );
}

export function filterDirectoryRecords(records, state = {}) {
  const normalized = normalizeDirectoryState(state);
  const query = foldSearchText(normalized.query);
  return records.filter(
    (record) =>
      (!query || record.searchText.includes(query)) &&
      FACET_DIMENSIONS.every((dimension) =>
        matchesDimension(record, normalized[dimension], dimension),
      ),
  );
}

export function deriveFacetValues(records) {
  return Object.fromEntries(
    FACET_DIMENSIONS.map((dimension) => [
      dimension,
      uniqueSorted(records.flatMap((record) => record[dimension])),
    ]),
  );
}

export function deriveFacetCounts(records, state = {}) {
  const normalized = normalizeDirectoryState(state);
  const facets = deriveFacetValues(records);
  return Object.fromEntries(
    FACET_DIMENSIONS.map((dimension) => {
      const withoutCurrentDimension = {
        ...normalized,
        [dimension]: [],
      };
      const eligibleRecords = filterDirectoryRecords(
        records,
        withoutCurrentDimension,
      );
      return [
        dimension,
        Object.fromEntries(
          facets[dimension].map((value) => [
            value,
            eligibleRecords.filter((record) =>
              record[dimension].includes(value),
            ).length,
          ]),
        ),
      ];
    }),
  );
}

export function pagefindFilters(state = {}) {
  const normalized = normalizeDirectoryState(state);
  return Object.fromEntries(
    FACET_DIMENSIONS.flatMap((dimension) => {
      const selected = normalized[dimension];
      if (selected.length === 0) {
        return [];
      }
      return [
        [
          dimension,
          selected.length === 1 ? selected[0] : { any: selected },
        ],
      ];
    }),
  );
}
