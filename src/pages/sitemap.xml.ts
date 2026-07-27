import type { APIRoute } from "astro";
import { getCollection } from "astro:content";
import type { Locale } from "../i18n/ui";
import {
  hreflangUrls,
  locales,
  localizedRoute,
} from "../lib/i18n.mjs";
import { sitemapXml } from "../lib/seo.mjs";

const supportedLocales = locales as readonly Locale[];

export const GET: APIRoute = async () => {
  const pages = await getCollection("editorialPages");
  const slugs = [...new Set(pages.map((page) => page.data.slug))].sort();
  const editorialRouteGroups = slugs.map((slug) => {
    const availableLocales = supportedLocales.filter((locale) =>
      pages.some(
        (page) => page.data.slug === slug && page.data.locale === locale,
      ),
    );
    const suffix = `/about/${slug}/`;
    return {
      suffix,
      paths: availableLocales.map((locale) =>
        localizedRoute(locale, suffix),
      ),
      alternates: hreflangUrls(suffix, availableLocales),
    };
  });

  return new Response(sitemapXml(editorialRouteGroups), {
    headers: {
      "Content-Type": "application/xml; charset=utf-8",
    },
  });
};
