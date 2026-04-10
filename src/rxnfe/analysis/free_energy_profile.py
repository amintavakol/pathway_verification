from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def build_profile(species_table: pd.DataFrame, species_free_energies: pd.DataFrame) -> pd.DataFrame:
    required_species_cols = {"species_id", "reaction_id", "step_index", "role"}
    required_free_cols = {"species_id", "G_species_kcal_mol"}
    missing_species = required_species_cols - set(species_table.columns)
    missing_free = required_free_cols - set(species_free_energies.columns)
    if missing_species:
        raise ValueError(f"species_table is missing columns: {sorted(missing_species)}")
    if missing_free:
        raise ValueError(
            f"species_free_energies is missing columns: {sorted(missing_free)}. "
            f"Found columns: {species_free_energies.columns.tolist()}"
        )

    merged = species_table.merge(
        species_free_energies[["species_id", "G_species_kcal_mol"]],
        on="species_id",
        how="left",
    )
    merged = merged.sort_values(["reaction_id", "step_index"]).copy()
    merged["G_relative_kcal_mol"] = merged.groupby("reaction_id")["G_species_kcal_mol"].transform(lambda s: s - s.iloc[0])
    merged["deltaG_step_kcal_mol"] = merged.groupby("reaction_id")["G_species_kcal_mol"].diff()
    return merged


def plot_profile(
    df: pd.DataFrame,
    reaction_id: str,
    out_path: str | Path | None = None,
    dpi: int = 160,
    figsize: tuple[float, float] = (8, 4),
):
    sub = df[df["reaction_id"] == reaction_id].sort_values("step_index")
    if sub.empty:
        raise ValueError(f"No rows found for reaction_id={reaction_id}")
    x = sub["step_index"].to_list()
    y = sub["G_relative_kcal_mol"].to_list()
    labels = [f"{i}:{r}" for i, r in zip(sub["step_index"], sub["role"])]
    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(x, y, marker="o")
    ax.set_xlabel("Pathway state index")
    ax.set_ylabel("Relative free energy (kcal/mol)")
    ax.set_title(f"Free energy profile | {reaction_id}")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right")
    fig.tight_layout()
    if out_path is not None:
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_path, dpi=dpi, bbox_inches="tight")
    return fig, ax
