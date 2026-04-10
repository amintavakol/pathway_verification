from __future__ import annotations

try:
    from rdkit import Chem
except Exception:
    Chem = None


def validate_smiles(smiles: str) -> bool:
    if Chem is None:
        return bool(smiles)
    return Chem.MolFromSmiles(smiles) is not None
