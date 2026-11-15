# Result files

The pipeline scripts (`scripts/run_chain.py` and the scripts it calls) write
CSR results to this directory and JPL results to `jpl/`. The
[archive manifest](../docs/ARCHIVE_MANIFEST.md) identifies the source file and
column for each table, figure, and quoted number in the paper.

The files behind the main results:

| File | Contents |
|---|---|
| `paper_baseline_ladder.csv` | Benchmark forecasts, KF, KF-R1, KF-R12, and KF-R12E at leads 1 to 6 on matched rows (Table 2, Appendix B). Skill uses the stronger damped-persistence variant at each lead. |
| `paper_baseline_contrasts.csv` | Pairwise contrasts behind the ladder: skill, bootstrap interval, DM statistic and p value |
| `flat12_ridge_summary.csv` | KF-R1, KF-R12 and KF-R12E against KF and against the own-basin ridge (Table 3) |
| `r0_ablation_summary.csv`, `kalman_mission_summary.csv` | Zero-r and two-variance KF variants (Fig. 4). `kalman_mission_summary.csv` also holds the fit diagnostics. |
| `phase6_li_comparison_headline.csv` | KF, KF-R1, KF-R12, KF-R12E, damped persistence, and the per-basin lag ridge against GRACE-FCast full and non-seasonal forecasts (Table 5). Both orientations use the `all_matched`, `coverage_ge_0.5`, and `joint_full_cells` subsets. |
| `conventional_metrics_summary.csv` | RMSE in cm, correlation, and NSE for damped persistence, KF, KF-R1, KF-R12, and KF-R12E (Appendix C). Extended stacked-model predictions supply the `stacked_ens` rows when those files exist. |
| `phase7_lstm_summary.csv`, `phase7_resmlp_summary.csv` | Nonlinear models (Table 4, Fig. 6) |
| `jpl/` | JPL tables, mainly `jpl/paper_baseline_ladder.csv` and `jpl/phase6_li_comparison_headline.csv`. The [JPL run record](jpl/RUN_PROVENANCE.md) describes their provenance. |

## Naming conventions

File names identify the type of output:

| Pattern | Contents |
|---|---|
| `*_summary.csv` | Scores for each model and lead |
| `*_headline.csv` | Rows that the paper quotes |
| `*_predictions.csv` | One row per model, basin, issue month, and lead |
| `*_placebo_*.csv` | Null draws for the neighbor and surrogate tests |
| `chain_<step>.log` | Console output from one chain step. The archives exclude these logs. |

The `phaseN_` prefixes identify experiment stages in their original run order:

| Stage | Experiments |
|---|---|
| 2 | Benchmark forecasts |
| 3b and 4 | Neighbor and surrogate tests |
| 5 | In-filter and nonlinear neighbor variants |
| 6 | GRACE-FCast comparison and ERA5-Land models |
| 7 and 8 | Neural models |

## Score conventions

Skill is 1 - MSE(model)/MSE(vs). A positive value means that the model in the
`model` column has the lower error. Unless the column name specifies cm, errors
use standardized units.

## Archived files and checksums

The Zenodo data archive contains the large files that git excludes:

| Directory | Files |
|---|---|
| `results/` | `*_predictions.csv`, `*_placebo_basin.csv`, and `phase3b_placebo_monthly.csv` |
| `results/jpl/` | Predictions, all placebo tables, and `kalman_fold_params.pkl` |

`SHA256_MANIFEST_LIVE.csv` in each result directory records file sizes and
SHA-256 checksums. Run these commands from the repository root:

1. Check the CSR files:

   ```bash
   python scripts/make_manifest.py --check
   ```

2. Check the JPL files:

   ```bash
   GRACEFC_SOURCE=jpl python scripts/make_manifest.py --check
   ```

`kalman_fold_params.pkl` caches the fitted KF parameters per fold. The `flat12_ridge` and `phase3b`
steps rewrite it when it is missing or out of date.
