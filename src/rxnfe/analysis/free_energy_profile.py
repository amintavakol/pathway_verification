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
    dpi: int = 300,
    figsize: tuple[float, float] = (10, 5),
):
    sub = df[df["reaction_id"] == reaction_id].sort_values("step_index")
    if sub.empty:
        raise ValueError(f"No rows found for reaction_id={reaction_id}")

    x = sub["step_index"].to_list()
    y = sub["G_relative_kcal_mol"].to_list()

    # Create custom labels: "reactants", "1", "2", ..., "products"
    labels = []
    n_steps = len(sub)
    for i, role in enumerate(sub["role"]):
        if i == 0:
            labels.append("reactants")
        elif i == n_steps - 1:
            labels.append("products")
        else:
            labels.append(str(i))

    fig, ax = plt.subplots(figsize=figsize)

    # Plotting parameters
    line_width = 0.4  # width of the horizontal line for each state
    color = "royalblue"

    # Plot horizontal lines for each state and dashed connectors
    for i in range(len(x)):
        # Horizontal line for the state
        ax.hlines(y[i], x[i] - line_width/2, x[i] + line_width/2, color=color, lw=3)

        # Dashed line connecting to the next state
        if i < len(x) - 1:
            ax.plot([x[i] + line_width/2, x[i+1] - line_width/2], [y[i], y[i+1]],
                    color=color, linestyle="--", alpha=0.6)

    ax.set_xlabel("Reaction Coordinate", fontsize=12)
    ax.set_ylabel(r"$G_{\rm rel}$ (kcal/mol)", fontsize=12)
    ax.set_title(f"Free Energy Profile | {reaction_id}", fontsize=14, pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)

    # Styling
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', linestyle=':', alpha=0.3)

    fig.tight_layout()

    if out_path is not None:
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_path, dpi=dpi, bbox_inches="tight")
    return fig, ax
