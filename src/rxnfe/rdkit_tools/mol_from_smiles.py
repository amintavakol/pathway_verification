from __future__ import annotations

from pathlib import Path

try:
    from rdkit import Chem
except Exception:
    Chem = None


def mol_from_smiles(smiles: str):
    if Chem is None:
        raise ImportError("RDKit is required for this stage.")
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Failed to parse SMILES: {smiles}")
    mol = Chem.AddHs(mol)
    return mol
