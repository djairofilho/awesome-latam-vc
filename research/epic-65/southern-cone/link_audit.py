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
FILES = ("agencies.jsonl", "programs.jsonl", "calls.jsonl", "evidence.jsonl",
         "coverage-matrix.jsonl")
OFFICIAL_SUFFIXES = (
    "argentina.gob.ar", "bice.com.ar", "innovaryemprendercba.com.ar",
    "corfo.cl", "startupchile.org", "sercotec.cl", "economia.gob.cl",
    "bancoestado.cl", "gorebiobio.cl", "conacyt.gov.py", "mic.gov.py",
    "afd.gov.py", "asuncion.gov.py", "anii.org.uy", "ande.org.uy",
    "gub.uy", "brou.com.uy",
)
REACHABLE_BLOCKS = {401, 403, 405, 429}


def urls() -> list[str]:
    found = set()
    for filename in FILES:
        for line in (ROOT / filename).read_text(encoding="utf-8").splitlines():
            for value in json.loads(line).values():
                if isinstance(value, str) and value.startswith(("http://", "https://")):
                    found.add(value)
    return sorted(found)


def validate(url: str) -> str | None:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or not host:
        return f"URL não HTTPS ou sem domínio: {url}"
    if not any(host == suffix or host.endswith("." + suffix) for suffix in OFFICIAL_SUFFIXES):
        return f"Domínio fora do inventário oficial: {url}"
    return None


def fetch(url: str) -> tuple[str, int | None]:
    request = urllib.request.Request(
        url, headers={"User-Agent": "awesome-latam-vc-link-audit/1.0"}, method="GET"
    )
    try:
        with urllib.request.urlopen(
            request, timeout=10, context=ssl.create_default_context()
        ) as response:
            return "ok", response.status
    except urllib.error.HTTPError as error:
        if error.code in REACHABLE_BLOCKS:
            return "bloqueado, mas alcançável", error.code
        return "link quebrado HTTP", error.code
    except (urllib.error.URLError, TimeoutError) as error:
        detail = error.reason if hasattr(error, "reason") else error
        return f"não verificável por transporte: {detail}", None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    links = urls()
    errors = [message for link in links if (message := validate(link))]
    if errors:
        print("\n".join(errors))
        return 1
    broken = 0
    if args.live:
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            results = dict(zip(links, pool.map(fetch, links)))
        for link in links:
            result, status = results[link]
            print(f"{status or '-'}\t{result}\t{link}")
            broken += result.startswith("link quebrado")
    print(f"Links auditados: {len(links)}")
    return 1 if broken else 0


if __name__ == "__main__":
    raise SystemExit(main())
