from __future__ import annotations

import numpy as np
import pandas as pd


def boltzmann_weights(energies_kcal_mol: np.ndarray, temperature_K: float = 298.15, R_kcal_mol_K: float = 0.0019872041) -> np.ndarray:
    energies = np.asarray(energies_kcal_mol, dtype=float)
    shifted = energies - energies.min()
    weights = np.exp(-shifted / (R_kcal_mol_K * temperature_K))
    weights = weights / weights.sum()
    return weights


def boltzmann_average(energies_kcal_mol: np.ndarray, temperature_K: float = 298.15) -> float:
    w = boltzmann_weights(energies_kcal_mol, temperature_K=temperature_K)
    return float(np.sum(w * np.asarray(energies_kcal_mol, dtype=float)))


def boltzmann_average_dataframe(df: pd.DataFrame, energy_col: str = "G_kcal_mol", temperature_K: float = 298.15) -> dict:
    energies = df[energy_col].to_numpy(dtype=float)
    weights = boltzmann_weights(energies, temperature_K=temperature_K)
    out = df.copy()
    out["boltzmann_weight"] = weights
    return {
        "table": out,
        "G_min_kcal_mol": float(energies.min()),
        "G_boltzmann_kcal_mol": float(np.sum(weights * energies)),
        "n_conformers": int(len(out)),
    }
