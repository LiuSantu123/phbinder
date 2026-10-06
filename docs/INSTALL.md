# phbinder installation

## 1. Core installation

```bash
cd /path/to/phbinder
conda env create -f environment.yml
conda activate phbinder
python -m pip install -e .
phbinder --help
```

If Conda is unavailable:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
```

Install `biotite` for CIF input. PDB-only screening needs only the dependencies
listed in `pyproject.toml`.

## 2. Configure external tools

Copy the example and edit it:

```bash
cp configs/site.example.yaml configs/site.yaml
$EDITOR configs/site.yaml
```

Or use environment variables without editing YAML:

```bash
export PHBINDER_PROPKA=/path/to/propka3
export PHBINDER_PDB2PQR=/path/to/pdb2pqr
export PHBINDER_APBS=/path/to/apbs
export PHBINDER_ROSETTA=/path/to/InterfaceAnalyzer.linuxgccrelease
export PHBINDER_MMPBSA=/path/to/MMPBSA.py
```

The YAML file is passed with `--config configs/site.yaml`. Missing optional tools
are recorded and do not abort the fast structure-only screen.

## 3. Recommended software environments

Keep the core Python environment separate from scientific tool environments:

```text
phbinder       Python, NumPy, pandas, PyYAML, Biotite
phbinder-apbs  PROPKA, PDB2PQR, APBS
phbinder-amber AmberTools, MMPBSA.py, OpenMM (optional)
phbinder-rosetta Rosetta binaries (license required)
```

Do not commit binary software, license files, MSA databases or large model
parameters to GitHub. Record their versions with the run metadata instead.

## 4. Slurm

The template in `scripts/slurm_screen.sbatch` follows the two-GPU node policy,
but the structure screen itself is CPU-bound. Request a GPU only when the same
job also runs an upstream predictor or GPU molecular dynamics.
