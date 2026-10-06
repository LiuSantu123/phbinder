# pH-sensitive binder screening

This is a resumable, batch-oriented project for ranking protein binder structures by
their potential to bind at `pH_on` and weaken at `pH_off`. It is a computational
prioritization tool; it does not prove a binding switch and should be followed by
experimental measurements.

## Install

```bash
cd /path/to/phbinder
python -m venv .venv
. .venv/bin/activate
pip install -e .
```

Detailed installation and external-tool setup is in [`docs/INSTALL.md`](docs/INSTALL.md)
and [`docs/EXTERNAL_TOOLS.md`](docs/EXTERNAL_TOOLS.md).

Check the local installation with:

```bash
phbinder doctor --config configs/site.yaml
```

Run the public synthetic example:

```bash
phbinder --input examples/structures --output /tmp/phbinder_example.csv
```

The fast mode only needs Python, NumPy and pandas. CIF input additionally needs
`biotite`. PROPKA/PDB2PQR/APBS/Rosetta/MM-PBSA are optional and are supplied via
`configs/default.yaml` or a site-specific YAML file. Paths can be supplied through
`PHBINDER_PROPKA`, `PHBINDER_PDB2PQR`, `PHBINDER_APBS`, `PHBINDER_ROSETTA` and
`PHBINDER_MMPBSA`. A missing optional executable
is recorded in the run metadata instead of silently pretending it ran.

## Run a batch (direct CSV mode)

The shortest interface takes a structure directory and writes a ranked CSV
directly. No per-design cache is created unless an external PROPKA executable is
available/configured.

```bash
phbinder \
  --input /path/to/structures \
  --output /path/to/results.csv \
  --ph-on 6.5 \
  --ph-off 7.4 \
  --workers 8
```

For resumable runs with metadata and per-design caches, use the explicit command:

```bash
phbinder run \
  --input /path/to/structures \
  --out /path/to/results \
  --config configs/default.yaml \
  --top 20
```

The input directory may contain PDB and CIF files. By default chains A and B are
target and binder. Each candidate is cached in `results/per_design/<id>/metrics.json`;
rerunning resumes without recomputation. Use `--force` to invalidate the cache.

Outputs:

- direct mode output CSV: one ranked row per candidate;
- cached mode `metrics.csv`: one row per candidate;
- `ranked.csv` or the requested rank output: combined ranking;
- `ranked_top20.csv`: selected candidates;
- `run_metadata.json`: config and completion counts.

## Stages and interpretation

The project separates structure/interface measurement, pH-sensitive residue scoring,
optional external electrostatics/energy stages, and ranking. PROPKA is invoked when
`tools.propka` (or `propka3` on `PATH`) is available. PDB2PQR/APBS are invoked when
both are configured. Rosetta and MM/PBSA are callable refinement adapters and are
kept opt-in because their setup varies by installation. A result without PROPKA is labeled
`ph_method=heuristic_interface_titratable_prior` and must not be reported as APBS.

Recommended modes:

- `fast`: contact/interface prior for large libraries;
- `standard`: PROPKA + APBS for the first shortlist;
- `precise`: add Rosetta/FoldX and MM/PBSA or constant-pH MD for the final 5–10.

## Reproducibility

Keep the YAML config, `run_metadata.json`, software versions, target MSA/template,
and the exact input manifest with each result directory. The final score is a ranking
prior, not an experimental affinity or a guarantee of pH selectivity.
