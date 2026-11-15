# Data and code for "A Kalman filter benchmark for data-driven forecasts of GRACE terrestrial water storage"

Ishaan Kejriwal and Ian Wang. This deposit accompanies the manuscript submitted to
Hydrology and Earth System Sciences.

## Contents

The deposit has three archives. The code and data archives unpack into the same folder,
`kalmanfilter-<commit>/`.

`kalmanfilter-<commit>-code.zip` is the repository at the commit cited in the
manuscript, without our working notes and submission tooling. It holds the `gracefc`
package (`src/`), the experiment and figure scripts (`scripts/`), every result table
behind the manuscript (`results/*.csv`, `results/jpl/*.csv`), the figures and the LaTeX
source. `README.md` describes the pipeline, and `docs/ARCHIVE_MANIFEST.md` maps each
manuscript table and figure to the result file and column it comes from.

`kalmanfilter-<commit>-data.zip` holds the files that git leaves out for size, plus a
copy of this readme:

| Path | Content |
|---|---|
| `results/*_predictions.csv` | Row-level forecasts on the CSR mascon product, one row per model, basin, issue month and lead time. Predictions and targets are in standardized units; `phase2_baseline_predictions.csv` also gives them in cm (`target`, `pred`) next to the standardized columns |
| `results/*_placebo_basin.csv`, `results/phase3b_placebo_monthly.csv` | Null draws for the neighbor and surrogate tests (the smaller placebo tables are in the code archive) |
| `results/SHA256_MANIFEST_LIVE.csv` | SHA-256 checksums of the 25 CSR files above |
| `results/jpl/*_predictions.csv`, `results/jpl/*_placebo_basin.csv`, `results/jpl/*_placebo_monthly.csv`, `results/jpl/kalman_fold_params.pkl` | The same row-level files for the JPL mascon product (33 files), including the fitted Kalman parameters as a Python pickle; load it only in the pinned environment |
| `results/jpl/SHA256_MANIFEST_LIVE.csv`, `results/jpl/RUN_PROVENANCE.md` | SHA-256 checksums of all 92 generated JPL result files (the 33 above and the tables in the code archive), and the JPL run record: product release, run dates, seeds, input checksums |
| `data/processed/basin_month_twsa_global.csv` | Monthly basin-average CSR TWSA (cm of equivalent water height) |
| `data/processed/basin_meta.csv` | Basin labels (`name`, B001 to B284), areas, centroids and the exclusion flags of Sect. 2.2 |
| `data/processed/era5_basin_month.csv`, `era5_basin_coverage.csv` | Monthly basin-average ERA5-Land variables and their land-cell coverage |
| `data/processed/indices.csv` | Monthly climate indices |
| `data/processed/li2026_csr_basin_forecasts.csv`, `li2026_basin_coverage.csv` | The CSR member of GRACE-FCast, aggregated by us to the basins above, and per-basin coverage |
| `data/processed/jpl/basin_month_twsa_global.csv`, `basin_meta.csv` | Monthly basin-average TWSA (cm) and basin metadata with the JPL exclusion flags, for the JPL RL06.3Mv04 CRI product |
| `data/processed/jpl/li2026_jpl_basin_forecasts.csv`, `li2026_basin_coverage.csv` | The JPL member of GRACE-FCast, aggregated by us to the basins above, and per-basin coverage |

`kalmanfilter-71be5ec-jpl-run-code.zip` unpacks into `kalmanfilter-71be5ec/`. It holds
`src/`, `scripts/` and `requirements-lock.txt` at commit `71be5ec` of the JPL
pipeline branch, the code that produced the JPL tables and row-level files in
`results/jpl/` (run record in `results/jpl/RUN_PROVENANCE.md`). Three parts of that
commit are left out because they contain basin names from the mask file (see "Basin
partition" below): `tests/`, `scripts/make_figures.py` and `src/gracefc/basins.py`. The
main code archive has their current versions; to run this revision, copy
`src/gracefc/basins.py` from there (its code differs only in the basin labels). The CSR results and the
figures come from the main code archive. The JPL steps in the main archive have changed
since this revision: it adds the `flat12_ridge` and `kalman_mission` steps, which the JPL
run did not have. Regenerate the archived JPL tables with this revision.

Appendix A (Table A1) of the manuscript maps model names to the `model` identifiers in
these files. Every JPL table and figure value is in `results/jpl/*.csv` in the code
archive.

`data/processed/jpl/li2026_basin_coverage.csv` is the file the JPL runs used. It predates
the `n_full_native_mascons` column that the current comparison code reads. To rerun the
JPL comparison with this file, add that column from `n_full_jpl_mascons` in
`data/processed/jpl/basin_meta.csv`, matched on `name`.
`scripts/build_li_basin_series.py --source jpl` writes that column.

`data/processed/indices.csv` was downloaded again from NOAA PSL on 16 September 2026,
after the runs that used it. NOAA revises some indices, so its values may differ slightly
from the run inputs. The climate indices enter one benchmark model only.

## Basin partition

The basin mask (`HydroShed+Mascon_Basins_L3.nc`) is a 0.25° partition that combines
HydroSHEDS Level-3 basins with the CSR mascon land and ocean mask. It has not been cleared
for public release and is not in this deposit. The basin series built from it are here,
so every table and Figs. 2, 3, 6 and 7 can be rebuilt without it. Figs. 1, 4 and 5 contain
basin maps and need the mask; `scripts/make_figures.py` builds only the other four when
the mask is absent. The scripts that read the mask are `build_basin_series.py`,
`build_era5_basin_table.py`, `build_li_basin_series.py`, `run_resolution_sensitivity.py`,
`inspect_inputs.py` and `make_figures.py`.

Every file identifies basins by the labels B001 to B284 in its `name` column.
`data/processed/basin_meta.csv` gives the centroid, area and continent of each label and
the numerical identifier the mask assigns to it (`id`; the water bodies B283 and B284
share one). The result and processed files were written with the mask's basin names and
relabelled afterwards; nothing else in them changed.

## Reproducing the figures and tables

Install the pinned environment with Python 3.11 and check the large files against their
manifests:

```
pip install -r requirements-lock.txt
python scripts/make_manifest.py --check
GRACEFC_SOURCE=jpl python scripts/make_manifest.py --check
python scripts/make_figures.py
```

The figure script checks each plotted headline value against its source table. Without
the basin mask it builds Figs. 2, 3, 6 and 7 (see "Basin partition"). It needs
the Arial font, and Cartopy downloads the Natural Earth base map on first use. Rerunning
the experiments from raw data follows `README.md` and needs the third-party inputs below.

## Third-party data

The processed inputs are derived from CSR RL06 mascons (Save et al., 2016; Save, 2020),
JPL RL06.3Mv04 mascons (Wiese et al., 2023), ERA5-Land (Muñoz-Sabater et al., 2021), NOAA
PSL climate indices, the GRACE-FCast hindcast of Li and Kusche (PANGAEA, CC BY 4.0) and
HydroSHEDS (Lehner and Grill, 2013). The files derived from ERA5-Land carry the
attribution Copernicus requires:
"Contains modified Copernicus Climate Change Service information 2026."
Cite the original products when reusing these files.

## Licence

Code: MIT (see `LICENSE`), except the Copernicus LaTeX class, style and template files
under `paper/`, which keep Copernicus's terms. Data and result files: CC BY 4.0. Files
derived from the third-party products above remain subject to those products' attribution
terms.
