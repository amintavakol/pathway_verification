from __future__ import annotations

from pathlib import Path

from rxnfe.xtb_tools.tblite_singlepoint import build_tblite_calculator, load_atoms_from_xyz, tblite_available

try:
    from ase.vibrations import Vibrations
except Exception:
    Vibrations = None


def run_vibrations(
    xyz_path: str | Path,
    workdir: str | Path,
    charge: int = 0,
    multiplicity: int = 1,
    method: str = "GFN2-xTB",
    delta: float = 0.01,
    nfree: int = 2,
    accuracy: float = 1.0,
    electronic_temperature: float = 300.0,
    max_iterations: int = 250,
    verbosity: int = 0,
):
    if not tblite_available() or Vibrations is None:
        raise ImportError("tblite and ASE vibrations are required.")
    atoms = load_atoms_from_xyz(xyz_path)
    atoms.calc = build_tblite_calculator(
        charge=charge,
        multiplicity=multiplicity,
        method=method,
        accuracy=accuracy,
        electronic_temperature=electronic_temperature,
        max_iterations=max_iterations,
        verbosity=verbosity,
    )
    workdir = Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    vib = Vibrations(atoms, name=str(workdir / "vib"), delta=float(delta), nfree=int(nfree))
    vib.run()
    return vib
