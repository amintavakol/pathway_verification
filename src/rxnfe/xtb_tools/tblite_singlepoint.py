from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

HARTREE_TO_EV = 27.211386245988
EV_TO_KCAL_MOL = 23.06054783061903

try:
    from ase import Atoms
    from ase.io import read as ase_read
    from tblite.ase import TBLite
except Exception:
    Atoms = None
    ase_read = None
    TBLite = None


def tblite_available() -> bool:
    return TBLite is not None and ase_read is not None and Atoms is not None


def build_tblite_calculator(
    charge: int = 0,
    multiplicity: int = 1,
    method: str = "GFN2-xTB",
    accuracy: float = 1.0,
    electronic_temperature: float = 300.0,
    max_iterations: int = 250,
    verbosity: int = 0,
):
    if not tblite_available():
        raise ImportError("tblite and ASE are required. Install conda-forge::tblite-python and ase.")
    kwargs: dict[str, Any] = {
        "method": method,
        "charge": int(charge),
        "accuracy": float(accuracy),
        "electronic_temperature": float(electronic_temperature),
        "max_iterations": int(max_iterations),
        "verbosity": int(verbosity),
    }
    if multiplicity is not None:
        kwargs["multiplicity"] = int(multiplicity)
    return TBLite(**kwargs)


def load_atoms_from_xyz(path: str | Path):
    if ase_read is None:
        raise ImportError("ASE is required to read XYZ files.")
    return ase_read(str(path))


def singlepoint_atoms(
    atoms,
    charge: int = 0,
    multiplicity: int = 1,
    method: str = "GFN2-xTB",
    accuracy: float = 1.0,
    electronic_temperature: float = 300.0,
    max_iterations: int = 250,
    verbosity: int = 0,
) -> dict[str, float]:
    calc = build_tblite_calculator(
        charge=charge,
        multiplicity=multiplicity,
        method=method,
        accuracy=accuracy,
        electronic_temperature=electronic_temperature,
        max_iterations=max_iterations,
        verbosity=verbosity,
    )
    atoms = atoms.copy()
    atoms.calc = calc
    energy_ev = float(atoms.get_potential_energy())
    return {
        "energy_eV": energy_ev,
        "energy_hartree": energy_ev / HARTREE_TO_EV,
        "energy_kcal_mol": energy_ev * EV_TO_KCAL_MOL,
    }


def singlepoint_xyz(path: str | Path, **kwargs) -> dict[str, float]:
    atoms = load_atoms_from_xyz(path)
    return singlepoint_atoms(atoms, **kwargs)
