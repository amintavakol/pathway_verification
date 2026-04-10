from __future__ import annotations

from pathlib import Path
import pandas as pd

from rxnfe.rdkit_tools.mol_from_smiles import mol_from_smiles

try:
    from rdkit import Chem
    from rdkit.Chem import AllChem
except Exception:
    Chem = None
    AllChem = None


def generate_rdkit_conformers(
    smiles: str,
    n_confs: int,
    out_sdf: str | Path,
    out_csv: str | Path,
    random_seed: int = 42,
    do_mmff_relax: bool = True,
) -> pd.DataFrame:
    if Chem is None or AllChem is None:
        raise ImportError("RDKit is required for this stage.")

    mol = mol_from_smiles(smiles)

    params = AllChem.ETKDGv3()
    params.randomSeed = random_seed

    conf_ids = list(AllChem.EmbedMultipleConfs(mol, numConfs=n_confs, params=params))

    rows = []
    props = None
    mmff_ok = False

    if do_mmff_relax:
        try:
            props = AllChem.MMFFGetMoleculeProperties(mol, mmffVariant="MMFF94")
            mmff_ok = props is not None
        except Exception:
            props = None
            mmff_ok = False

    out_sdf = Path(out_sdf)
    out_sdf.parent.mkdir(parents=True, exist_ok=True)
    writer = Chem.SDWriter(str(out_sdf))

    for cid in conf_ids:
        e = None
        relax_method = None
        success = True
        error = None

        try:
            if do_mmff_relax and mmff_ok:
                ff = AllChem.MMFFGetMoleculeForceField(mol, props, confId=cid)
                if ff is not None:
                    ff.Minimize(maxIts=500)
                    e = ff.CalcEnergy()
                    relax_method = "MMFF94"
                else:
                    uff = AllChem.UFFGetMoleculeForceField(mol, confId=cid)
                    if uff is not None:
                        uff.Minimize(maxIts=500)
                        e = uff.CalcEnergy()
                        relax_method = "UFF"
                    else:
                        success = False
                        error = "Could not build MMFF or UFF force field"
            else:
                uff = AllChem.UFFGetMoleculeForceField(mol, confId=cid)
                if uff is not None:
                    uff.Minimize(maxIts=500)
                    e = uff.CalcEnergy()
                    relax_method = "UFF"
                else:
                    success = False
                    error = "Could not build UFF force field"
        except Exception as exc:
            success = False
            error = str(exc)

        if success:
            writer.write(mol, confId=cid)

        rows.append(
            {
                "conformer_id": int(cid),
                "relax_success": bool(success),
                "relax_method": relax_method,
                "ff_energy": e,
                "error": error,
            }
        )

    writer.close()

    df = pd.DataFrame(
        rows,
        columns=["conformer_id", "relax_success", "relax_method", "ff_energy", "error"],
    )

    Path(out_csv).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)
    return df