from __future__ import annotations

from pathlib import Path
import json
import pandas as pd


def read_csv(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(path)


def read_table(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        return pd.DataFrame()
    if path.suffix == ".parquet":
        return pd.read_parquet(path)
    if path.suffix == ".csv":
        return pd.read_csv(path)
    raise ValueError(f"Unsupported table format: {path}")


def read_json(path: str | Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
