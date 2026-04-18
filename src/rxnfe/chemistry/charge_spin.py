from __future__ import annotations

try:
    from rdkit import Chem
except Exception:
    Chem = None


def formal_charge_from_smiles(smiles: str) -> int:
    if Chem is None:
        return 0
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return 0
    return sum(atom.GetFormalCharge() for atom in mol.GetAtoms())


def default_spin_multiplicity(smiles: str) -> int:
    if Chem is None:
        return 1
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return 1
    n_rad = sum(atom.GetNumRadicalElectrons() for atom in mol.GetAtoms())
    return n_rad + 1
