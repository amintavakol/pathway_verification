from __future__ import annotations

from pathlib import Path

from rxnfe.io.xyz_io import write_xyz

try:
    from rdkit import Chem
except Exception:
    Chem = None


def write_selected_conformer_xyz(sdf_path: str | Path, species_id: str, conformer_id: int, out_xyz: str | Path) -> None:
    if Chem is None:
        raise ImportError("RDKit is required to extract conformers from SDF.")
    supplier = Chem.SDMolSupplier(str(sdf_path), removeHs=False)
    if conformer_id < 0 or conformer_id >= len(supplier):
        raise IndexError(f"Conformer index {conformer_id} out of range for {sdf_path}")
    mol = supplier[conformer_id]
    if mol is None:
        raise ValueError(f"Failed to read conformer {conformer_id} from {sdf_path}")
    conf = mol.GetConformer()
    symbols = []
    coords = []
    for atom in mol.GetAtoms():
        pos = conf.GetAtomPosition(atom.GetIdx())
        symbols.append(atom.GetSymbol())
        coords.append([pos.x, pos.y, pos.z])
    write_xyz(symbols, coords, out_xyz, comment=f"{species_id} conf {conformer_id}")
