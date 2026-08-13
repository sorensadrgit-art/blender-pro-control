from pathlib import Path
from typing import Iterable

def require_within(path: str | Path, roots: Iterable[str | Path]) -> Path:
    candidate = Path(path).resolve()
    allowed = [Path(root).resolve() for root in roots]
    for root in allowed:
        try:
            candidate.relative_to(root)
            return candidate
        except ValueError:
            continue
    raise ValueError(f"path is outside allowed roots: {candidate}")
