"""Audit inventory links and robots.txt without bypassing access controls."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from pathlib import Path


ROOT = Path(__file__).parent
USER_AGENT = "awesome-latam-vc-research/1.0"
TIMEOUT_SECONDS = 20
MINIMUM_DELAY_SECONDS = 0.5


def load_sources() -> list[dict]:
    return [
        json.loads(line)
        for line in (ROOT / "source-inventory.jsonl").read_text(encoding="utf-8").splitlines()
        if line
    ]


def fetch_status(url: str) -> tuple[int | None, str | None, str | None]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            body = response.read().decode("utf-8", errors="replace")
            return response.status, None, body
    except urllib.error.HTTPError as error:
        return error.code, f"HTTP {error.code}", None
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        return None, str(error), None


def audit(source: dict, last_request: dict[str, float]) -> dict:
    url = source["initial_url"]
    parsed = urllib.parse.urlsplit(url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    robots_url = f"{origin}/robots.txt"
    elapsed = time.monotonic() - last_request.get(parsed.netloc, 0.0)
    if elapsed < MINIMUM_DELAY_SECONDS:
        time.sleep(MINIMUM_DELAY_SECONDS - elapsed)
    robots_status, robots_error, robots_body = fetch_status(robots_url)
    last_request[parsed.netloc] = time.monotonic()

    parser = urllib.robotparser.RobotFileParser(robots_url)
    robots_allowed: bool | None
    if robots_status is not None and 200 <= robots_status < 300:
        try:
            parser.parse((robots_body or "").splitlines())
            robots_allowed = parser.can_fetch(USER_AGENT, url)
        except (urllib.error.URLError, OSError):
            robots_allowed = None
    elif robots_status == 404:
        robots_allowed = True
    else:
        robots_allowed = None

    link_status = None
    link_error = None
    if robots_allowed is not False:
        elapsed = time.monotonic() - last_request.get(parsed.netloc, 0.0)
        if elapsed < MINIMUM_DELAY_SECONDS:
            time.sleep(MINIMUM_DELAY_SECONDS - elapsed)
        link_status, link_error, _ = fetch_status(url)
        last_request[parsed.netloc] = time.monotonic()

    return {
        "source_id": source["source_id"],
        "url": url,
        "checked_on": "2026-07-27",
        "robots_url": robots_url,
        "robots_http_status": robots_status,
        "robots_allowed": robots_allowed,
        "robots_error": robots_error,
        "link_http_status": link_status,
        "link_error": link_error,
        "access_control_bypassed": False,
    }


def main() -> None:
    last_request: dict[str, float] = {}
    records = [audit(source, last_request) for source in load_sources()]
    output = "".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
        for record in sorted(records, key=lambda item: item["source_id"])
    )
    (ROOT / "link-audit.jsonl").write_text(output, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
