#!/usr/bin/env python3
"""Generate review-pending Spanish profile translations in deterministic batches."""

from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[2]
TARGET_ROOT = ROOT / "translations" / "es"
CACHE_PATH = ROOT / ".translation-cache-es.json"
MANIFEST_PATH = TARGET_ROOT / "manifest.json"
PROFILE_ROOTS = (ROOT / "funds", ROOT / "ecosystem")
TOKEN_RE = re.compile(r"ZXQMASK(\d{5})QXZ", re.IGNORECASE)
MARIAN_MODEL = None
MARIAN_TOKENIZER = None
EXACT_TRANSLATIONS = {
    "Investment profile": "Perfil de inversión",
    "Portfolio signals": "Señales de cartera",
    "Declared thesis": "Tesis declarada",
    "Sources": "Fuentes",
    "Official sources": "Fuentes oficiales",
    "Eligibility and application": "Elegibilidad y solicitud",
    "Program profile": "Perfil del programa",
    "Activity signals": "Señales de actividad",
    "Calls": "Convocatorias",
    "Agency relationship": "Relación con la agencia",
    "Published programs": "Programas publicados",
    "Products": "Productos",
    "Regulation": "Regulación",
    "Offers observed": "Ofertas observadas",
    "Website": "Sitio web",
    "Fund type": "Tipo de fondo",
    "Direct startup investment": "Inversión directa en startups",
    "Open to external founders": "Abierto a fundadores externos",
    "Stage at entry": "Etapa de entrada",
    "Follow-on stages": "Etapas posteriores",
    "Focus": "Enfoque",
    "Geography": "Geografía",
    "Initial check": "Inversión inicial",
    "Investment role": "Rol de inversión",
    "Business models": "Modelos de negocio",
    "Portfolio size": "Tamaño de la cartera",
    "Selected companies": "Empresas seleccionadas",
    "Submit a startup": "Postular una startup",
    "Last verified": "Última verificación",
    "Aliases": "Alias",
    "Operator": "Operador",
    "Founder route": "Ruta para fundadores",
    "Publication batch": "Lote de publicación",
    "Entity type": "Tipo de entidad",
    "Entity ID": "ID de la entidad",
    "Stage": "Etapa",
    "Instrument": "Instrumento",
    "Investment vehicle": "Vehículo de inversión",
    "Apply": "Postular",
    "Equity": "Participación accionaria",
    "Capital offered": "Capital ofrecido",
    "Activity status": "Estado de actividad",
    "Program type": "Tipo de programa",
    "Application status": "Estado de postulación",
    "Duration": "Duración",
    "Program format": "Formato del programa",
    "Type": "Tipo",
    "Financial support": "Apoyo financiero",
    "Official page": "Página oficial",
    "Activity basis": "Base de actividad",
    "Program status": "Estado del programa",
    "Recent activity": "Actividad reciente",
    "Brand": "Marca",
    "Platform": "Plataforma",
    "Activity": "Actividad",
    "Operator jurisdiction": "Jurisdicción del operador",
    "Operator website": "Sitio web del operador",
    "Status": "Estado",
    "Call ID": "ID de la convocatoria",
    "Call-specific eligibility": "Elegibilidad de la convocatoria",
    "Call-specific benefit": "Beneficio de la convocatoria",
    "Call route": "Enlace de la convocatoria",
    "Snapshot date": "Fecha de corte",
    "Capital": "Capital",
    "Closed or closes on": "Cerrada o cierra el",
    "Decision": "Decisión",
    "Selection": "Selección",
    "Opened on": "Abierta el",
    "Disclosed investment size": "Tamaño de inversión divulgado",
    "Selected Latin American companies": "Empresas latinoamericanas seleccionadas",
    "Selected companies in the local dataset": "Empresas seleccionadas en el conjunto de datos local",
    "Apply as a scientist": "Postular como científico",
    "Apply as an entrepreneur": "Postular como emprendedor",
    "Not publicly disclosed": "No divulgado públicamente",
    "Not publicly disclosed in the reviewed sources": "No divulgado públicamente en las fuentes revisadas",
    "Open": "Abierta",
    "Closed": "Cerrada",
    "Closed between cycles": "Cerrada entre ciclos",
    "None published": "Ninguno publicado",
    "No separately qualifying investment vehicle identified": "No se identificó ningún vehículo de inversión independiente que cumpliera los criterios",
    "The frozen independent review confirmed current official activity with outcome `confirmed`.": "La revisión independiente documentada confirmó actividad oficial vigente con el resultado `confirmed`.",
    "The frozen independent review confirmed current official activity with outcome `confirmed_with_resolution`.": "La revisión independiente documentada confirmó actividad oficial vigente con el resultado `confirmed_with_resolution`.",
    "8 weeks": "8 semanas",
    "Up to USD 1,000,000 in AWS credits": "Hasta USD 1,000,000 en créditos de AWS",
    "Three stages; IGNITE lasts 3 months": "Tres etapas; IGNITE dura 3 meses",
    "Yes": "Sí",
    "No": "No",
    "Pre-seed and Seed": "Presemilla y semilla",
    "Technology startups": "Startups tecnológicas",
}
PROTECTED_PATTERNS = (
    re.compile(r"```[\s\S]*?```"),
    re.compile(r"`[^`\n]+`"),
    re.compile(r"\[[^\]]+\]\([^)]+\)"),
    re.compile(r"https://[^\s)>]+"),
    re.compile(
        r"(?<![/@\w-])(?:[a-z0-9-]+\.)+[a-z]{2,}(?:#[a-z0-9-]+)?",
        re.IGNORECASE,
    ),
    re.compile(r"(?:funds|ecosystem)/[^\s;,)]+"),
    re.compile(r"\b\d{4}-\d{2}-\d{2}\b"),
    re.compile(r"(?:US\$|R\$|MX\$|COP\$|CLP\$|ARS\$|BRL|USD|MXN|COP|CLP|ARS|EUR)"),
    re.compile(r"(?<![\w])[-+]?\d+(?:[.,]\d+)*(?:%|x)?(?![\w])"),
)


def canonical_paths() -> list[Path]:
    paths: list[Path] = []
    for root in PROFILE_ROOTS:
        paths.extend(
            path
            for path in root.rglob("*.md")
            if not path.name.startswith("README")
        )
    return sorted(paths, key=lambda path: path.relative_to(ROOT).as_posix())


def write_manifest(paths: list[Path]) -> None:
    batches = []
    for start in range(0, len(paths), 25):
        batch = paths[start : start + 25]
        batches.append(
            {
                "batch": start // 25 + 1,
                "start": start + 1,
                "end": start + len(batch),
                "paths": [
                    target_path(path).relative_to(ROOT).as_posix()
                    for path in batch
                ],
            }
        )
    MANIFEST_PATH.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "locale": "es",
                "canonical_count": len(paths),
                "batch_size": 25,
                "batches": batches,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )


def parse_profile(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\r?\n(\{[\s\S]*?\})\r?\n---\r?\n([\s\S]+)$", text)
    if not match:
        raise ValueError(f"{path}: invalid JSON front matter")
    return json.loads(match.group(1)), match.group(2)


def load_cache() -> dict[str, str]:
    if not CACHE_PATH.exists():
        return {}
    return json.loads(CACHE_PATH.read_text(encoding="utf-8"))


def save_cache(cache: dict[str, str]) -> None:
    CACHE_PATH.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def request_translation(text: str) -> str:
    data = urlencode(
        {"client": "gtx", "sl": "en", "tl": "es", "dt": "t", "q": text}
    ).encode()
    request = Request(
        "https://translate.googleapis.com/translate_a/single",
        data=data,
        headers={"User-Agent": "awesome-latam-vc-translation/1.0"},
    )
    for attempt in range(6):
        try:
            with urlopen(request, timeout=30) as response:
                payload = json.load(response)
            return "".join(item[0] for item in payload[0] if item[0])
        except (HTTPError, URLError, TimeoutError) as exc:
            if attempt == 5:
                raise RuntimeError(f"translation request failed: {exc}") from exc
            time.sleep(2**attempt)
    raise AssertionError("unreachable")


def marian_translation(text: str) -> str:
    global MARIAN_MODEL, MARIAN_TOKENIZER
    if MARIAN_MODEL is None or MARIAN_TOKENIZER is None:
        from transformers import MarianMTModel, MarianTokenizer

        model_name = "Helsinki-NLP/opus-mt-en-es"
        MARIAN_TOKENIZER = MarianTokenizer.from_pretrained(model_name)
        MARIAN_MODEL = MarianMTModel.from_pretrained(model_name)
    inputs = MARIAN_TOKENIZER([text], return_tensors="pt", padding=True)
    output = MARIAN_MODEL.generate(**inputs, num_beams=1)
    return MARIAN_TOKENIZER.batch_decode(output, skip_special_tokens=True)[0]


def translate(text: str, cache: dict[str, str], engine: str) -> str:
    cache_key = f"{engine}\0{text}"
    if cache_key not in cache:
        if engine == "google":
            cache[cache_key] = request_translation(text)
        elif engine == "argos":
            from argostranslate import translate as argos

            cache[cache_key] = argos.translate(text, "en", "es")
        else:
            cache[cache_key] = marian_translation(text)
        save_cache(cache)
    return cache[cache_key]


def mask_text(text: str, metadata: dict) -> tuple[str, list[str]]:
    spans: list[tuple[int, int]] = []
    protected_literals = [
        metadata["name"],
        *metadata["aliases"],
        *([metadata["operator"]] if metadata["operator"] else []),
        *metadata["protected_terms"],
        *(source["title"] for source in metadata["sources"]),
    ]
    for literal in sorted(set(protected_literals), key=len, reverse=True):
        spans.extend(
            (match.start(), match.end())
            for match in re.finditer(re.escape(literal), text)
        )
    for pattern in PROTECTED_PATTERNS:
        spans.extend((match.start(), match.end()) for match in pattern.finditer(text))

    selected: list[tuple[int, int]] = []
    for start, end in sorted(spans):
        while end < len(text) and text[end].isspace():
            end += 1
        if not selected or start > selected[-1][1]:
            selected.append((start, end))
        else:
            selected[-1] = (selected[-1][0], max(selected[-1][1], end))

    values: list[str] = []
    chunks: list[str] = []
    cursor = 0
    for start, end in selected:
        chunks.append(text[cursor:start])
        token = f"ZXQMASK{len(values):05d}QXZ"
        chunks.append(token)
        values.append(text[start:end])
        cursor = end
    chunks.append(text[cursor:])
    return "".join(chunks), values


def restore_text(text: str, values: list[str]) -> str:
    text = re.sub(
        r"(?<=[a-záéíóúüñ])\.(?=[A-ZÁÉÍÓÚÜÑ])",
        ". ",
        text,
    )
    replacements = {
        "La revisión congelada": "La revisión documentada",
        "la revisión congelada": "la revisión documentada",
        "acceso fundador externo": "acceso para fundadores externos",
        "acceso externo fundador": "acceso para fundadores externos",
        "acceso externo al fundador": "acceso para fundadores externos",
        "acceso externo a fundadores": "acceso para fundadores externos",
        "estado de la aplicación": "estado de la postulación",
        "estatus de aplicación": "estado de la postulación",
        "EE.UU.": "EE. UU.",
        "EE.UU": "EE. UU.",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)

    seen: list[int] = []

    def replace(match: re.Match[str]) -> str:
        index = int(match.group(1))
        if index >= len(values):
            raise ValueError(f"unknown placeholder {match.group(0)}")
        seen.append(index)
        return values[index]

    restored = TOKEN_RE.sub(replace, text)
    if sorted(seen) != list(range(len(values))):
        raise ValueError("translation lost or duplicated protected placeholders")
    return re.sub(
        r"^((?:#\s*){1,6})(?=[^#\s])",
        lambda match: match.group(1).replace(" ", "") + " ",
        restored,
        flags=re.MULTILINE,
    )


def unwrap_prose(body: str) -> str:
    blocks = body.split("\n\n")
    normalized = []
    for block in blocks:
        lines = block.splitlines()
        if (
            len(lines) > 1
            and not any(
                line.lstrip().startswith(("#", "-", "*", ">", "```"))
                for line in lines
            )
        ):
            normalized.append(" ".join(line.strip() for line in lines))
        else:
            normalized.append(block)
    return "\n\n".join(normalized)


def translate_field(
    text: str, metadata: dict, cache: dict[str, str], engine: str
) -> str:
    if text in EXACT_TRANSLATIONS:
        return EXACT_TRANSLATIONS[text]
    masked, values = mask_text(text, metadata)
    translated = translate(masked, cache, engine)
    try:
        return restore_text(translated, values)
    except ValueError:
        pieces = TOKEN_RE.split(masked)
        restored = []
        for index, piece in enumerate(pieces):
            if index % 2:
                restored.append(values[int(piece)])
            elif piece:
                restored.append(
                    restore_text(translate(piece, cache, engine), [])
                )
        return "".join(restored)


def translate_body(
    body: str, metadata: dict, cache: dict[str, str], engine: str
) -> str:
    translated_blocks = []
    for raw_block in unwrap_prose(body).split("\n\n"):
        block = raw_block.strip()
        heading = re.fullmatch(r"(#{1,6})\s+(.+)", block)
        if heading:
            translated_blocks.append(
                f"{heading.group(1)} "
                + translate_field(heading.group(2), metadata, cache, engine)
            )
            continue
        lines = block.splitlines()
        if lines and lines[0].startswith("- "):
            items: list[str] = []
            for line in lines:
                if line.startswith("- "):
                    items.append(line[2:])
                elif items:
                    items[-1] += " " + line.strip()
                else:
                    raise ValueError("list continuation without an item")
            translated_lines = []
            for item in items:
                field = re.fullmatch(r"\*\*(.+?):\*\*\s*(.*)", item)
                if field:
                    label = translate_field(
                        field.group(1), metadata, cache, engine
                    )
                    value = (
                        field.group(2)
                        if field.group(1) == "Selected companies"
                        else translate_field(
                            field.group(2), metadata, cache, engine
                        )
                    )
                    translated_lines.append(f"- **{label}:** {value}")
                else:
                    translated_lines.append(
                        "- " + translate_field(item, metadata, cache, engine)
                    )
            translated_blocks.append("\n".join(translated_lines))
            continue
        verified = re.fullmatch(r"\*\*(.+?):\*\*\s*(.+)", block)
        if verified:
            label = translate_field(verified.group(1), metadata, cache, engine)
            value = translate_field(verified.group(2), metadata, cache, engine)
            translated_blocks.append(f"**{label}:** {value}")
            continue
        translated_blocks.append(translate_field(block, metadata, cache, engine))
    return "\n\n".join(translated_blocks)


def body_units(body: str) -> list[str]:
    units = []
    for raw_block in unwrap_prose(body).split("\n\n"):
        block = raw_block.strip()
        heading = re.fullmatch(r"(#{1,6})\s+(.+)", block)
        if heading:
            units.append(heading.group(2))
            continue
        lines = block.splitlines()
        if lines and lines[0].startswith("- "):
            items: list[str] = []
            for line in lines:
                if line.startswith("- "):
                    items.append(line[2:])
                else:
                    items[-1] += " " + line.strip()
            for item in items:
                field = re.fullmatch(r"\*\*(.+?):\*\*\s*(.*)", item)
                if field:
                    units.extend((field.group(1), field.group(2)))
                else:
                    units.append(item)
            continue
        verified = re.fullmatch(r"\*\*(.+?):\*\*\s*(.+)", block)
        if verified:
            units.extend((verified.group(1), verified.group(2)))
        else:
            units.append(block)
    return units


def prefill_marian(
    sources: list[Path], cache: dict[str, str], batch_size: int = 32
) -> None:
    pending: dict[str, str] = {}
    for source in sources:
        metadata, body = parse_profile(source)
        for text in [metadata["summary"], *body_units(body)]:
            if text in EXACT_TRANSLATIONS:
                continue
            masked, _ = mask_text(text, metadata)
            cache_key = f"marian\0{masked}"
            if cache_key not in cache:
                pending[cache_key] = masked
    if not pending:
        return

    global MARIAN_MODEL, MARIAN_TOKENIZER
    marian_translation("Warm up.")
    items = list(pending.items())
    for start in range(0, len(items), batch_size):
        batch = items[start : start + batch_size]
        inputs = MARIAN_TOKENIZER(
            [text for _, text in batch],
            return_tensors="pt",
            padding=True,
        )
        outputs = MARIAN_MODEL.generate(**inputs, num_beams=1)
        translations = MARIAN_TOKENIZER.batch_decode(
            outputs, skip_special_tokens=True
        )
        for (cache_key, _), translated in zip(batch, translations, strict=True):
            cache[cache_key] = translated
        save_cache(cache)


def target_path(source: Path) -> Path:
    return TARGET_ROOT / source.relative_to(ROOT)


def generate(source: Path, cache: dict[str, str], engine: str) -> Path:
    metadata, body = parse_profile(source)
    localized = dict(metadata)
    localized["id"] = f"{metadata['entity_id']}:es"
    localized["locale"] = "es"
    localized["translation_of"] = metadata["id"]
    localized["translation_status"] = "needs_review"
    localized["summary"] = translate_field(
        metadata["summary"], metadata, cache, engine
    )
    translated_body = translate_body(body, metadata, cache, engine)
    target = target_path(source)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "---\n"
        + json.dumps(localized, ensure_ascii=False, indent=2)
        + "\n---\n"
        + translated_body.rstrip()
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return target


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument(
        "--path",
        action="append",
        help="Canonical repository-relative path; repeat for an explicit batch.",
    )
    parser.add_argument(
        "--engine",
        choices=("argos", "google", "marian"),
        default="marian",
    )
    parser.add_argument(
        "--manifest-only",
        action="store_true",
        help="Write the deterministic batch manifest without translating.",
    )
    args = parser.parse_args()
    paths = canonical_paths()
    if args.manifest_only:
        write_manifest(paths)
        print(MANIFEST_PATH.relative_to(ROOT).as_posix())
        return
    selected = (
        [ROOT / path for path in args.path]
        if args.path
        else paths[args.start : args.start + args.limit]
    )
    if any(path not in paths for path in selected):
        raise SystemExit("every --path must identify a canonical profile")
    if args.limit > 25:
        raise SystemExit("a translation batch cannot exceed 25 profiles")
    cache = load_cache()
    if args.engine == "marian":
        prefill_marian(selected, cache)
    for source in selected:
        target = generate(source, cache, args.engine)
        index = paths.index(source) + 1
        print(f"{index:03d}/{len(paths)} {target.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
