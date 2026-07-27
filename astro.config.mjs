import { defineConfig } from "astro/config";
import { unified } from "@astrojs/markdown-remark";
import { rehypeProfileLinks } from "./scripts/rehype-profile-links.mjs";

export default defineConfig({
  site: "https://djairofilho.github.io",
  base: "/awesome-latam-vc",
  output: "static",
  trailingSlash: "always",
  markdown: {
    processor: unified({
      rehypePlugins: [rehypeProfileLinks],
    }),
    syntaxHighlight: false,
  },
  build: {
    format: "directory",
  },
});
