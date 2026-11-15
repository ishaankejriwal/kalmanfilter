# A Kalman filter benchmark for GRACE water storage forecasts

Code and result tables for Kejriwal and Wang, "A Kalman filter benchmark for
data-driven forecasts of GRACE terrestrial water storage", submitted to
Hydrology and Earth System Sciences (HESS).

The study forecasts deseasonalized GRACE and GRACE-FO terrestrial water storage
anomalies in 234 river basins at leads of 1 to 6 months. It evaluates a per-basin
AR(1) Kalman filter against damped persistence, ridge corrections, nonlinear
models, and Li and Kusche's GRACE-FCast. The main results use CSR RL0603M
mascons. A second experiment uses JPL RL06.3Mv04 CRI mascons.

## Installation

Use Python 3.11. The dependency versions in
[requirements-lock.txt](requirements-lock.txt) come from a Python 3.11.4
environment. The experiments run on a CPU.

Run these PowerShell commands from the repository root on Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-lock.txt
python -m pytest tests/ -q
```

If processed data or prediction files are absent, pytest skips the tests that
need them. A successful test run can include skipped tests.

Run subsequent commands from the repository root with this environment active.
The pipeline uses the Python interpreter that launches it.

## Data

The repository contains result tables. The data archive contains processed
basin inputs and row-level predictions. The
[deposit notes](docs/DEPOSIT_README.md) describe the archive contents.

Before you run the reproduction commands, unpack the code and data archives
into the same folder.

We do not have clearance to release the basin mask,
`HydroShed+Mascon_Basins_L3.nc`. The available inputs support these tasks:

| Task | Required inputs |
|---|---|
| Inspect result tables | Repository files |
| Rebuild tables and Figs. 2, 3, 6, and 7 | Repository files and data archive |
| Build basin maps in Figs. 1, 4, and 5 | Repository files, data archive, and basin mask |
| Run the pipeline from raw data | Basin mask and the inputs in the [experiment guide](docs/RUNNING.md#input-data) |

## Reproduce the paper

This procedure checks archived result files and regenerates figures. The
figure script needs Arial. On first use, Cartopy downloads the Natural Earth
base map.

1. Check the CSR result files:

   ```powershell
   $env:GRACEFC_SOURCE = "csr"
   python scripts/make_manifest.py --check
   ```

2. Check the JPL result files:

   ```powershell
   $env:GRACEFC_SOURCE = "jpl"
   python scripts/make_manifest.py --check
   ```

3. Generate the figures:

   ```powershell
   $env:GRACEFC_SOURCE = "csr"
   python scripts/make_figures.py
   ```

The checksum checks use `results/SHA256_MANIFEST_LIVE.csv` and
`results/jpl/SHA256_MANIFEST_LIVE.csv`. The figure script writes PDF and 300 dpi
PNG files to `figures/`. It checks headline values against those in the paper
and stops if they differ. Without the basin mask, it builds only Figs. 2, 3, 6,
and 7.

The [archive manifest](docs/ARCHIVE_MANIFEST.md) identifies the source files and
columns for each manuscript table, figure, and quoted number. It also explains
score conventions, units, and model identifiers. The conventions cover the
reversed skill orientation in the archived JPL GRACE-FCast comparison.

## Run the experiments

1. Prepare the inputs in the [experiment guide](docs/RUNNING.md#input-data).
2. List the pipeline steps and their inputs and outputs:

   ```powershell
   python scripts/run_chain.py --list
   ```

3. Run the default pipeline:

   ```powershell
   python scripts/run_chain.py
   ```

The default chain builds the basin tables and runs the benchmark experiments.
It checks inputs and outputs at each step and stops at the first failure.
Most steps take minutes. `kalman_mission` takes about 30 minutes.
The extended neural experiments take 2 to 9 hours each on a CPU.

See the [experiment guide](docs/RUNNING.md) for extended runs, individual steps,
manuscript analyses, and JPL options. The archived JPL run used revision
`71be5ec`. To reproduce those results, use that archived revision.

## Documentation

- [Code map](docs/CODE_MAP.md): library modules and experiment scripts.
- [Results](results/README.md): result files and naming conventions.
- [Archive manifest](docs/ARCHIVE_MANIFEST.md): sources for the paper's numbers.
- [Deposit notes](docs/DEPOSIT_README.md): archive contents and data attribution.
- [JPL run record](results/jpl/RUN_PROVENANCE.md): inputs, checksums and run settings.

## Citation

Kejriwal, I. and Wang, I.: A Kalman filter benchmark for data-driven forecasts of
GRACE terrestrial water storage, submitted to Hydrology and Earth System
Sciences, 2026.

Kejriwal, I. and Wang, I.: Data and code for "A Kalman filter benchmark for
data-driven forecasts of GRACE terrestrial water storage", Zenodo, 2026.

We will add the deposit DOI.

## License

We release the code under the [MIT license](LICENSE). The Copernicus LaTeX
class, style, and template files under `paper/` retain Copernicus's terms.

We release data and result files under CC BY 4.0. Files derived from CSR and
JPL mascons, ERA5-Land, NOAA indices, GRACE-FCast, and HydroSHEDS remain subject
to those products' attribution terms.
