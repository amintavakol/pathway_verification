from __future__ import annotations

from pathlib import Path
import json
import pandas as pd


def ensure_parent(path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def write_table(df: pd.DataFrame, path: str | Path) -> None:
    path = ensure_parent(path)
    if path.suffix == ".parquet":
        df.to_parquet(path, index=False)
        return
    if path.suffix == ".csv":
        df.to_csv(path, index=False)
        return
    raise ValueError(f"Unsupported output format: {path}")


def write_json(data, path: str | Path) -> None:
    path = ensure_parent(path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
