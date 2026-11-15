# JPL run record

This file records how the JPL results in this directory were produced. Git versions the
summary and diagnostic tables. It ignores the row-level predictions, placebo draws, model
state and chain logs, which can be regenerated and make up nearly all of the output size.
The predictions, placebo draws and model state are in the data archive of the Zenodo
deposit. `SHA256_MANIFEST_LIVE.csv` identifies the generated files behind the shared
tables.

## Run

- Pipeline: the JPL mascon experiment chain (`--source jpl`), kept separate from the CSR
  outputs.
- Code revision: `71be5ec6af30e9d8f3c72549ca114c3b47071380` ("compare JPL results with
  Li"). The GRACE-FCast comparison was run from the working tree committed as this
  revision.
- Main suite: 2026-09-05 15:36 to 2026-09-06 01:21, America/Chicago workstation time.
- JPL basin table and GRACE-FCast comparison rerun: 2026-09-06 12:30 to 12:34,
  America/Chicago workstation time.
- Evaluation: five frozen-origin folds beginning 2019-06, 2020-11, 2022-04, 2023-09 and
  2025-02. The GRACE-FCast comparison has 59 issue months and leads 1 to 6.

## GRACE/GRACE-FO target

- File: `data/GRCTellus.JPL.200204_202606.GLO.RL06.3M.MSCNv04CRI.nc`
- Product: JPL GRACE and GRACE-FO Mascon RL06.3Mv04 CRI (source `GRACE and GRACE-FO JPL
  RL06.3Mv04-CRI`, product version `v3.0`), DOI `10.5067/TEMSC-3JC634`.
- File created 2026-08-19 10:08:27 UTC; time coverage 2002-04-16 to 2026-06-16.
- Grid: sampled at 0.5 degrees. The native resolution is about 3-degree equal-area
  mascons.
- SHA-256: `d5a6737bd0406ef4e9ea72c825ea95c6693a15faf2027e52be491efa8cf89bbd`

JPL has already applied the Coastline Resolution Improvement filter in the CRI product.
The pipeline applied the NetCDF `scale_factor` field (the run did not use
`--no-scale-factors`), and every row of `data/processed/jpl/basin_meta.csv` records
`scale_factors_applied=True`. The target reader uses JPL's official missing-month
metadata.

## Basins

The basin mask is `HydroShed+Mascon_Basins_L3.nc`, SHA-256
`b0434196b7615366626b4bd88ce1f450c63c79e1ebe0b866fea3a05aebaf4a24`. The JPL table has 284
mask basins: 228 kept for modeling, 46 ice sheets, 4 water bodies and 6 without valid
JPL observations.

## Processed inputs

SHA-256 of the processed JPL inputs in `data/processed/jpl/`. The runs wrote these files,
and the result files, with the mask's basin names. On 2026-11-15 the names were replaced
by the labels B001 to B284. The checksums below and in `SHA256_MANIFEST_LIVE.csv` are for
the relabelled files, which otherwise match the files recorded on 2026-10-14 byte for
byte.

| File | SHA-256 |
|---|---|
| `basin_meta.csv` | `781851021e196582717b720159b14d6148f3fc3541ccdb3a52c17b68a495dfc0` |
| `basin_month_twsa_global.csv` | `d7b8feb69a73506040c3e0107dd62e4f5e55f187376f50ff953185b393c0a293` |
| `li2026_basin_coverage.csv` | `f80a533f35afe8b1e222e66e01b59fd8608e030d10cf6c516cb4315473c24898` |
| `li2026_jpl_basin_forecasts.csv` | `2645bc0cb9bfbef3f4b2632dd29187bcd085d485c4f3e8ad554b5b254e7540eb` |

Rebuilt from these files, the JPL baseline ladder and the GRACE-FCast comparison
populations reproduce `phase2_baseline_summary.csv` and `phase6_li_comparison_summary.csv`
to rounding error.

## GRACE-FCast comparison

The forecasts are Li and Kusche's JPL-FCast, the JPL member of GRACE-FCast, PANGAEA dataset
`10.1594/PANGAEA.973113`: 173 monthly NetCDF initialization files in
`data/raw/li2026/JPL-FCast/global_gridded/`, from 2009-12 to 2024-04, on 1-degree global
land cells. Li and Kusche trained it against JPL RL06.1_v03 (April 2002 to April 2024),
while our target is JPL RL06.3Mv04 CRI, so the comparison crosses product releases.

`li_lstm_nonseas` is their interannual plus subseasonal forecast, transformed into the
pipeline's fold-specific standardized, deseasonalized target space. `li_lstm_full` adds
their published seasonal and linear terms before the same transformation.

Each comparison table reports two populations, and within each population every model is
scored on the same `(basin, issue_date, target_date, horizon)` rows.

- `all_matched`: every basin and date row available to all compared models; 227 basins,
  13,393 rows per horizon and 59 issue months.
- `joint_full_cells`: a basin must contain every 0.25-degree mask subcell of at least one
  native JPL `mascon_ID`, and all sixteen 0.25-degree subcells of at least one finite
  1-degree GRACE-FCast cell. This is full containment, not an area threshold or a
  coverage fraction. It keeps 67 basins, 3,953 rows per horizon and 59 issue months.

The paper reports `joint_full_cells`. The headline and summary files keep both
populations so the effect of the restriction is visible.

## Seeds and resampling

- Moving-block bootstrap confidence intervals: 2,000 resamples, seed 0, block length
  max(3, h) months at lead h.
- LSTM models: seeds 0 and 1.
- Stacked LSTM and residual models: seeds 0 and 1.
- Residual MLP experiments: seeds 0, 1 and 2.
- Random-graph placebos: 50 graphs in the linear neighbor tests (`placebo_n` in
  `phase3b_summary.csv`) and 20 draws per fold and horizon in the ERA5-Land, nonlinear and
  neural experiments, with seeds set in the experiment modules.
- IAAFT surrogate control: draws 0 to 98 (99 in total).
- Basin random-forest analysis and permutation importance: seed 0.

## Checks and conventions

`SHA256_MANIFEST_LIVE.csv` lists the byte count and SHA-256 digest of every generated CSV
and serialized model-state file in this directory. The tables stored in git are hashed as
they are in the code archive, with LF line endings.
`GRACEFC_SOURCE=jpl python scripts/make_manifest.py --check` verifies the files git does
not store; git versions the rest.

Positive `skill` means the first named model has lower MSE than its `vs` model:
`skill = 1 - MSE(model) / MSE(vs)`. Check the `model` and `vs` columns before reading a
value as a percentage improvement.

Raw NetCDF inputs and processed row-level data are not stored in git.
