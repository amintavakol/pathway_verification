from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd

from _bootstrap import ROOT
from rxnfe.utils.config import load_config
from rxnfe.io.readers import read_table
from rxnfe.io.writers import write_json
from rxnfe.xtb_tools.tblite_optimize import optimize_xyz
from rxnfe.rdkit_tools.sdf_conformers import write_selected_conformer_xyz


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--species-table",
        type=str,
        default=str(ROOT / "data" / "processed" / "species_table.parquet"),
    )
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    config = load_config()
    species_df = read_table(args.species_table)

    if args.limit is not None:
        species_df = species_df.head(args.limit)

    for _, row in species_df.iterrows():
        species_id = row["species_id"]
        selected_csv = ROOT / "work" / "species" / species_id / "crest" / "selected.csv"
        rdkit_sdf = ROOT / "work" / "species" / species_id / "rdkit" / "conformers.sdf"

        if not selected_csv.exists() or not rdkit_sdf.exists():
            print(f"[WARN] {species_id}: missing selected.csv or conformers.sdf, skipping.")
            continue

        selected = pd.read_csv(selected_csv)
        if selected.empty:
            print(f"[WARN] {species_id}: selected.csv is empty, skipping.")
            continue

        success_count = 0
        failure_count = 0

        for _, crow in selected.iterrows():
            conf_id = int(crow["conformer_id"])
            conf_dir = ROOT / "work" / "species" / species_id / "xtb" / f"CONF_{conf_id:04d}"
            conf_dir.mkdir(parents=True, exist_ok=True)

            input_xyz = conf_dir / "input.xyz"
            out_xyz = conf_dir / "optimized.xyz"

            try:
                write_selected_conformer_xyz(
                    rdkit_sdf,
                    species_id=species_id,
                    conformer_id=conf_id,
                    out_xyz=input_xyz,
                )
            except Exception as e:
                failure_count += 1
                meta = {
                    "success": False,
                    "error": f"Failed to write selected conformer XYZ: {e}",
                    "species_id": species_id,
                    "conformer_id": conf_id,
                    "input_xyz": str(input_xyz),
                    "output_xyz": str(out_xyz),
                }
                write_json(meta, conf_dir / "opt.json")
                print(f"[WARN] {species_id} CONF_{conf_id:04d}: {meta['error']}")
                continue

            try:
                meta = optimize_xyz(
                    input_xyz=input_xyz,
                    output_xyz=out_xyz,
                    charge=int(row["formal_charge"]),
                    multiplicity=int(row["spin_multiplicity"]),
                    method=str(config.get("xtb", {}).get("tblite_method", "GFN2-xTB")),
                    fmax=float(config.get("xtb", {}).get("optimization_fmax_eV_A", 0.05)),
                    steps=int(config.get("xtb", {}).get("optimization_steps", 300)),
                    accuracy=float(config.get("xtb", {}).get("accuracy", 1.0)),
                    electronic_temperature=float(
                        config.get("xtb", {}).get(
                            "electronic_temperature_K",
                            config["project"]["temperature_K"],
                        )
                    ),
                    max_iterations=int(config.get("xtb", {}).get("max_iterations", 250)),
                    verbosity=int(config.get("xtb", {}).get("verbosity", 0)),
                    trajectory_path=conf_dir / "optimization.traj",
                    log_path=conf_dir / "optimization.log",
                )
            except Exception as e:
                meta = {
                    "success": False,
                    "error": str(e),
                    "species_id": species_id,
                    "conformer_id": conf_id,
                    "input_xyz": str(input_xyz),
                    "output_xyz": str(out_xyz),
                }

            write_json(meta, conf_dir / "opt.json")

            if meta.get("success", False):
                success_count += 1
            else:
                failure_count += 1
                print(f"[WARN] {species_id} CONF_{conf_id:04d}: optimization failed: {meta.get('error')}")

        summary = {
            "species_id": species_id,
            "n_selected_conformers": int(len(selected)),
            "n_success": int(success_count),
            "n_failed": int(failure_count),
        }
        write_json(summary, ROOT / "work" / "species" / species_id / "xtb" / "summary.json")

        if success_count == 0:
            print(f"[WARN] xTB optimize stage completed for {species_id}, but no conformers succeeded.")
        else:
            print(f"[INFO] xTB optimize stage completed for {species_id}: {success_count}/{len(selected)} succeeded.")


if __name__ == "__main__":
    main()