# reaction_free_energy

A Python-first pipeline for approximate thermodynamic scoring of reaction pathways represented as a single ordered sequence of states:

reactants >> intermediate_1 >> intermediate_2 >> ... >> product

The project uses:
- RDKit for SMILES parsing, stereochemistry, 3D embedding, and initial conformers
- CREST-compatible ensemble selection layout
- GFN2-xTB via tblite + ASE for geometry optimization and thermochemistry
- Boltzmann aggregation to obtain one free energy per state
- one free-energy profile per reaction

## Input format

Place a CSV file in `data/raw/` with these columns:

```csv
reaction_id,species_smiles
RXN000001,"[CH3:1][Br:2]>>[CH3:1].[Br-:2]>>[CH3:1][OH:3]"
RXN000002,"CCO>>CC[O-]>>CC=O"
```

`species_smiles` is one ordered sequence of states for one reaction.

## Main commands

Prepare species table:

```bash
python workflows/run_prepare_dataset.py --input data/raw/example_subset.csv
```

Run the full pipeline:

```bash
python workflows/run_full_pipeline.py
```

Plot one reaction profile:

```bash
python workflows/visualize_free_energy_profile.py --reaction-id RXN000001
```

## Notes

- The pipeline assumes exactly one pathway per reaction.
- Profiles are keyed only by `reaction_id`.
- Boltzmann averaging collapses sampled conformers into one state free energy per species.
