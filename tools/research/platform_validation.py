"""Integration helpers for Epic 64 funding-platform research artifacts."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType


def _load_validator(path: Path) -> tuple[ModuleType | None, list[str]]:
    spec = importlib.util.spec_from_file_location(
        f"_epic_64_validator_{abs(hash(path.resolve()))}",
        path,
    )
    if spec is None or spec.loader is None:
        return None, [f"{path.as_posix()}: não foi possível carregar o validador"]
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        return None, [f"{path.as_posix()}: falha ao carregar o validador: {exc}"]
    return module, []


def _relative_error(root: Path, error: str) -> str:
    resolved = str(root.resolve())
    for prefix in (resolved + "/", resolved + "\\"):
        if error.startswith(prefix):
            return error[len(prefix) :].replace("\\", "/")
    return error.replace("\\", "/")


def validate_epic_64(root: Path) -> list[str]:
    """Validate Epic 64 schemas, templates, examples and coverage matrix."""
    epic_root = root / "research" / "epic-64"
    if not epic_root.exists():
        return []
    validator_path = epic_root / "validate.py"
    if not validator_path.is_file():
        return ["research/epic-64/validate.py: validador obrigatório ausente"]
    module, errors = _load_validator(validator_path)
    if module is None:
        return errors
    validate_contract = getattr(module, "validate_contract", None)
    if not callable(validate_contract):
        return [
            "research/epic-64/validate.py: função validate_contract obrigatória ausente"
        ]
    try:
        validation_errors = validate_contract()
    except Exception as exc:
        return [f"research/epic-64/validate.py: validação falhou: {exc}"]
    return sorted({_relative_error(root, error) for error in validation_errors})
