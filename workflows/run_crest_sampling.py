from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from _bootstrap import ROOT
from rxnfe.utils.config import load_config
from rxnfe.io.readers import read_table
from rxnfe.crest_tools.launcher import run_crest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--species-table", type=str, default=str(ROOT / "data" / "processed" / "species_table.parquet"))
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    config = load_config()
    species_df = read_table(args.species_table)
    if args.limit is not None:
        species_df = species_df.head(args.limit)

    crest_exe = shutil.which(config["crest"]["executable"])
    for _, row in species_df.iterrows():
        species_id = row["species_id"]
        initial_xyz = ROOT / "work" / "species" / species_id / "initial" / "initial.xyz"
        crest_dir = ROOT / "work" / "species" / species_id / "crest"
        if crest_exe:
            proc = run_crest(
                initial_xyz,
                crest_dir,
                executable=crest_exe,
                charge=int(row["formal_charge"]),
                uhf=max(int(row["spin_multiplicity"]) - 1, 0),
                extra_args=config["crest"]["extra_args"],
            )
            (crest_dir / "crest.stdout.txt").write_text(proc.stdout or "", encoding="utf-8")
            (crest_dir / "crest.stderr.txt").write_text(proc.stderr or "", encoding="utf-8")
        else:
            crest_dir.mkdir(parents=True, exist_ok=True)
            (crest_dir / "crest.stdout.txt").write_text("CREST executable not found. Skipped.\n", encoding="utf-8")
        print(f"CREST stage completed for {species_id}")


if __name__ == "__main__":
    main()
