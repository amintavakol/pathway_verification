from __future__ import annotations

import argparse
import pandas as pd

from _bootstrap import ROOT
from rxnfe.utils.config import load_config
from rxnfe.io.readers import read_table
from rxnfe.xtb_tools.thermo import compute_gibbs_free_energy_xyz


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
        selected_csv = ROOT / "work" / "species" / species_id / "crest" / "selected.csv"
        final_dir = ROOT / "work" / "species" / species_id / "final"
        final_dir.mkdir(parents=True, exist_ok=True)
        records = []
        if selected_csv.exists():
            selected = pd.read_csv(selected_csv)
        else:
            selected = pd.DataFrame([{"conformer_id": 0}])
        for _, crow in selected.iterrows():
            conf_id = int(crow["conformer_id"])
            conf_dir = ROOT / "work" / "species" / species_id / "xtb" / f"CONF_{conf_id:04d}"
            optimized_xyz = conf_dir / "optimized.xyz"
            if not optimized_xyz.exists():
                continue
            terms = compute_gibbs_free_energy_xyz(
                xyz_path=optimized_xyz,
                charge=int(row["formal_charge"]),
                multiplicity=int(row["spin_multiplicity"]),
                temperature_K=float(config["project"]["temperature_K"]),
                pressure_Pa=float(config.get("xtb", {}).get("pressure_Pa", 101325.0)),
                method=str(config.get("xtb", {}).get("tblite_method", "GFN2-xTB")),
                accuracy=float(config.get("xtb", {}).get("accuracy", 1.0)),
                electronic_temperature=float(config.get("xtb", {}).get("electronic_temperature_K", config["project"]["temperature_K"])),
                max_iterations=int(config.get("xtb", {}).get("max_iterations", 250)),
                vib_delta=float(config.get("xtb", {}).get("vib_delta_A", 0.01)),
                vib_nfree=int(config.get("xtb", {}).get("vib_nfree", 2)),
                symmetrynumber=int(config.get("xtb", {}).get("symmetrynumber", 1)),
                ignore_imag_modes=bool(config.get("xtb", {}).get("ignore_imag_modes", True)),
                verbosity=int(config.get("xtb", {}).get("verbosity", 0)),
                scratch_dir=conf_dir / "vib",
                cleanup=bool(config.get("xtb", {}).get("cleanup_vibration_files", True)),
            )
            terms["species_id"] = species_id
            terms["conformer_id"] = conf_id
            records.append(terms)
        out = pd.DataFrame(records)
        out.to_csv(final_dir / "conformer_thermo.csv", index=False)
        print(f"Thermochemistry written for {species_id}")


if __name__ == "__main__":
    main()
