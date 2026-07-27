export const SITE_ORIGIN = "https://djairofilho.github.io";
export const SITE_BASE = "/awesome-latam-vc";

export function withBase(pathname = "/") {
  const normalized = pathname.startsWith("/") ? pathname : `/${pathname}`;
  if (normalized === "/") {
    return `${SITE_BASE}/`;
  }
  return `${SITE_BASE}${normalized}`.replace(/\/+$/, "/");
}

export function canonicalUrl(pathname = "/") {
  return new URL(withBase(pathname), SITE_ORIGIN).href;
}
