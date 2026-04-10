from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import yaml


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def load_config(config_path: str | Path | None = None) -> Dict[str, Any]:
    path = Path(config_path) if config_path else project_root() / "config" / "config.yaml"
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
