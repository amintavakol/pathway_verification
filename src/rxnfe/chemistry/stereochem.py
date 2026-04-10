from __future__ import annotations

try:
    from rdkit import Chem
except Exception:
    Chem = None


def has_defined_stereochemistry(smiles: str) -> bool:
    if Chem is None:
        return False
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return False
    return any(atom.HasProp('_CIPCode') for atom in mol.GetAtoms())
