"""Audita estruturalmente e, opcionalmente, por HTTP os links do bundle."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import ssl
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent
FILES = (
    "agencies.jsonl",
    "programs.jsonl",
    "calls.jsonl",
    "evidence.jsonl",
    "coverage-matrix.jsonl",
)
URL_FIELDS = ("official_site", "official_url", "route_url", "url", "initial_url")
OFFICIAL_SUFFIXES = (
    "bdp.com.bo",
    "produccion.gob.bo",
    "probolivia.gob.bo",
    "gob.bo",
    "lapaz.bo",
    "sena.edu.co",
    "mincit.gov.co",
    "bancoldex.com",
    "innpulsacolombia.com",
    "rutanmedellin.org",
    "educacionsuperior.gob.ec",
    "produccion.gob.ec",
    "cfn.fin.ec",
    "gob.ec",
    "conquito.org.ec",
    "quitoinforma.gob.ec",
    "gob.pe",
    "proinnovate.gob.pe",
    "proinnovate.gob.pe",
    "cofide.com.pe",
    "produce.gob.pe",
    "fonacit.gob.ve",
    "mincyt.gob.ve",
    "bandes.gob.ve",
    "miranda.gob.ve",
)


def load_urls() -> list[str]:
    urls: set[str] = set()
    for filename in FILES:
        for raw in (ROOT / filename).read_text(encoding="utf-8").splitlines():
            if not raw.strip():
                continue
            record = json.loads(raw)
            for field in URL_FIELDS:
                value = record.get(field)
                if isinstance(value, str):
                    urls.add(value)
    return sorted(urls)


def is_official(host: str) -> bool:
    return any(host == suffix or host.endswith("." + suffix) for suffix in OFFICIAL_SUFFIXES)


def request_status(url: str) -> tuple[str, str]:
    request = urllib.request.Request(url, headers={"User-Agent": "awesome-latam-vc-link-audit/1.0"})
    try:
        with urllib.request.urlopen(
            request,
            timeout=20,
            context=ssl.create_default_context(),
        ) as response:
            return "ok", str(response.status)
    except urllib.error.HTTPError as exc:
        if exc.code in {401, 403, 405, 429} or 500 <= exc.code < 600:
            return "não verificável", f"HTTP {exc.code}"
        return "quebrado", f"HTTP {exc.code}"
    except (OSError, urllib.error.URLError) as exc:
        return "não verificável", type(exc).__name__


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="também consulta cada URL")
    args = parser.parse_args()
    urls = load_urls()
    failures: list[str] = []
    live_results = {"ok": 0, "quebrado": 0, "não verificável": 0}
    valid_urls: list[str] = []
    for url in urls:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        if parsed.scheme != "https":
            failures.append(f"esquema não HTTPS: {url}")
        if not host or not is_official(host):
            failures.append(f"domínio não oficial: {url}")
        else:
            valid_urls.append(url)
    if args.live:
        with ThreadPoolExecutor(max_workers=12) as executor:
            results = executor.map(request_status, valid_urls)
        for url, (result, detail) in zip(valid_urls, results, strict=True):
            live_results[result] += 1
            print(f"{result}\t{detail}\t{url}")
            if result == "quebrado":
                failures.append(f"link quebrado ({detail}): {url}")
    if failures:
        print("Auditoria de links falhou:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(f"Auditoria estrutural passou: {len(urls)} links oficiais HTTPS.")
    if args.live:
        print(
            "Auditoria HTTP: "
            + ", ".join(f"{key}={value}" for key, value in live_results.items())
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
