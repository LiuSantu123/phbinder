# External tool interfaces

The configuration exposes one executable path per optional tool:

| Config key | Expected executable | Purpose |
|---|---|---|
| `tools.propka` | `propka3` | pKa estimates for titratable residues |
| `tools.pdb2pqr` | `pdb2pqr` | pH-specific charge/radius preparation |
| `tools.apbs` | `apbs` | Poisson–Boltzmann electrostatic energy |
| `tools.rosetta_interface_analyzer` | InterfaceAnalyzer binary | interface energy and buried area |
| `tools.mmpbsa` | `MMPBSA.py` | MM/PBSA refinement |

The current direct screen executes PROPKA when available and runs the paired
PDB2PQR/APBS energy calculation when both executables are configured. Rosetta
and MM/PBSA are exposed as callable adapters but remain opt-in refinement stages,
because their command-line options, licenses and force-field setup vary by
installation. Their paths are recorded in configuration rather than hard-coded
into the core parser.

Every production run should save:

- the exact YAML configuration;
- `phbinder --help`/package version;
- `propka3 --version`, `pdb2pqr --version`, `apbs --version` where supported;
- Rosetta and AmberTools release identifiers;
- input structure SHA256 values.

AF3, Boltz/Boltz2 and MPNN/ProtonPottsMPNN are upstream GPU tools. Their outputs
can be supplied as PDB/CIF inputs; they are not required to run the CPU screen.
