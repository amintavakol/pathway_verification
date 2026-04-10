from __future__ import annotations

from pathlib import Path


def species_dir(root: str | Path, species_id: str) -> Path:
    return Path(root) / "species" / species_id
