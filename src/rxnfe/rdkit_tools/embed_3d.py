from __future__ import annotations

from pathlib import Path

from rxnfe.io.xyz_io import write_xyz
from rxnfe.rdkit_tools.mol_from_smiles import mol_from_smiles

try:
    from rdkit import Chem
    from rdkit.Chem import AllChem
except Exception:
    Chem = None
    AllChem = None


def build_initial_3d(smiles: str, out_sdf: str | Path, out_xyz: str | Path, random_seed: int = 42) -> None:
    if Chem is None or AllChem is None:
        raise ImportError("RDKit is required for this stage.")
    mol = mol_from_smiles(smiles)
    params = AllChem.ETKDGv3()
    params.randomSeed = random_seed
    params.useRandomCoords = True
    status = AllChem.EmbedMolecule(mol, params)
    if status != 0:
        raise RuntimeError(f"RDKit embedding failed for SMILES: {smiles}")
    AllChem.UFFOptimizeMolecule(mol)
    out_sdf = Path(out_sdf)
    out_sdf.parent.mkdir(parents=True, exist_ok=True)
    writer = Chem.SDWriter(str(out_sdf))
    writer.write(mol)
    writer.close()
    conf = mol.GetConformer()
    coords = []
    symbols = []
    for atom in mol.GetAtoms():
        pos = conf.GetAtomPosition(atom.GetIdx())
        coords.append([pos.x, pos.y, pos.z])
        symbols.append(atom.GetSymbol())
    write_xyz(symbols, coords, out_xyz, comment=smiles)
