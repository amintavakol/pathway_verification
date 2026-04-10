from __future__ import annotations

import pandas as pd


def rank_pathways(summary_df: pd.DataFrame) -> pd.DataFrame:
    if summary_df.empty:
        return summary_df.copy()
    df = summary_df.copy()
    df["rank_score"] = df["overall_deltaG_kcal_mol"] + 0.5 * df["max_uphill_step_kcal_mol"]
    return df.sort_values(["reaction_id", "rank_score"]).reset_index(drop=True)
