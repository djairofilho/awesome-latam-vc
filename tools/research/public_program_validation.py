"""Central validation entry point for Epic 65 public-program artifacts."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType


def _load_contract_validator(root: Path) -> tuple[ModuleType | None, list[str]]:
    path = root / "research" / "epic-65" / "validate.py"
    display_path = path.relative_to(root).as_posix()
    if not path.is_file():
        return None, [f"{display_path}: validador obrigatório ausente"]
    spec = importlib.util.spec_from_file_location(
        "_epic_65_contract_validator",
        path,
    )
    if spec is None or spec.loader is None:
        return None, [f"{display_path}: não foi possível carregar o validador"]
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        return None, [f"{display_path}: falha ao carregar o validador: {exc}"]
    return module, []


def validate_epic_65(root: Path) -> list[str]:
    """Validate the canonical Epic 65 templates and example."""
    module, errors = _load_contract_validator(root)
    if module is None:
        return errors
    validate_bundle = getattr(module, "validate_bundle", None)
    if not callable(validate_bundle):
        return [
            "research/epic-65/validate.py: função validate_bundle obrigatória ausente"
        ]
    epic_root = root / "research" / "epic-65"
    for bundle_name in ("templates", "examples"):
        errors.extend(validate_bundle(epic_root / bundle_name))
    return sorted(set(errors))
