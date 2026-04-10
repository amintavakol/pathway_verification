from __future__ import annotations

from pathlib import Path
import json

from rxnfe.xtb_tools.tblite_singlepoint import build_tblite_calculator, load_atoms_from_xyz, tblite_available

try:
    from ase.io import write as ase_write
    from ase.optimize import BFGS
except Exception:
    ase_write = None
    BFGS = None


def optimize_xyz(
    input_xyz: str | Path,
    output_xyz: str | Path,
    charge: int = 0,
    multiplicity: int = 1,
    method: str = "GFN2-xTB",
    fmax: float = 0.05,
    steps: int = 300,
    accuracy: float = 1.0,
    electronic_temperature: float = 300.0,
    max_iterations: int = 250,
    verbosity: int = 0,
    trajectory_path: str | Path | None = None,
    log_path: str | Path | None = None,
) -> dict:
    if not tblite_available() or ase_write is None or BFGS is None:
        raise ImportError("tblite and ASE with optimizer support are required.")

    atoms = load_atoms_from_xyz(input_xyz)
    atoms.calc = build_tblite_calculator(
        charge=charge,
        multiplicity=multiplicity,
        method=method,
        accuracy=accuracy,
        electronic_temperature=electronic_temperature,
        max_iterations=max_iterations,
        verbosity=verbosity,
    )

    output_xyz = Path(output_xyz)
    output_xyz.parent.mkdir(parents=True, exist_ok=True)
    if trajectory_path is not None:
        trajectory_path = Path(trajectory_path)
        trajectory_path.parent.mkdir(parents=True, exist_ok=True)
    if log_path is not None:
        log_path = Path(log_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)

    optimizer = BFGS(atoms, trajectory=str(trajectory_path) if trajectory_path else None, logfile=str(log_path) if log_path else None)
    converged = optimizer.run(fmax=float(fmax), steps=int(steps))
    energy_ev = float(atoms.get_potential_energy())
    ase_write(str(output_xyz), atoms)
    meta = {
        "converged": bool(converged),
        "n_steps": int(getattr(optimizer, "nsteps", -1)),
        "final_energy_eV": energy_ev,
        "fmax_threshold_eV_A": float(fmax),
        "max_steps": int(steps),
        "method": method,
        "charge": int(charge),
        "multiplicity": int(multiplicity),
    }
    return meta
