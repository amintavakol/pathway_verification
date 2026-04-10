from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from _bootstrap import ROOT

SCRIPTS = [
    "run_prepare_dataset.py",
    "run_build_3d.py",
    "run_rdkit_conformers.py",
    "run_select_ensemble.py",
    "run_xtb_optimize.py",
    "run_xtb_thermo.py",
    "run_boltzmann_average.py",
    "run_score_pathways.py",
]


def main() -> None:
    for script in SCRIPTS:
        path = ROOT / "workflows" / script
        print(f"Running {path.name}")
        subprocess.run([sys.executable, str(path)], check=True)


if __name__ == "__main__":
    main()
