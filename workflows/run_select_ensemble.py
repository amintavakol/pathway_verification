from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd

from _bootstrap import ROOT
from rxnfe.utils.config import load_config
from rxnfe.io.readers import read_table
from rxnfe.crest_tools.cregen_filter import select_by_energy_window


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--species-table", type=str, default=str(ROOT / "data" / "processed" / "species_table.parquet"))
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    config = load_config()
    species_df = read_table(args.species_table)
    if args.limit is not None:
        species_df = species_df.head(args.limit)

    for _, row in species_df.iterrows():
        species_id = row["species_id"]
        rdkit_csv = ROOT / "work" / "species" / species_id / "rdkit" / "conformers.csv"
        crest_dir = ROOT / "work" / "species" / species_id / "crest"
        out_csv = crest_dir / "selected.csv"
        if rdkit_csv.exists():
            df = pd.read_csv(rdkit_csv)
            if "mmff_energy" in df.columns and df["mmff_energy"].notna().any():
                energy_col = "mmff_energy"
                df = df.rename(columns={"conformer_id": "conformer_id"})
            else:
                df["mmff_energy"] = range(len(df))
                energy_col = "mmff_energy"
            selected = select_by_energy_window(
                df,
                energy_col=energy_col,
                window_kcal_mol=float(config["ensemble"]["selection_window_kcal_mol"]),
                max_selected=int(config["ensemble"]["max_selected_conformers"]),
            )
            crest_dir.mkdir(parents=True, exist_ok=True)
            selected.to_csv(out_csv, index=False)
        print(f"Selected ensemble for {species_id}")


if __name__ == "__main__":
    main()
