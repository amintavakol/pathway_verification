from __future__ import annotations

from pathlib import Path
from typing import Any
import contextlib
import json
import math

from rxnfe.xtb_tools.hessian import run_vibrations
from rxnfe.xtb_tools.tblite_singlepoint import EV_TO_KCAL_MOL, HARTREE_TO_EV, build_tblite_calculator, load_atoms_from_xyz, tblite_available

try:
    import numpy as np
    from ase.thermochemistry import IdealGasThermo
except Exception:
    np = None
    IdealGasThermo = None


def _guess_geometry(atoms) -> str:
    natoms = len(atoms)
    if natoms == 1:
        return "monatomic"
    moments = atoms.get_moments_of_inertia()
    small = sum(abs(x) < 1e-3 for x in moments)
    return "linear" if small >= 1 else "nonlinear"


def compute_gibbs_free_energy_xyz(
    xyz_path: str | Path,
    charge: int = 0,
    multiplicity: int = 1,
    temperature_K: float = 298.15,
    pressure_Pa: float = 101325.0,
    method: str = "GFN2-xTB",
    accuracy: float = 1.0,
    electronic_temperature: float = 300.0,
    max_iterations: int = 250,
    vib_delta: float = 0.01,
    vib_nfree: int = 2,
    symmetrynumber: int = 1,
    geometry: str | None = None,
    ignore_imag_modes: bool = True,
    verbosity: int = 0,
    scratch_dir: str | Path | None = None,
    cleanup: bool = True,
) -> dict[str, Any]:
    if not tblite_available() or IdealGasThermo is None or np is None:
        raise ImportError("tblite, numpy, and ASE thermochemistry are required.")

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
    potentialenergy_eV = float(atoms.get_potential_energy())

    if scratch_dir is None:
        scratch_dir = Path(xyz_path).with_suffix("")
        scratch_dir = scratch_dir.parent / (scratch_dir.name + "_vib")
    scratch_dir = Path(scratch_dir)
    vib = run_vibrations(
        xyz_path=xyz_path,
        workdir=scratch_dir,
        charge=charge,
        multiplicity=multiplicity,
        method=method,
        delta=vib_delta,
        nfree=vib_nfree,
        accuracy=accuracy,
        electronic_temperature=electronic_temperature,
        max_iterations=max_iterations,
        verbosity=verbosity,
    )
    try:
        vib_energies = vib.get_energies()
        vib_freqs_cm1 = vib.get_frequencies()
        if geometry is None:
            geometry = _guess_geometry(atoms)
        spin = 0.5 * max(int(multiplicity) - 1, 0)
        thermo = IdealGasThermo(
            vib_energies=vib_energies,
            geometry=geometry,
            potentialenergy=potentialenergy_eV,
            atoms=atoms,
            symmetrynumber=int(symmetrynumber),
            spin=spin,
            ignore_imag_modes=bool(ignore_imag_modes),
        )
        enthalpy_eV = float(thermo.get_enthalpy(temperature=temperature_K, verbose=False))
        entropy_eV_per_K = float(thermo.get_entropy(temperature=temperature_K, pressure=pressure_Pa, verbose=False))
        gibbs_eV = float(thermo.get_gibbs_energy(temperature=temperature_K, pressure=pressure_Pa, verbose=False))
        ts_eV = float(temperature_K * entropy_eV_per_K)
        thermal_corr_eV = float(enthalpy_eV - potentialenergy_eV)
        zpe_eV = float(vib.get_zero_point_energy())
        n_imag = int(sum(1 for x in vib_freqs_cm1 if np.iscomplex(x) or float(getattr(x, 'real', x)) < 0.0))
        return {
            "E_elec_eV": potentialenergy_eV,
            "H_eV": enthalpy_eV,
            "S_eV_per_K": entropy_eV_per_K,
            "TS_eV": ts_eV,
            "G_eV": gibbs_eV,
            "thermal_corr_eV": thermal_corr_eV,
            "ZPE_eV": zpe_eV,
            "n_vib_modes": int(len(vib_energies)),
            "n_imag_freqs": n_imag,
            "geometry_model": geometry,
            "symmetrynumber": int(symmetrynumber),
            "temperature_K": float(temperature_K),
            "pressure_Pa": float(pressure_Pa),
            "E_elec_hartree": potentialenergy_eV / HARTREE_TO_EV,
            "H_hartree": enthalpy_eV / HARTREE_TO_EV,
            "G_hartree": gibbs_eV / HARTREE_TO_EV,
            "E_elec_kcal_mol": potentialenergy_eV * EV_TO_KCAL_MOL,
            "H_kcal_mol": enthalpy_eV * EV_TO_KCAL_MOL,
            "TS_kcal_mol": ts_eV * EV_TO_KCAL_MOL,
            "thermal_corr_kcal_mol": thermal_corr_eV * EV_TO_KCAL_MOL,
            "G_kcal_mol": gibbs_eV * EV_TO_KCAL_MOL,
            "ZPE_kcal_mol": zpe_eV * EV_TO_KCAL_MOL,
        }
    finally:
        with contextlib.suppress(Exception):
            vib.clean()
        if cleanup:
            for p in scratch_dir.parent.glob(scratch_dir.name + '*'):
                with contextlib.suppress(Exception):
                    if p.is_file():
                        p.unlink()
