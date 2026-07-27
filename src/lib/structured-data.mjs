import { canonicalUrl } from "./paths.mjs";

export const SCHEMA_CONTEXT = "https://schema.org";
export const DATASET_VERSION = "2026-07-27";
export const DATASET_DATE = "2026-07-27";
export const DATASET_LICENSE =
  "https://creativecommons.org/publicdomain/zero/1.0/";

export function webSiteJsonLd() {
  return {
    "@type": "WebSite",
    "@id": `${canonicalUrl("/")}#website`,
    url: canonicalUrl("/"),
    name: "Awesome LatAm VC",
    description:
      "An open, source-backed directory of venture funds and startup funding programs across Latin America.",
    inLanguage: "en",
  };
}

export function datasetJsonLd(entityCount) {
  return {
    "@type": "Dataset",
    "@id": `${canonicalUrl("/data/entities.json")}#dataset`,
    name: "Awesome LatAm VC catalog entities",
    description:
      "Canonical metadata for venture funds and startup funding programs across Latin America.",
    url: canonicalUrl("/catalog/"),
    version: DATASET_VERSION,
    datePublished: DATASET_DATE,
    dateModified: DATASET_DATE,
    license: DATASET_LICENSE,
    inLanguage: "en",
    variableMeasured: {
      "@type": "PropertyValue",
      name: "Entity count",
      value: entityCount,
    },
    distribution: [
      {
        "@type": "DataDownload",
        encodingFormat: "application/json",
        contentUrl: canonicalUrl("/data/entities.json"),
      },
      {
        "@type": "DataDownload",
        encodingFormat: "text/csv",
        contentUrl: canonicalUrl("/data/entities.csv"),
      },
    ],
  };
}

export function breadcrumbListJsonLd(items) {
  return {
    "@type": "BreadcrumbList",
    itemListElement: items.map(({ name, path }, index) => ({
      "@type": "ListItem",
      position: index + 1,
      name,
      item: canonicalUrl(path),
    })),
  };
}

export function organizationJsonLd(profile) {
  const publicAgency =
    profile.category === "public_program" && profile.operator === null;
  if (profile.category === "public_program" && !publicAgency) {
    return null;
  }

  const organization = {
    "@type": publicAgency ? "GovernmentOrganization" : "Organization",
    "@id": profile.sourceUrl,
    name: profile.name,
    url: profile.sourceUrl,
  };
  if (profile.summary) {
    organization.description = profile.summary;
  }
  if (profile.officialWebsite) {
    organization.sameAs = profile.officialWebsite;
  }
  return organization;
}

export function jsonLdDocument(nodes) {
  return {
    "@context": SCHEMA_CONTEXT,
    "@graph": nodes.filter(Boolean),
  };
}

export function serializeJsonLd(nodes) {
  return JSON.stringify(jsonLdDocument(nodes)).replaceAll("<", "\\u003c");
}
