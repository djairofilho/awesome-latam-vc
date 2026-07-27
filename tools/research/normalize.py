"""Normalization and baseline import helpers for Epic 16 research."""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import urlsplit


HEADING_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
WEBSITE_RE = re.compile(r"^-\s+\*\*Website:\*\*\s+(.+?)\s*$", re.MULTILINE)
MARKDOWN_URL_RE = re.compile(r"\[[^\]]+\]\((https?://[^)]+)\)")
PLAIN_URL_RE = re.compile(r"https?://\S+")
README_FUND_RE = re.compile(r"\[([^\]]+)\]\((funds/[^)]+\.md)\)")
PARENTHETICAL_RE = re.compile(r"\s+\((?:ex-|formerly\s+)([^)]+)\)", re.IGNORECASE)


def normalize_domain(value: str) -> str:
    """Return a stable ASCII hostname without www, port, or trailing dot."""

    candidate = value.strip()
    if not candidate:
        return ""
    if " " in candidate and "://" not in candidate:
        return ""
    parsed = urlsplit(candidate if "://" in candidate else f"//{candidate}")
    hostname = parsed.hostname
    if not hostname:
        return ""
    hostname = hostname.rstrip(".").lower()
    if hostname.startswith("www."):
        hostname = hostname[4:]
    try:
        return hostname.encode("idna").decode("ascii")
    except UnicodeError:
        return hostname


def normalize_alias(value: str) -> str:
    """Normalize a display name for lookup without changing its identity."""

    decomposed = unicodedata.normalize("NFKD", value)
    ascii_value = "".join(char for char in decomposed if not unicodedata.combining(char))
    return " ".join(re.sub(r"[^a-zA-Z0-9]+", " ", ascii_value).lower().split())


def name_aliases(name: str) -> list[str]:
    """Build conservative lookup aliases from a profile name.

    Parenthetical former names are searchable, but remain attached to the
    original profile. This function never decides that two profiles are the
    same vehicle.
    """

    candidates = [name]
    candidates.extend(PARENTHETICAL_RE.findall(name))
    without_former_name = PARENTHETICAL_RE.sub("", name).strip()
    if without_former_name != name:
        candidates.append(without_former_name)
    return list(dict.fromkeys(alias for item in candidates if (alias := normalize_alias(item))))


@dataclass(frozen=True)
class BaselineFund:
    profile_path: str
    name: str
    website: str
    domain: str
    aliases: list[str]


def _read_profile(path: Path, root: Path) -> BaselineFund:
    text = path.read_text(encoding="utf-8")
    heading = HEADING_RE.search(text)
    website = WEBSITE_RE.search(text)
    if not heading:
        raise ValueError(f"missing profile heading: {path}")
    if not website:
        raise ValueError(f"missing Website field: {path}")
    website_value = website.group(1).strip()
    markdown_url = MARKDOWN_URL_RE.search(website_value)
    plain_url = PLAIN_URL_RE.search(website_value)
    if markdown_url:
        raw_website = markdown_url.group(1)
    elif plain_url:
        raw_website = plain_url.group(0).rstrip(").,")
    else:
        raw_website = website_value
    name = heading.group(1).strip()
    return BaselineFund(
        profile_path=path.relative_to(root).as_posix(),
        name=name,
        website=raw_website,
        domain=normalize_domain(raw_website),
        aliases=name_aliases(name),
    )


def import_baseline(root: str | Path) -> list[BaselineFund]:
    """Import funds referenced by README.md without merging shared domains."""

    repository = Path(root).resolve()
    readme = repository / "README.md"
    if not readme.is_file():
        raise FileNotFoundError(f"README.md not found under {repository}")
    references = {
        relative_path
        for _, relative_path in README_FUND_RE.findall(readme.read_text(encoding="utf-8"))
    }
    if not references:
        raise ValueError("README.md does not reference any fund profiles")
    funds = [_read_profile(repository / relative_path, repository) for relative_path in references]
    return sorted(funds, key=lambda fund: fund.profile_path)


def baseline_json(root: str | Path) -> list[dict[str, object]]:
    return [asdict(fund) for fund in import_baseline(root)]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    domain_parser = subparsers.add_parser("domain", help="normalize a URL or hostname")
    domain_parser.add_argument("value")

    alias_parser = subparsers.add_parser("alias", help="normalize a fund name")
    alias_parser.add_argument("value")

    baseline_parser = subparsers.add_parser(
        "baseline", help="export the README/funds baseline as JSON"
    )
    baseline_parser.add_argument("--root", default=".", help="repository root")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "domain":
        print(normalize_domain(args.value))
    elif args.command == "alias":
        print(normalize_alias(args.value))
    else:
        print(json.dumps(baseline_json(args.root), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
