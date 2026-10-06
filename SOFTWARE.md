# Optional software

The core package is CPU-only and installs with Python, NumPy, pandas, PyYAML and
optionally Biotite for CIF input. The following tools are external adapters and
must be installed under their own licenses where applicable:

| Tool | Role | GPU |
|---|---|---|
| PROPKA | residue pKa estimates | no |
| PDB2PQR | pH-dependent PQR preparation | no |
| APBS | Poisson–Boltzmann electrostatics | usually no |
| Rosetta/FoldX | interface energy | CPU |
| AmberTools/MMPBSA.py | MM/PBSA | CPU, optional GPU |
| OpenMM/Amber constant-pH | dynamic validation | optional GPU |

Set paths with `PHBINDER_PROPKA`, `PHBINDER_PDB2PQR`, `PHBINDER_APBS`,
`PHBINDER_ROSETTA` and `PHBINDER_MMPBSA`, or in a site-specific YAML file.
AF3, Boltz and MPNN/ProtonPottsMPNN are upstream GPU workflows and are not
required for screening already-generated structures.
