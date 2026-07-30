"""Integrate Epic 207 fund re-audit artifacts with the central research gate."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType


def _load(path: Path) -> tuple[ModuleType | None, list[str]]:
    spec = importlib.util.spec_from_file_location("_epic_207_validator", path)
    if spec is None or spec.loader is None:
        return None, [f"{path.as_posix()}: não foi possível carregar o validador"]
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        return None, [f"{path.as_posix()}: falha ao carregar o validador: {exc}"]
    return module, []


def validate_epic_207(root: Path) -> list[str]:
    """Validate Epic 207 schemas, templates and examples."""
    epic_root = root / "research" / "epic-207"
    if not epic_root.exists():
        return []
    path = epic_root / "validate.py"
    if not path.is_file():
        return ["research/epic-207/validate.py: validador obrigatório ausente"]
    module, errors = _load(path)
    if module is None:
        return errors
    validate_contract = getattr(module, "validate_contract", None)
    if not callable(validate_contract):
        return [
            "research/epic-207/validate.py: função validate_contract obrigatória ausente"
        ]
    try:
        errors.extend(validate_contract())
    except Exception as exc:
        errors.append(f"research/epic-207/validate.py: validação falhou: {exc}")
    return sorted(set(errors))
