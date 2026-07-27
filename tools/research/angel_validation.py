"""Integra o contrato de redes-anjo da epic 63 ao gate central."""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path
from types import ModuleType


ARTIFACT_FILES = {
    "candidates.jsonl",
    "coverage-matrix.jsonl",
    "evidence.jsonl",
    "run-manifest.jsonl",
    "source-inventory.jsonl",
}


def _display(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def _load_contract_validator(script: Path) -> ModuleType:
    digest = hashlib.sha256(str(script).encode("utf-8")).hexdigest()[:12]
    module_name = f"epic_63_contract_validate_{digest}"
    spec = importlib.util.spec_from_file_location(module_name, script)
    if spec is None or spec.loader is None:
        raise ImportError(f"não foi possível carregar {script}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _artifact_directories(epic_root: Path) -> list[Path]:
    directories = {
        path.parent
        for path in epic_root.rglob("*.jsonl")
        if path.name in ARTIFACT_FILES and "shards" not in path.parts
    }
    return sorted(directories)


def validate_epic_63(root: Path) -> list[str]:
    """Valida schemas, exemplos, templates e conjuntos canônicos da epic 63."""
    epic_root = root / "research" / "epic-63"
    if not epic_root.exists():
        return []
    script = epic_root / "validate.py"
    if not script.is_file():
        return ["research/epic-63/validate.py: validador obrigatório ausente"]
    try:
        validator = _load_contract_validator(script)
    except (ImportError, OSError, SyntaxError) as exc:
        return [f"research/epic-63/validate.py: falha ao carregar: {exc}"]

    directories = _artifact_directories(epic_root)
    errors: list[str] = []
    for required in ("examples", "templates"):
        directory = epic_root / required
        if directory not in directories:
            errors.append(
                f"{_display(root, directory)}: conjunto obrigatório ausente"
            )

    for directory in directories:
        prefix = _display(root, directory)
        try:
            directory_errors = validator.validate_directory(directory)
        except Exception as exc:
            errors.append(f"{prefix}: validação falhou: {exc}")
            continue
        errors.extend(f"{prefix}/{error}" for error in directory_errors)
    return sorted(set(errors))
