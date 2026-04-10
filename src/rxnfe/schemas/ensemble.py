from __future__ import annotations

from pydantic import BaseModel


class EnsembleRecord(BaseModel):
    species_id: str
    temperature_K: float
    n_conformers: int
    G_min_kcal_mol: float
    G_boltzmann_kcal_mol: float
