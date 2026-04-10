from __future__ import annotations

import argparse

from _bootstrap import ROOT
from rxnfe.utils.config import load_config
from rxnfe.io.readers import read_table
from rxnfe.analysis.free_energy_profile import plot_profile


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profiles", type=str, default=str(ROOT / "data" / "processed" / "pathway_profiles.parquet"))
    parser.add_argument("--reaction-id", type=str, required=True)
    parser.add_argument("--output", type=str, default=None)
    args = parser.parse_args()
    config = load_config()
    df = read_table(args.profiles)
    output = args.output or str(ROOT / "work" / "pathways" / args.reaction_id / f"{args.reaction_id}_profile.png")
    plot_profile(
        df,
        reaction_id=args.reaction_id,
        out_path=output,
        dpi=int(config["plotting"]["dpi"]),
        figsize=tuple(config["plotting"]["figsize"]),
    )
    print(f"Saved plot to {output}")


if __name__ == "__main__":
    main()
