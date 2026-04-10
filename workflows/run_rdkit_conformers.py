from __future__ import annotations

import argparse
from pathlib import Path

from _bootstrap import ROOT
from rxnfe.utils.config import load_config
from rxnfe.io.readers import read_table
from rxnfe.rdkit_tools.generate_conformers import generate_rdkit_conformers


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
        rdkit_dir = ROOT / "work" / "species" / species_id / "rdkit"
        generate_rdkit_conformers(
            row["state_smiles"],
            n_confs=config["rdkit"]["num_initial_conformers"],
            out_sdf=rdkit_dir / "conformers.sdf",
            out_csv=rdkit_dir / "conformers.csv",
            random_seed=config["rdkit"]["random_seed"],
            do_mmff_relax=config["rdkit"]["do_mmff_relax"],
        )
        print(f"Generated RDKit conformers for {species_id}")


if __name__ == "__main__":
    main()
