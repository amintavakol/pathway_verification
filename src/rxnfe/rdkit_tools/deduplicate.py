from __future__ import annotations

import pandas as pd


def deduplicate_conformers(df: pd.DataFrame) -> pd.DataFrame:
    if "mmff_energy" not in df.columns:
        return df
    return df.sort_values("mmff_energy", na_position="last").drop_duplicates(subset=["mmff_energy"])
