"""Audita URLs oficiais e robots.txt usados pela issue #85."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent
USER_AGENT = "awesome-latam-vc-research/1.0"
TIMEOUT = 20


def load_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def request(url: str) -> dict:
    result = {
        "url": url,
        "status": None,
        "final_url": None,
        "error": None,
        "accessed_on": "2026-07-27",
    }
    try:
        with urlopen(
            Request(url, headers={"User-Agent": USER_AGENT}),
            timeout=TIMEOUT,
        ) as response:
            result["status"] = response.status
            result["final_url"] = response.url
    except HTTPError as error:
        result["status"] = error.code
        result["final_url"] = error.url
        result["error"] = str(error)
    except (URLError, TimeoutError, OSError) as error:
        result["error"] = str(error)
    return result


def dump(path: Path, records: list[dict]) -> None:
    path.write_text(
        json.dumps(records, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> None:
    source_urls = {
        item["initial_url"] for item in load_jsonl(ROOT / "source-inventory.jsonl")
    }
    evidence_urls = {item["url"] for item in load_jsonl(ROOT / "evidence.jsonl")}
    urls = sorted(source_urls | evidence_urls)
    domains = sorted({urlsplit(url).netloc.lower() for url in urls})
    robots_urls = [f"https://{domain}/robots.txt" for domain in domains]
    with ThreadPoolExecutor(max_workers=4) as executor:
        link_rows = sorted(executor.map(request, urls), key=lambda row: row["url"])
        robots_rows = sorted(
            executor.map(request, robots_urls),
            key=lambda row: row["url"],
        )
    dump(ROOT / "link-audit.json", link_rows)
    dump(ROOT / "robots-audit.json", robots_rows)


if __name__ == "__main__":
    main()
