from __future__ import annotations

import argparse
from pathlib import Path

from _bootstrap import ROOT
from rxnfe.utils.config import load_config
from rxnfe.io.readers import read_table
from rxnfe.rdkit_tools.embed_3d import build_initial_3d
from rxnfe.io.writers import write_json


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
        sp_dir = ROOT / "work" / "species" / species_id
        initial_dir = sp_dir / "initial"
        build_initial_3d(
            row["state_smiles"],
            initial_dir / "mol.sdf",
            initial_dir / "initial.xyz",
            random_seed=config["rdkit"]["random_seed"],
        )
        write_json(row.to_dict(), sp_dir / "metadata.json")
        (sp_dir / "input_smiles.txt").write_text(str(row["state_smiles"]) + "\n", encoding="utf-8")
        print(f"Built 3D for {species_id}")


if __name__ == "__main__":
    main()
