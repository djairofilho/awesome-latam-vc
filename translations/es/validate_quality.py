#!/usr/bin/env python3
"""Reject unequivocal untranslated fragments and known Spanish calques."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TRANSLATIONS = ROOT / "translations" / "es"
MOJIBAKE = re.compile(r"Ã.|Â.|â€|â€™|â€œ|â€|�|[^\W\d_]\?[^\W\d_]")
PLACEHOLDER = re.compile(r"ZXQMASK\d+QXZ", re.IGNORECASE)
PORTUGUESE = re.compile(
    r"\b(?:não|ações|informações|investimentos|empreendimentos|"
    r"fontes revisadas|até|também|público-alvo|serviços|inovação|"
    r"negócios|investimento|investidores)\b|(?:^|\n)O\s+(?=[A-ZÁÉÍÓÚ])",
    re.IGNORECASE,
)
ENGLISH_PROSE = re.compile(
    r"\b(?:weeks?|months?|years?|up to|not publicly disclosed|"
    r"reviewed sources|invests?|investments?|investions|backs|"
    r"seeks?|leads?|co-leads?|rounds?|using|automate|traditional "
    r"industries|for|equity|stake|launch|million)\b",
    re.IGNORECASE,
)
ENGLISH_MARKDOWN = re.compile(
    r"^(?:#{2,6}\s+(?:Investment profile|Portfolio signals|Declared thesis|"
    r"Sources|Official sources|Program profile|Eligibility and application|"
    r"Activity signals)|-\s+\*\*(?:Website|Fund type|Stage at entry|"
    r"Follow-on stages|Focus|Geography|Initial check|Investment role|"
    r"Business models|Portfolio size|Selected companies|Submit a startup|"
    r"Last verified):\*\*)",
    re.MULTILINE,
)
STRAY_ENGLISH_CONNECTOR = re.compile(r"\b(?:as|at)\b", re.IGNORECASE)
DOUBLE_INTERNAL_SPACE = re.compile(r"(?<=\S) {2,}(?=\S)")
UNGRAMMATICAL_DISCLOSURE = re.compile(r"\bNo divulgado\b", re.IGNORECASE)
PROTECTED_OFFICIAL_PHRASES = ("PIPE Invest", "Equity")
BARE_REFERENCE = re.compile(
    r"(?<![\w@])(?:"
    r"(?:[a-z0-9-]+\.)+[a-z]{2,}"
    r"|(?:funds|accelerators|public-programs|angel-networks|"
    r"funding-platforms)/[\w./:-]+"
    r")(?:[/?#][^\s;,)]+)?",
    re.IGNORECASE,
)
KNOWN_CALQUES = (
    "revisión congelada",
    "señales portfolio",
    "portfolio señales",
    "portfolio tamaño",
    "verificación inicial",
    "enviar un startup",
    "inversión de arranque directa",
)


def parse(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(\{[\s\S]*?\})\n---\n([\s\S]+)$", text)
    if not match:
        raise ValueError("invalid JSON front matter")
    return json.loads(match.group(1)), match.group(2)


def prose_without_protected_sources(body: str, metadata: dict) -> str:
    cleaned = body
    for source in metadata["sources"]:
        cleaned = cleaned.replace(
            f"[{source['title']}]({source['url']})",
            "",
        )
    for phrase in PROTECTED_OFFICIAL_PHRASES:
        cleaned = cleaned.replace(phrase, "")
    identity_terms = [
        metadata.get("name"),
        metadata.get("operator"),
        *metadata.get("aliases", []),
        *metadata["protected_terms"],
    ]
    for term in filter(None, identity_terms):
        cleaned = cleaned.replace(term, "")
    cleaned = re.sub(r"`[^`\n]+`", "", cleaned)
    cleaned = BARE_REFERENCE.sub("", cleaned)
    return re.sub(r"https://[^\s)>]+", "", cleaned)


def style_text_without_sources(body: str, metadata: dict) -> str:
    """Keep names for spacing checks while excluding source titles and URLs."""
    cleaned = body
    for source in metadata["sources"]:
        cleaned = cleaned.replace(
            f"[{source['title']}]({source['url']})",
            "[fuente]",
        )
    return re.sub(r"https://[^\s)>]+", "[url]", cleaned)


def validate(path: Path) -> list[str]:
    metadata, body = parse(path)
    prose = prose_without_protected_sources(body, metadata)
    style_text = (
        metadata.get("summary", "")
        + "\n"
        + style_text_without_sources(body, metadata)
    )
    errors = []
    if MOJIBAKE.search(prose):
        errors.append("contains mojibake")
    if PLACEHOLDER.search(prose):
        errors.append("contains a translation placeholder")
    if PORTUGUESE.search(prose):
        errors.append("contains an unequivocal Portuguese fragment")
    if ENGLISH_MARKDOWN.search(prose):
        errors.append("contains an untranslated English heading or label")
    if ENGLISH_PROSE.search(prose):
        errors.append("contains an unequivocal English fragment")
    if STRAY_ENGLISH_CONNECTOR.search(prose):
        errors.append("contains a stray English connector")
    if DOUBLE_INTERNAL_SPACE.search(style_text):
        errors.append("contains a repeated internal space")
    if UNGRAMMATICAL_DISCLOSURE.search(prose):
        errors.append("contains ungrammatical disclosure wording")
    folded = prose.casefold()
    for phrase in KNOWN_CALQUES:
        if phrase in folded:
            errors.append(f"contains known calque: {phrase}")
    if metadata["locale"] != "es":
        errors.append("locale is not es")
    return errors


def main() -> int:
    paths = sorted(
        path
        for path in TRANSLATIONS.rglob("*.md")
        if not path.name.startswith("README")
    )
    errors = []
    for path in paths:
        try:
            findings = validate(path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            findings = [str(exc)]
        errors.extend(
            f"{path.relative_to(ROOT).as_posix()}: {finding}"
            for finding in findings
        )
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Spanish translation quality gate passed for {len(paths)} profiles.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
