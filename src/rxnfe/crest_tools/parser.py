from __future__ import annotations

from pathlib import Path
import pandas as pd


def parse_selected_from_csv(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        return pd.DataFrame(columns=["conformer_id", "relative_energy_kcal_mol", "selected"])
    return pd.read_csv(path)
