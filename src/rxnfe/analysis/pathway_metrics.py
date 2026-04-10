from __future__ import annotations

import pandas as pd


def summarize_profiles(profile_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for reaction_id, sub in profile_df.groupby("reaction_id"):
        sub = sub.sort_values("step_index")
        rows.append({
            "reaction_id": reaction_id,
            "n_states": int(len(sub)),
            "overall_deltaG_kcal_mol": float(sub["G_relative_kcal_mol"].iloc[-1]),
            "max_uphill_step_kcal_mol": float(sub["deltaG_step_kcal_mol"].fillna(0.0).max()),
        })
    return pd.DataFrame(rows)
