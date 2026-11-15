# Data and code for "A Kalman filter benchmark for data-driven forecasts of GRACE terrestrial water storage"

Ishaan Kejriwal and Ian Wang. This deposit accompanies the manuscript submitted to
Hydrology and Earth System Sciences.

## Contents

The deposit contains three archives. The code and data archives share the top-level directory
`kalmanfilter-v1.0/`.

`kalmanfilter-v1.0-code.zip` contains release v1.0 of the repository
(https://github.com/ishaankejriwal/kalmanfilter). It includes the `gracefc`
package (`src/`), experiment and figure scripts (`scripts/`), all result tables
used in the manuscript (`results/*.csv`, `results/jpl/*.csv`) and the figures. `README.md` documents the pipeline. `docs/ARCHIVE_MANIFEST.md` identifies the
source files and columns for each manuscript table and figure.

`kalmanfilter-v1.0-data.zip` contains large files excluded from Git and a copy of
this README:

| Path | Content |
|---|---|
| `results/*_predictions.csv` | Row-level forecasts for the CSR mascon product, with one row per model, basin, issue month and lead time. Predictions and targets are in standardized units; `phase2_baseline_predictions.csv` also includes values in cm (`target`, `pred`) alongside the standardized columns |
| `results/*_placebo_basin.csv`, `results/phase3b_placebo_monthly.csv` | Null draws for the neighbor and surrogate tests (the smaller placebo tables are in the code archive) |
| `results/SHA256_MANIFEST_LIVE.csv` | SHA-256 checksums of the 25 CSR files above |
| `results/jpl/*_predictions.csv`, `results/jpl/*_placebo_basin.csv`, `results/jpl/*_placebo_monthly.csv`, `results/jpl/kalman_fold_params.pkl` | Corresponding row-level files for the JPL mascon product (33 files), including fitted Kalman parameters stored as a Python pickle; load this file only in the pinned environment |
| `results/jpl/SHA256_MANIFEST_LIVE.csv`, `results/jpl/RUN_PROVENANCE.md` | SHA-256 checksums of all 92 generated JPL result files (the 33 above and the tables in the code archive), and run provenance: product release, run dates, seeds and input checksums |
| `data/processed/basin_month_twsa_global.csv` | Monthly basin-average CSR TWSA (cm of equivalent water height) |
| `data/processed/basin_meta.csv` | Basin labels (`name`, B001 to B284), areas, centroids and the exclusion flags of Sect. 2.2 |
| `data/processed/era5_basin_month.csv`, `era5_basin_coverage.csv` | Monthly basin-average ERA5-Land variables and their land-cell coverage |
| `data/processed/indices.csv` | Monthly climate indices |
| `data/processed/li2026_csr_basin_forecasts.csv`, `li2026_basin_coverage.csv` | The CSR member of GRACE-FCast, aggregated to the study basins, and per-basin coverage |
| `data/processed/jpl/basin_month_twsa_global.csv`, `basin_meta.csv` | Monthly basin-average TWSA (cm) and basin metadata with the JPL exclusion flags, for the JPL RL06.3Mv04 CRI product |
| `data/processed/jpl/li2026_jpl_basin_forecasts.csv`, `li2026_basin_coverage.csv` | The JPL member of GRACE-FCast, aggregated to the study basins, and per-basin coverage |

`kalmanfilter-71be5ec-jpl-run-code.zip` extracts to `kalmanfilter-71be5ec/`. It contains
`src/`, `scripts/` and `requirements-lock.txt` at commit `71be5ec` of the JPL
pipeline branch. This revision produced the JPL tables and row-level files in
`results/jpl/`; the run is documented in `results/jpl/RUN_PROVENANCE.md`. Three parts of
that commit are excluded because they contain basin names from the mask file (see
"Basin partition"): `tests/`, `scripts/make_figures.py` and `src/gracefc/basins.py`.
Their current versions are included in the main code archive. To run the archived JPL
revision, copy `src/gracefc/basins.py` from the main code archive; the two versions
differ only in basin labels. Use the main code archive for the CSR results and figures.
Its JPL pipeline also includes the `flat12_ridge` and `kalman_mission` steps, which were
not part of the archived run. Use the archived JPL revision to regenerate its tables.

Appendix A (Table A1) of the manuscript maps model names to the `model` identifiers in
these files. All JPL table and figure values are in `results/jpl/*.csv` in the code
archive.

The archived JPL runs used `data/processed/jpl/li2026_basin_coverage.csv`, which lacks
the `n_full_native_mascons` column required by the current comparison code. To use
this file with the current code, populate that column from `n_full_jpl_mascons` in
`data/processed/jpl/basin_meta.csv`, matching rows on `name`.
`scripts/build_li_basin_series.py --source jpl` writes the required column.

`data/processed/indices.csv` was downloaded again from NOAA PSL on 16 September 2026,
after the experiments were run. NOAA revises some indices, so the archived values may
differ slightly from those used in the runs. Climate indices are used in one benchmark
model only.

## Basin partition

The basin mask (`HydroShed+Mascon_Basins_L3.nc`) is a 0.25° partition that combines
HydroSHEDS Level-3 basins with the CSR mascon land and ocean mask. It has not been cleared
for public release and is excluded from this deposit. The derived basin series are
included and support reproduction of all tables and Figs. 2, 3, 6 and 7 without the mask.
Figs. 1, 4 and 5 contain basin maps and require the mask; `scripts/make_figures.py`
generates only the other four figures when the mask is absent. The scripts that read
the mask are `build_basin_series.py`,
`build_era5_basin_table.py`, `build_li_basin_series.py`, `run_resolution_sensitivity.py`,
`inspect_inputs.py` and `make_figures.py`.

Files identify basins by labels B001 to B284 in the `name` column.
`data/processed/basin_meta.csv` lists each basin's centroid, area, continent and
numerical mask identifier (`id`; the water bodies B283 and B284 share one identifier).
The result and processed files originally used the basin names from the mask. Only
these labels were changed for the deposit.

## Reproducing the figures and tables

With Python 3.11, install the pinned dependencies, verify the large files against their
checksum manifests and generate the figures:

```
pip install -r requirements-lock.txt
python scripts/make_manifest.py --check
GRACEFC_SOURCE=jpl python scripts/make_manifest.py --check
python scripts/make_figures.py
```

The figure script checks each plotted headline value against its source table. Without
the basin mask, it generates Figs. 2, 3, 6 and 7 (see "Basin partition"). Arial is
required, and Cartopy downloads the Natural Earth base map on first use. To rerun the
experiments from raw data, follow `README.md` and obtain the third-party inputs below.

## Third-party data

The processed inputs are derived from CSR RL06 mascons (Save et al., 2016; Save, 2020),
JPL RL06.3Mv04 mascons (Wiese et al., 2023), ERA5-Land (Muñoz-Sabater et al., 2021), NOAA
PSL climate indices, the GRACE-FCast hindcast of Li and Kusche (PANGAEA, CC BY 4.0) and
HydroSHEDS (Lehner and Grill, 2013). Files derived from ERA5-Land include the required
Copernicus attribution:
"Contains modified Copernicus Climate Change Service information 2026."
Cite the original products when reusing these files.

## Licence

Code is released under the MIT licence (see `LICENSE`). Data
and result files are released under CC BY 4.0. Files derived from third-party products
remain subject to the attribution terms of those products.
