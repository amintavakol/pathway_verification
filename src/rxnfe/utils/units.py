from __future__ import annotations

HARTREE_TO_KCAL_MOL = 627.509474
KCAL_MOL_TO_HARTREE = 1.0 / HARTREE_TO_KCAL_MOL


def hartree_to_kcal_mol(x: float) -> float:
    return x * HARTREE_TO_KCAL_MOL


def kcal_mol_to_hartree(x: float) -> float:
    return x * KCAL_MOL_TO_HARTREE
