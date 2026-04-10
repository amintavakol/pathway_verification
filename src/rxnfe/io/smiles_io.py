from __future__ import annotations

from typing import List


def split_pathway_states(species_smiles: str) -> List[str]:
    return [chunk.strip() for chunk in species_smiles.split(">>") if chunk.strip()]
