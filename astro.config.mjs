import { defineConfig } from "astro/config";

export default defineConfig({
  site: "https://djairofilho.github.io",
  base: "/awesome-latam-vc",
  output: "static",
  trailingSlash: "always",
  build: {
    format: "directory",
  },
  markdown: {
    syntaxHighlight: false,
  },
});
