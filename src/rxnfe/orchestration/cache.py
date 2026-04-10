from __future__ import annotations

from pathlib import Path


def exists(path: str | Path) -> bool:
    return Path(path).exists()
