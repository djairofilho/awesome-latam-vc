import type { APIRoute } from "astro";
import { readFileSync } from "node:fs";
import { join } from "node:path";

export const prerender = true;

export const GET: APIRoute = () =>
  new Response(readFileSync(join(process.cwd(), "data", "entities.json")), {
    headers: {
      "Content-Type": "application/json; charset=utf-8",
    },
  });
