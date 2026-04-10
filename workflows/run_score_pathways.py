from __future__ import annotations

import argparse
from pathlib import Path

from _bootstrap import ROOT
from rxnfe.io.readers import read_table
from rxnfe.io.writers import write_table
from rxnfe.analysis.free_energy_profile import build_profile
from rxnfe.analysis.pathway_metrics import summarize_profiles
from rxnfe.analysis.ranking import rank_pathways


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--species-table", type=str, default=str(ROOT / "data" / "processed" / "species_table.parquet"))
    parser.add_argument("--species-free-energies", type=str, default=str(ROOT / "data" / "processed" / "species_free_energies.parquet"))
    parser.add_argument("--profile-output", type=str, default=str(ROOT / "data" / "processed" / "pathway_profiles.parquet"))
    parser.add_argument("--benchmark-output", type=str, default=str(ROOT / "data" / "processed" / "benchmark_scores.parquet"))
    args = parser.parse_args()

    species_table = read_table(args.species_table)
    species_free = read_table(args.species_free_energies)
    profile = build_profile(species_table, species_free)
    summary = summarize_profiles(profile)
    ranked = rank_pathways(summary)
    write_table(profile, args.profile_output)
    write_table(ranked, args.benchmark_output)
    print(f"Wrote profiles to {args.profile_output}")
    print(f"Wrote benchmark scores to {args.benchmark_output}")


if __name__ == "__main__":
    main()
