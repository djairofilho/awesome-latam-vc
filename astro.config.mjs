import { defineConfig } from "astro/config";
import { rehypeProfileLinks } from "./scripts/rehype-profile-links.mjs";

export default defineConfig({
  site: "https://djairofilho.github.io",
  base: "/awesome-latam-vc",
  output: "static",
  trailingSlash: "always",
  markdown: {
    rehypePlugins: [rehypeProfileLinks],
    syntaxHighlight: false,
  },
  build: {
    format: "directory",
  },
});
