from __future__ import annotations

import pandas as pd


def select_by_energy_window(df: pd.DataFrame, energy_col: str, window_kcal_mol: float, max_selected: int) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    df = df.copy().sort_values(energy_col)
    e0 = df.iloc[0][energy_col]
    df["relative_energy_kcal_mol"] = df[energy_col] - e0
    df["selected"] = df["relative_energy_kcal_mol"] <= window_kcal_mol
    df = df[df["selected"]].head(max_selected).copy()
    return df
