from __future__ import annotations

import argparse
import pandas as pd

from _bootstrap import ROOT
from rxnfe.io.readers import read_csv
from rxnfe.io.smiles_io import split_pathway_states
from rxnfe.io.writers import write_table
from rxnfe.chemistry.charge_spin import formal_charge_from_smiles, default_spin_multiplicity


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, default=str(ROOT / "data" / "raw" / "example_subset.csv"))
    parser.add_argument("--output", type=str, default=str(ROOT / "data" / "processed" / "species_table.parquet"))
    args = parser.parse_args()

    df = read_csv(args.input)
    rows = []
    species_counter = 1
    for r_idx, row in df.iterrows():
        reaction_id = row.get("reaction_id", f"RXN{r_idx+1:06d}")
        states = split_pathway_states(row["species_smiles"])
        n_states = len(states)
        for step_index, state_smiles in enumerate(states):
            if step_index == 0:
                role = "reactant"
            elif step_index == n_states - 1:
                role = "product"
            else:
                role = "intermediate"
            species_id = f"SP{species_counter:06d}"
            species_counter += 1
            rows.append({
                "species_id": species_id,
                "reaction_id": reaction_id,
                "step_index": step_index,
                "role": role,
                "mapped_smiles": state_smiles,
                "state_smiles": state_smiles,
                "formal_charge": formal_charge_from_smiles(state_smiles),
                "spin_multiplicity": default_spin_multiplicity(state_smiles),
            })
    out = pd.DataFrame(rows)
    write_table(out, args.output)
    print(f"Wrote {len(out)} species rows to {args.output}")


if __name__ == "__main__":
    main()
