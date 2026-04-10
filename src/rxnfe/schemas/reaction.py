from __future__ import annotations

from pydantic import BaseModel


class ReactionRecord(BaseModel):
    reaction_id: str
    species_smiles: str
