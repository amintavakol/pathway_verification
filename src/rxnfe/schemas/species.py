from __future__ import annotations

from pydantic import BaseModel


class SpeciesRecord(BaseModel):
    species_id: str
    reaction_id: str
    step_index: int
    role: str
    mapped_smiles: str
    state_smiles: str
    formal_charge: int = 0
    spin_multiplicity: int = 1
