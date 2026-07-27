"""Audita sintaxe, domínio oficial e disponibilidade dos links do bundle."""

from __future__ import annotations

import argparse
import concurrent.futures
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
OFFICIAL_SUFFIXES = (
    "gob.mx",
    "secihti.mx",
    "nafin.com",
    "innovafest.mx",
)
REACHABLE_BLOCKS = {401, 403, 405, 429}


def collect_urls() -> list[str]:
    urls: set[str] = set()
    for filename in FILES:
        for line in (ROOT / filename).read_text(encoding="utf-8").splitlines():
            record = json.loads(line)
            for value in record.values():
                if isinstance(value, str) and value.startswith(("http://", "https://")):
                    urls.add(value)
    return sorted(urls)


def validate_official_url(url: str) -> str | None:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname:
        return f"URL no HTTPS o sin dominio: {url}"
    hostname = parsed.hostname.lower()
    if not any(hostname == suffix or hostname.endswith("." + suffix) for suffix in OFFICIAL_SUFFIXES):
        return f"Dominio fuera del inventario oficial: {url}"
    return None


def live_status(url: str) -> tuple[str, int | None]:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "awesome-latam-vc-link-audit/1.0"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(
            request,
            timeout=8,
            context=ssl.create_default_context(),
        ) as response:
            return "ok", response.status
    except urllib.error.HTTPError as error:
        if error.code in REACHABLE_BLOCKS:
            return "bloqueado, pero alcanzable", error.code
        return "enlace roto HTTP", error.code
    except (urllib.error.URLError, TimeoutError) as error:
        return (
            f"no verificable por transporte: "
            f"{error.reason if hasattr(error, 'reason') else error}",
            None,
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Consulta cada URL por HTTP.")
    args = parser.parse_args()
    urls = collect_urls()
    errors = [error for url in urls if (error := validate_official_url(url))]
    if errors:
        print("\n".join(errors))
        return 1

    live_errors = 0
    if args.live:
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            results = dict(zip(urls, executor.map(live_status, urls)))
        for url in urls:
            result, status = results[url]
            print(f"{status or '-'}\t{result}\t{url}")
            if result.startswith("enlace roto"):
                live_errors += 1
    print(f"Links auditados: {len(urls)}")
    return 1 if live_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
