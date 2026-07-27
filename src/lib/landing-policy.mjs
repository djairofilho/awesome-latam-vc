export const LANDING_THRESHOLD = 3;
export const LANDING_DIMENSIONS = [
  "category",
  "country",
  "stage",
  "focus",
];

const ALWAYS_INDEXABLE = new Set(["category", "country"]);

function hasEditorialIntroduction(introduction) {
  return typeof introduction === "string" && introduction.trim().length > 0;
}

export function landingDecision({
  dimension,
  count,
  introduction,
  threshold = LANDING_THRESHOLD,
}) {
  if (!LANDING_DIMENSIONS.includes(dimension)) {
    throw new TypeError(`Unsupported landing dimension: ${dimension}`);
  }
  if (!Number.isInteger(count) || count < 0) {
    throw new TypeError("Landing count must be a non-negative integer");
  }
  if (count === 0) {
    return { generate: false, indexable: false, reason: "empty" };
  }
  if (ALWAYS_INDEXABLE.has(dimension)) {
    return { generate: true, indexable: true, reason: "catalog_navigation" };
  }
  if (count < threshold) {
    return { generate: false, indexable: false, reason: "below_threshold" };
  }
  if (!hasEditorialIntroduction(introduction)) {
    return {
      generate: false,
      indexable: false,
      reason: "missing_editorial_introduction",
    };
  }
  return { generate: true, indexable: true, reason: "editorial_landing" };
}

export function deriveLandingPolicy(
  counts,
  introductions = {},
  threshold = LANDING_THRESHOLD,
) {
  return Object.fromEntries(
    LANDING_DIMENSIONS.map((dimension) => [
      dimension,
      Object.fromEntries(
        Object.entries(counts[dimension] ?? {})
          .sort(([left], [right]) => left.localeCompare(right))
          .map(([value, count]) => [
            value,
            landingDecision({
              dimension,
              count,
              introduction: introductions[dimension]?.[value],
              threshold,
            }),
          ]),
      ),
    ]),
  );
}
