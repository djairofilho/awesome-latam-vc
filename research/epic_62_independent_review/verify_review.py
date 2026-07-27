"""Import bridge for the filesystem-backed review verifier."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


_path = (
    Path(__file__).resolve().parents[1]
    / "epic-62"
    / "independent-review"
    / "verify_review.py"
)
_spec = spec_from_file_location("issue77_verify_review", _path)
if _spec is None or _spec.loader is None:
    raise ImportError(f"Não foi possível carregar {_path}")
_module = module_from_spec(_spec)
_spec.loader.exec_module(_module)

REVIEW = _module.REVIEW
validate = _module.validate
