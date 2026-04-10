from __future__ import annotations


def strip_atom_mapping(smiles: str) -> str:
    # Conservative placeholder. Keep the original if you rely on atom-mapped strings elsewhere.
    import re
    return re.sub(r":\d+", "", smiles)
