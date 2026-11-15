# JPL run record

This file records the JPL run that produced the results in this directory. Git
versions the summary and diagnostic tables. It excludes row-level predictions,
placebo draws, model state, and chain logs. The pipeline can regenerate those
files, which account for nearly all of the output size.

The Zenodo data archive contains the predictions, placebo draws, and model
state. `SHA256_MANIFEST_LIVE.csv` identifies the generated files behind the
shared tables.

## Run

- Pipeline: The JPL mascon experiment chain (`--source jpl`), with separate
  output directories from CSR
- Code revision: `71be5ec6af30e9d8f3c72549ca114c3b47071380` ("compare JPL results with
  Li"). The GRACE-FCast comparison used the working tree for that revision.
- Main suite: 2026-09-05 15:36 to 2026-09-06 01:21, America/Chicago workstation time.
- JPL basin table and GRACE-FCast comparison rerun: 2026-09-06 12:30 to 12:34,
  America/Chicago workstation time.
- Evaluation: Five frozen-origin folds with origins at 2019-06, 2020-11,
  2022-04, 2023-09, and 2025-02. The GRACE-FCast comparison has 59 issue months
  and leads 1 to 6.

## GRACE/GRACE-FO target

- File: `data/GRCTellus.JPL.200204_202606.GLO.RL06.3M.MSCNv04CRI.nc`
- Product: JPL GRACE and GRACE-FO Mascon RL06.3Mv04 CRI (source `GRACE and GRACE-FO JPL
  RL06.3Mv04-CRI`, product version `v3.0`), DOI `10.5067/TEMSC-3JC634`.
- File creation time: 2026-08-19 10:08:27 UTC
- Time coverage: 2002-04-16 to 2026-06-16
- Grid: sampled at 0.5 degrees. The native resolution is about 3-degree equal-area
  mascons.
- SHA-256: `d5a6737bd0406ef4e9ea72c825ea95c6693a15faf2027e52be491efa8cf89bbd`

JPL applied the Coastline Resolution Improvement filter to the CRI product.
The pipeline applied the NetCDF `scale_factor` field. The run did not use
`--no-scale-factors`. Every row of `data/processed/jpl/basin_meta.csv` records
`scale_factors_applied=True`. The target reader uses JPL's official metadata for
missing months.

## Basins

The basin mask is `HydroShed+Mascon_Basins_L3.nc`, SHA-256
`b0434196b7615366626b4bd88ce1f450c63c79e1ebe0b866fea3a05aebaf4a24`. The JPL table has 284
mask basins: 228 kept for modeling, 46 ice sheets, 4 water bodies and 6 without valid
JPL observations.

## Processed inputs

The table below lists SHA-256 checksums of the processed JPL inputs in
`data/processed/jpl/`. The runs wrote these inputs and the result files with the
mask's basin names. On 2026-11-15, we replaced those names with the labels B001
to B284.

The checksums below and in `SHA256_MANIFEST_LIVE.csv` describe the relabeled
files. Except for the basin labels, those files match the files recorded on
2026-10-14 byte for byte.

| File | SHA-256 |
|---|---|
| `basin_meta.csv` | `781851021e196582717b720159b14d6148f3fc3541ccdb3a52c17b68a495dfc0` |
| `basin_month_twsa_global.csv` | `d7b8feb69a73506040c3e0107dd62e4f5e55f187376f50ff953185b393c0a293` |
| `li2026_basin_coverage.csv` | `f80a533f35afe8b1e222e66e01b59fd8608e030d10cf6c516cb4315473c24898` |
| `li2026_jpl_basin_forecasts.csv` | `2645bc0cb9bfbef3f4b2632dd29187bcd085d485c4f3e8ad554b5b254e7540eb` |

The JPL baseline ladder and GRACE-FCast comparison populations use these
inputs. A rebuild reproduces `phase2_baseline_summary.csv` and
`phase6_li_comparison_summary.csv` to rounding error.

## GRACE-FCast comparison

The forecasts come from Li and Kusche's JPL-FCast, the JPL member of GRACE-FCast
(PANGAEA dataset `10.1594/PANGAEA.973113`). The input contains 173 monthly NetCDF
initialization files in `data/raw/li2026/JPL-FCast/global_gridded/`. The files
span 2009-12 to 2024-04 on 1-degree global land cells.

Li and Kusche trained JPL-FCast against JPL RL06.1_v03 (April 2002 to April
2024). Our target is JPL RL06.3Mv04 CRI, so the comparison crosses product
releases.

The pipeline expresses their interannual plus subseasonal forecast
(`li_lstm_nonseas`) in standardized, deseasonalized target space for each fold.
Before that transformation, `li_lstm_full` adds their published seasonal and
linear terms.

Each comparison table reports two populations. Within each population, the
pipeline scores every model on the same
`(basin, issue_date, target_date, horizon)` rows:

- The `all_matched` population contains every basin and date row available to
  all compared models. It has 227 basins, 13,393 rows per horizon, and 59 issue
  months.
- The `joint_full_cells` population contains basins that fully contain native
  JPL and GRACE-FCast cells. It has 67 basins, 3,953 rows per horizon, and 59
  issue months.

For `joint_full_cells`, each basin must contain both of these cell sets:

- Every 0.25-degree mask subcell of at least one native JPL `mascon_ID`
- All sixteen 0.25-degree subcells of at least one finite 1-degree GRACE-FCast cell.

The rule tests full containment rather than an area threshold or coverage
fraction.

The paper reports `joint_full_cells`. The headline and summary files keep both
populations so the effect of the restriction is visible.

## Seeds and resampling

- Moving-block bootstrap confidence intervals: 2,000 resamples, seed 0, block length
  max(3, h) months at lead h.
- LSTM models: seeds 0 and 1.
- Stacked LSTM and residual models: seeds 0 and 1.
- Residual MLP experiments: seeds 0, 1 and 2.
- Random-graph placebos: 50 graphs in the linear neighbor tests (`placebo_n` in
  `phase3b_summary.csv`). The ERA5-Land, nonlinear, and neural experiments use
  20 draws per fold and horizon. The experiment modules define the seeds.
- IAAFT surrogate control: draws 0 to 98 (99 in total).
- Basin random-forest analysis and permutation importance: seed 0.

## Checks and conventions

`SHA256_MANIFEST_LIVE.csv` lists the byte count and SHA-256 digest of every
generated CSV and serialized model-state file in this directory. The checksums
for tables in git use the code archive's LF line endings.

To check the files that git excludes, run
`GRACEFC_SOURCE=jpl python scripts/make_manifest.py --check`. Git versions the
other files.

Positive `skill` means the first named model has lower MSE than its `vs` model:
`skill = 1 - MSE(model) / MSE(vs)`.

Before you interpret a value as a percentage improvement, check the `model` and
`vs` columns.

Git excludes raw NetCDF inputs and processed row-level data.
