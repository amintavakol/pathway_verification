from __future__ import annotations

from pydantic import BaseModel


class ConformerRecord(BaseModel):
    species_id: str
    conformer_id: str
    energy_kcal_mol: float
    selected: bool = False
