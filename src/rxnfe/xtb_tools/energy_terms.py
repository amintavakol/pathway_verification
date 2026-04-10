from __future__ import annotations


def compose_free_energy(E_elec_kcal_mol: float, thermal_corr_kcal_mol: float, TS_kcal_mol: float) -> float:
    return E_elec_kcal_mol + thermal_corr_kcal_mol - TS_kcal_mol
