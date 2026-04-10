from __future__ import annotations

from pathlib import Path
import json


def record_failure(path: str | Path, species_id: str, stage: str, error: str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps({"species_id": species_id, "stage": stage, "error": error}) + "\n")
