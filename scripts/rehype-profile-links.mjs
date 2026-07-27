import { profileMarkdownHref } from "../src/lib/directory-routes.mjs";

function rewriteLinks(node) {
  if (
    node?.type === "element" &&
    node.tagName === "a" &&
    typeof node.properties?.href === "string"
  ) {
    node.properties.href = profileMarkdownHref(node.properties.href);
  }
  for (const child of node?.children ?? []) {
    rewriteLinks(child);
  }
}

export function rehypeProfileLinks() {
  return (tree, file) => {
    const sourcePath = String(file.path ?? "").replaceAll("\\", "/");
    if (
      sourcePath.includes("/funds/") ||
      sourcePath.includes("/ecosystem/")
    ) {
      rewriteLinks(tree);
    }
  };
}
