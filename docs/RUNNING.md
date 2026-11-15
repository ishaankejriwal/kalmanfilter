# Running the experiments

Run the commands below from the repository root with the Python environment
from the [installation instructions](../README.md#installation) active. To
rebuild figures from saved results, follow
[Reproduce the paper](../README.md#reproduce-the-paper).

Processing raw inputs requires the basin mask, which we do not distribute.
The archived basin tables let you run the later stages without it.

## Input data

Git excludes raw inputs. The data archive contains processed basin tables and
row-level result files, as described in the [deposit notes](DEPOSIT_README.md).
Those files support the tables and the figures without basin maps. A full
pipeline run needs the raw inputs below.

| Input | Path | Source |
|---|---|---|
| CSR RL0603M mascons | `CSR_GRACE_GRACE-FO_RL0603_Mascons_all-corrections.nc` (repository root) | [CSR mascon page](http://www2.csr.utexas.edu/grace/RL0603_mascons.html) |
| CSR mapping file and land mask | `data/raw/csr_ancillary/CSR_GRACE_GRACE-FO_RL0603_mascons_mapping_file.nc`, `data/raw/csr_ancillary/CSR_GRACE_GRACE-FO_RL06_Mascons_v02_LandMask.nc` | CSR mascon page, ancillary files |
| JPL RL06.3Mv04 CRI mascons (JPL runs only) | Path supplied with `--mascon-file` | PO.DAAC, doi:10.5067/TEMSC-3JC634 |
| Basin mask | `HydroShed+Mascon_Basins_L3.nc` (repository root) | Unreleased. See [Basin partition](DEPOSIT_README.md#basin-partition). |
| ERA5-Land monthly means | `data/raw/era5/` | `python scripts/download_era5.py` |
| Climate indices | `data/processed/indices.csv` | `python scripts/download_indices.py` |
| GRACE-FCast hindcast (Li and Kusche) | `data/raw/li2026/CSR-FCast/global_gridded/`, `data/raw/li2026/JPL-FCast/global_gridded/` | [PANGAEA, doi:10.1594/PANGAEA.973113](https://doi.pangaea.de/10.1594/PANGAEA.973113) |

`download_era5.py` requests 11 ERA5-Land variables from the Copernicus Climate
Data Store at 0.5° for 2001 through May 2026. It writes one file per year
(`era5_land_monthly_<year>.nc`). The script needs a CDS account with an API key
configured for `cdsapi`. It skips years already on disk, so a rerun resumes an
interrupted download.

`download_indices.py` fetches the indices from NOAA PSL, CPC, and NCEI. It needs
no account. `scripts/inspect_inputs.py` prints the structure of the NetCDF
inputs and leaves the files unchanged.

## Pipeline

`scripts/run_chain.py` runs the pipeline steps in dependency order. Before each
step, it checks that the declared inputs exist. After each step, it checks that
the step rewrote every declared output. The chain stops at the first failure.
Each step logs to `results/chain_<step>.log`.

1. List the steps and their inputs and outputs:

   ```powershell
   python scripts/run_chain.py --list                # steps with their inputs and outputs
   ```

2. Run the default list:

   ```powershell
   python scripts/run_chain.py                       # default list
   ```

3. To run the extended experiments, run the extended list after the default list:

   ```powershell
   python scripts/run_chain.py --extended            # extended list only
   ```

To select individual steps, use `--steps`. This example runs the LSTM,
the sensitivity experiment, and the figures in that order:

```powershell
python scripts/run_chain.py --steps phase7_lstm flat12_train85 figures
```

The default list has 12 steps and does not need torch:

```text
build_basin build_era5 build_li phase2 kalman flat12_ridge kalman_mission
r0_ablation ladder li_comparison conventional_metrics manifest
```

The default list writes the result files behind Tables 2, 3, and 5, Appendices B
and C, and Fig. 4. Three separate scripts supply the analyses in Sects. 3.1, 4.1,
and 4.5. After the default list completes, run these scripts:

1. Run `scripts/climatology_offset.py`.
2. Run `scripts/kalman_gain_correlates.py`.
3. Run `scripts/centimeter_contrasts.py`.

The extended list contains these steps:

- The neighbor experiments of Sect. 4.6
- The nonlinear models of Table 4 and Fig. 6
- The KF-R12E refit on the LSTM's training months (`flat12_train85`)
- Experiments outside the paper
- The `figures` step.

`--extended` runs only the extended list. `--steps` runs the named steps in the
given order. Use either `--steps` or `--extended` for a single invocation.

The `figures` step reads the basin mask and outputs from `phase7_lstm` and
`flat12_train85`. The data archive contains those outputs.
The `stacked_ens` rows of `results/conventional_metrics_summary.csv` need the
extended `phase8_h13` and `phase8_h46` outputs. A run of the default list alone
writes that table without those rows.

Most default steps take minutes. `kalman_mission` takes about 30 minutes. The
extended neural experiments take 2 to 9 hours each on a CPU.

## JPL mascons

To run the current JPL pipeline, supply the product path with `--mascon-file`:

```powershell
python scripts/run_chain.py --source jpl --mascon-file data/raw/GRCTellus.JPL.200204_202606.GLO.RL06.3M.MSCNv04CRI.nc
```

Without `--mascon-file`, the chain uses
`data/raw/GRCTellus.JPL.200204_202604.GLO.RL06.3M.MSCNv04.nc`. The chain writes
JPL processed tables to `data/processed/jpl/` and results to `results/jpl/`.
Both products use the same ERA5-Land and index tables. The JPL run leaves CSR
results unchanged.

If the file has a `scale_factor` field, the pipeline applies it and records
the choice in `basin_meta.csv`. The CRI product has this field.
`--no-scale-factors` disables this behavior. Six small-island basins have no
valid cells in the CRI product, which leaves 228 basins.

Place the GRACE-FCast JPL member under
`data/raw/li2026/JPL-FCast/global_gridded/`. The `figures` step supports CSR
only because it checks the CSR values in the paper.

The archived JPL run used commit `71be5ec` of the JPL pipeline branch. The
archive `kalmanfilter-71be5ec-jpl-run-code.zip` contains that revision. The
current JPL steps differ from that revision. The archived tables contain no
flat-12 models.

To regenerate the archived JPL tables in `results/jpl/`, use the archived
revision. The [JPL run record](../results/jpl/RUN_PROVENANCE.md) gives the
product file and its checksum, run dates, seeds, and comparison populations.
The [deposit notes](DEPOSIT_README.md) describe the three archives.

## Comparison populations

For the GRACE-FCast comparisons, a basin qualifies for `joint_full_cells` if
it contains both:

- Every 0.25-degree subcell of at least one native mascon
- All 16 subcells of at least one finite 1-degree GRACE-FCast cell.

`all_matched` keeps every basin and month available to all compared models.

See the [archive manifest](ARCHIVE_MANIFEST.md#conventions) for score orientation
and units, and Table A1 of the manuscript for model identifiers.
