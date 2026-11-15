# Data and code for "A Kalman filter benchmark for data-driven forecasts of GRACE terrestrial water storage"

Ishaan Kejriwal and Ian Wang. This deposit accompanies the manuscript submitted to
Hydrology and Earth System Sciences.

## Contents

The deposit contains three archives. The code and data archives share the
top-level directory `kalmanfilter-v1.0/`.

`kalmanfilter-v1.0-code.zip` contains release v1.0 of the
[repository](https://github.com/ishaankejriwal/kalmanfilter). It excludes our
working notes and submission tools. The code archive contains these files:

- The `gracefc` package (`src/`)
- The experiment and figure scripts (`scripts/`)
- Every result table behind the manuscript (`results/*.csv`, `results/jpl/*.csv`)
- The figures.

`README.md` describes the pipeline. `docs/ARCHIVE_MANIFEST.md` maps each
manuscript table and figure to its source file and column.

`kalmanfilter-v1.0-data.zip` contains the files that git excludes for size,
plus a copy of this README:

| Path | Content |
|---|---|
| `results/*_predictions.csv` | CSR forecasts, with one row per model, basin, issue month, and lead time. Predictions and targets use standardized units. `phase2_baseline_predictions.csv` also gives them in cm (`target`, `pred`). |
| `results/*_placebo_basin.csv`, `results/phase3b_placebo_monthly.csv` | Null draws for the neighbor and surrogate tests (the smaller placebo tables are in the code archive) |
| `results/SHA256_MANIFEST_LIVE.csv` | SHA-256 checksums of the 25 CSR files above |
| `results/jpl/*_predictions.csv`, `results/jpl/*_placebo_basin.csv`, `results/jpl/*_placebo_monthly.csv`, `results/jpl/kalman_fold_params.pkl` | JPL forecasts, placebo draws, and fitted Kalman parameters (33 files). The parameters use Python pickle format. |
| `results/jpl/SHA256_MANIFEST_LIVE.csv`, `results/jpl/RUN_PROVENANCE.md` | SHA-256 checksums of all 92 generated JPL result files (the 33 above and the tables in the code archive), and the JPL run record: product release, run dates, seeds, input checksums |
| `data/processed/basin_month_twsa_global.csv` | Monthly basin-average CSR TWSA (cm of equivalent water height) |
| `data/processed/basin_meta.csv` | Basin labels (`name`, B001 to B284), areas, centroids and the exclusion flags of Sect. 2.2 |
| `data/processed/era5_basin_month.csv`, `era5_basin_coverage.csv` | Monthly basin-average ERA5-Land variables and their land-cell coverage |
| `data/processed/indices.csv` | Monthly climate indices |
| `data/processed/li2026_csr_basin_forecasts.csv`, `li2026_basin_coverage.csv` | Basin means of the CSR member of GRACE-FCast and per-basin coverage |
| `data/processed/jpl/basin_month_twsa_global.csv`, `basin_meta.csv` | Monthly basin-average TWSA (cm) and basin metadata with the JPL exclusion flags, for the JPL RL06.3Mv04 CRI product |
| `data/processed/jpl/li2026_jpl_basin_forecasts.csv`, `li2026_basin_coverage.csv` | Basin means of the JPL member of GRACE-FCast and per-basin coverage |

Load `results/jpl/kalman_fold_params.pkl` only in the pinned environment.

`kalmanfilter-71be5ec-jpl-run-code.zip` unpacks into `kalmanfilter-71be5ec/`.
It contains `src/`, `scripts/`, and `requirements-lock.txt` at commit `71be5ec`
of the JPL pipeline branch. That revision produced the JPL tables and row-level
files in `results/jpl/`. `results/jpl/RUN_PROVENANCE.md` records the run.

The JPL code archive excludes three parts of that commit because they contain
basin names from the mask file (see "Basin partition"):

- The `tests/` directory
- The `scripts/make_figures.py` script
- The `src/gracefc/basins.py` module.

The main code archive contains their current versions. The current
`src/gracefc/basins.py` differs from the archived version only in the basin
labels. The main code archive also contains the CSR results and figures.
Its JPL pipeline adds the `flat12_ridge` and `kalman_mission` steps, which the
archived JPL run did not include.

To regenerate the archived JPL tables:

1. Extract `kalmanfilter-71be5ec-jpl-run-code.zip`.
2. Copy `src/gracefc/basins.py` from the main code archive into the extracted
   JPL code directory.
3. Run the JPL experiments with the archived revision.

Appendix A (Table A1) of the manuscript maps model names to the `model` identifiers in
these files. Every JPL table and figure value is in `results/jpl/*.csv` in the code
archive.

The JPL runs used `data/processed/jpl/li2026_basin_coverage.csv`. That file
predates the `n_full_native_mascons` column that the current comparison code
reads.

To use that file with the current comparison code, add `n_full_native_mascons`
from `n_full_jpl_mascons` in `data/processed/jpl/basin_meta.csv`. Match the rows
on `name`. `scripts/build_li_basin_series.py --source jpl` writes that column.

We downloaded `data/processed/indices.csv` again from NOAA PSL on 16 September
2026, after the runs that used it. NOAA revises some indices, so the archived
values can differ slightly from the run inputs. Only one benchmark model uses
the climate indices.

## Basin partition

The basin mask (`HydroShed+Mascon_Basins_L3.nc`) is a 0.25° partition. It combines
HydroSHEDS Level-3 basins with the CSR mascon land and ocean mask. We do not have
clearance to release it, so this deposit excludes it.

The deposit contains the basin series from that mask. Those series support
every table and Figs. 2, 3, 6, and 7. Figs. 1, 4, and 5 contain basin maps and
need the mask. If the mask is absent, `scripts/make_figures.py` builds only the
other four figures.

These scripts read the mask:

- The `build_basin_series.py` script
- The `build_era5_basin_table.py` script
- The `build_li_basin_series.py` script
- The `run_resolution_sensitivity.py` script
- The `inspect_inputs.py` script
- The `make_figures.py` script.

Every file identifies basins by the labels B001 to B284 in its `name` column.
`data/processed/basin_meta.csv` gives each basin's centroid, area, continent, and
numerical mask identifier (`id`). The water bodies B283 and B284 share one mask
identifier. The pipeline wrote the result and processed files with the mask's
basin names. We later replaced those names with the labels and left all other
content unchanged.

## Reproducing the figures and tables

The figure script needs Arial. On first use, Cartopy downloads the Natural
Earth base map. Run these commands from the repository root.

1. Install the pinned environment with Python 3.11:

   ```
   pip install -r requirements-lock.txt
   ```

2. Check the large CSR files against their manifest:

   ```
   python scripts/make_manifest.py --check
   ```

3. Check the large JPL files against their manifest:

   ```
   GRACEFC_SOURCE=jpl python scripts/make_manifest.py --check
   ```

4. Generate the figures:

   ```
   python scripts/make_figures.py
   ```

The figure script checks each plotted headline value against its source table.
Without the basin mask, it builds Figs. 2, 3, 6, and 7 (see "Basin partition").

To rerun the experiments from raw data, follow `README.md`. Those experiments
need the third-party inputs below.

## Third-party data

We derived the processed inputs from these products:

- CSR RL06 mascons (Save et al., 2016; Save, 2020)
- JPL RL06.3Mv04 mascons (Wiese et al., 2023)
- ERA5-Land (Muñoz-Sabater et al., 2021)
- NOAA PSL climate indices
- The GRACE-FCast hindcast of Li and Kusche (PANGAEA, CC BY 4.0)
- HydroSHEDS (Lehner and Grill, 2013).

The files derived from ERA5-Land carry this required Copernicus attribution:
"Contains modified Copernicus Climate Change Service information 2026."

When you reuse these files, cite the original products.

## License

We release the code under MIT (see `LICENSE`).

We release data and result files under CC BY 4.0. Files derived from the
third-party products above remain subject to those products' attribution terms.
