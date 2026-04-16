from __future__ import annotations

import argparse
import pandas as pd

from _bootstrap import ROOT
from rxnfe.utils.config import load_config
from rxnfe.io.readers import read_table
from rxnfe.io.writers import write_json, write_table
from rxnfe.analysis.boltzmann import boltzmann_average_dataframe


EXPECTED_COLUMNS = ["species_id", "G_species_kcal_mol", "G_min_kcal_mol", "n_conformers"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--species-table", type=str, default=str(ROOT / "data" / "processed" / "species_table.parquet"))
    parser.add_argument("--output", type=str, default=str(ROOT / "data" / "processed" / "species_free_energies.parquet"))
    args = parser.parse_args()
    config = load_config()
    species_df = read_table(args.species_table)

    rows = []
    for _, row in species_df.iterrows():
        species_id = row["species_id"]
        thermo_csv = ROOT / "work" / "species" / species_id / "final" / "conformer_thermo.csv"
        if not thermo_csv.exists():
            continue
        try:
            thermo_df = pd.read_csv(thermo_csv)
        except pd.errors.EmptyDataError:
            continue
        if thermo_df.empty or "G_kcal_mol" not in thermo_df.columns:
            continue
        result = boltzmann_average_dataframe(
            thermo_df,
            energy_col="G_kcal_mol",
            temperature_K=float(config["project"]["temperature_K"]),
        )
        result["table"].to_csv(ROOT / "work" / "species" / species_id / "final" / "conformer_thermo_weighted.csv", index=False)
        payload = {
            "species_id": species_id,
            "temperature_K": float(config["project"]["temperature_K"]),
            "n_conformers": int(result["n_conformers"]),
            "G_min_kcal_mol": float(result["G_min_kcal_mol"]),
            "G_boltzmann_kcal_mol": float(result["G_boltzmann_kcal_mol"]),
        }
        write_json(payload, ROOT / "work" / "species" / species_id / "final" / "ensemble_free_energy.json")
        rows.append({
            "species_id": species_id,
            "G_species_kcal_mol": payload["G_boltzmann_kcal_mol"],
            "G_min_kcal_mol": payload["G_min_kcal_mol"],
            "n_conformers": payload["n_conformers"],
        })
    out = pd.DataFrame(rows, columns=EXPECTED_COLUMNS)
    if out.empty:
        raise RuntimeError(
            "No species free energies were generated. Check whether run_xtb_thermo.py created non-empty conformer_thermo.csv files."
        )
    write_table(out, args.output)
    print(f"Wrote species free energies to {args.output}")


if __name__ == "__main__":
    main()
