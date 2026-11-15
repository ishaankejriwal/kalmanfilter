# Archive manifest

This file lists the source files and columns for each table, figure, and
in-text number in `paper/main.tex`. Table and figure numbers follow the
manuscript. Table A1 maps model names such as KF, KF-R1, KF-R12, and KF-R12E to
their identifiers in the result files.

## Conventions

Skill is 1 - MSE(first)/MSE(second). A positive value means that the first-named
model (the `model` or `challenger` column) has the lower error. Columns named
`skill` or `skill_vs_*` hold fractions. Columns with the suffix `_pct` hold
percentages. The paper prints percentages with our model first.

`results/phase6_li_comparison_headline.csv` holds each pair in both orders.
`results/jpl/phase6_li_comparison_headline.csv` stores GRACE-FCast first. To put
our model first, convert a stored skill s to 1 - 1/(1 - s). The conversion
leaves the DM p value unchanged.

The pipeline computes `rmse_std` and related skill scores from standardized
residuals. Before it pools errors, it divides each basin's residuals by the
residual standard deviation from the fold's training window.

`rmse_cm`, `pooled_rmse_cm`, and the other `_cm` columns use cm of equivalent
water height.
`horizon` gives the lead time in months.

Table 2, Table B1, Table B2, and Fig. 2a use the stronger damped-persistence
variant at each lead time. The `damped_ref` column of
`paper_baseline_ladder.csv` identifies that reference:

| Product | ρ^h variant (`damped_persistence_rho`) | Regression variant (`damped_persistence_reg`) |
|---|---|---|
| CSR | h = 1 | h = 2 to 6 |
| JPL | h = 1 and 2 | h = 3 to 6 |

Table 5 and Sect. 4.4 use the ρ^h variant at every lead time, and Fig. 4a uses the
regression variant at every lead time. The `damped_persistence` rows of the
conventional-metric files follow the CSR mapping on both products.

The data archive contains files with the suffix `_predictions.csv` and all
files under `data/processed/`. Git excludes those files for size.
`results/SHA256_MANIFEST_LIVE.csv` and `results/jpl/SHA256_MANIFEST_LIVE.csv`
hold the checksums for the result files among them. The code archive contains
all other files listed here.

The archived JPL run used commit 71be5ec. The
[JPL run record](../results/jpl/RUN_PROVENANCE.md) describes the tables in
`results/jpl/`.

## Tables

| Item | Source file and columns |
|---|---|
| Table 1 (forecast names) | No result file. Sect. 3 defines the forecasts. |
| Table 2 (benchmark skill, CSR) | `results/paper_baseline_ladder.csv`: `skill_vs_damped`, reference in `damped_ref` |
| Table 3 (own-basin models against KF) | KF-R1: `results/flat12_ridge_summary.csv`, `kalman_own_ridge` rows, `skill_vs_kalman` and `dm_p_vs_kalman`. KF-R12 and KF-R12E: `results/paper_baseline_contrasts.csv`, challengers `ridge_own_flat12` and `ridge_own_era5_flat12` against `kalman_ar1`, `skill` and `dm_p` |
| Table 4 (nonlinear models, h = 1 to 3) | `rmse_std` in `results/phase7_lstm_summary.csv` (`kalman_ar1`, `ridge_own_era5`, `ridge_own_flat12`, `ridge_own_era5_flat12`, `lstm_own_era5_s0`/`_s1`, `mlp_own_era5_flat12_s0`/`_s1`) and `results/phase7_resmlp_summary.csv` (`resmlp_own_era5_s0`/`_s1`/`_s2`) |
| Table 5, CSR rows | `results/phase6_li_comparison_headline.csv`, subset `joint_full_cells`: `kalman_ar1`, `ridge_own_era5_flat12` and `damped_persistence_rho` against `li_lstm_full` and `li_lstm_nonseas`, `skill` and `dm_p`. Basin counts: `results/phase6_li_comparison_perbasin.csv`, `li_lstm_full` against `kalman_ar1` and `ridge_own_era5_flat12`, number of basins with `a_better` true (GRACE-FCast better) at h = 1 and 6 |
| Table 5, JPL rows | `results/jpl/phase6_li_comparison_headline.csv`, subset `joint_full_cells`: `li_lstm_full` and `li_lstm_nonseas` against `kalman_ar1` and `damped_persistence_rho`, `skill` converted as above and `dm_p` |
| Table A1 (identifiers) | None |
| Table B1 (CSR, full) | `results/paper_baseline_ladder.csv`: `rmse_std`, `dm_p_vs_damped` |
| Table B2 (JPL benchmarks) | `results/jpl/paper_baseline_ladder.csv`: `skill_vs_damped`, `dm_p_vs_damped`, reference in `damped_ref` |
| Table C1 (conventional metrics) | `results/conventional_metrics_summary.csv`: `pooled_rmse_cm`, `rmse_cm_med`, `cc_anom_med`, `cc_full_med`, `nse_anom_med`, `nse_full_med` for `damped_persistence`, `kalman_ar1`, `kalman_own_ridge`, `ridge_own_flat12`, `ridge_own_era5_flat12`. The paper excludes the `stacked_ens` rows from extended runs. |

## Figures

`scripts/make_figures.py` writes each figure to `figures/fig0N_*.pdf` and `.png`,
where N is the figure number. The script stops if a headline value differs
from its source file.

| Item | Source file and columns |
|---|---|
| Fig. 1 (basin sample and comparison sets) | Metadata: `data/processed/basin_meta.csv`. Coverage: `data/processed/li2026_basin_coverage.csv` (`li_coverage`, `n_full_li_cells`, `n_full_native_mascons`). Basin lists and counts: `results/phase6_li_comparison_perbasin.csv`, `results/phase6_li_comparison_summary.csv`, and their copies in `results/jpl/`. |
| Fig. 2a (benchmark skill) | Skill: `results/paper_baseline_ladder.csv` (`skill_vs_damped`, `damped_ref`). Intervals: `results/paper_baseline_contrasts.csv` (`ci_lo`, `ci_hi` against the stronger variant). The contrast file has rows for `ridge_own_era5_flat12`, `kalman_ar1`, `ridge_own_flat12`, `kalman_own_ridge`, and `ridge_own_perbasin` only. |
| Fig. 2b (pooled RMSE in cm) | `results/conventional_metrics_summary.csv`: `pooled_rmse_cm` for the five Table C1 forecasts |
| Fig. 3 (example series, h = 1, cm) | Damped persistence: `results/phase2_baseline_predictions.csv` (`damped_persistence_rho`, `target` and `pred` in cm, `target_std_units`). KF: `results/kalman_predictions.csv` (`kalman_ar1`, standardized). The script converts KF to cm with the fold's training standard deviation, `target / target_std_units`. It checks panel RMSEs against `rmse_cm` in `results/conventional_metrics_perbasin.csv`. |
| Fig. 4a (zero-r variant) | `results/r0_ablation_summary.csv`: `skill_pct` of components `full_margin` (KF) and `rho_estimation_term` (zero-r variant). The annotation uses `noise_filtering_term`. |
| Fig. 4b (two-variance variant) | `results/kalman_mission_summary.csv`: component `mission_split_term`, `skill_pct`, `ci_lo_pct`, `ci_hi_pct` |
| Fig. 4c (per-basin KF skill map) | `results/conventional_metrics_perbasin.csv`: `rmse_cm` of `kalman_ar1` and `damped_persistence` at h = 1 |
| Fig. 5 (where the ERA5-Land window helps) | `results/flat12_ridge_predictions.csv`: 1-month MSE for each basin for `ridge_own_era5_flat12` and `kalman_ar1`. Per-basin DM tests use Benjamini-Hochberg q = 0.10. The script recomputes each basin's residual standard deviation over the training window from `data/processed/basin_month_twsa_global.csv`, then takes the median over folds. |
| Fig. 6a (nonlinear models against KF) | Scores: `results/phase7_lstm_summary.csv` (`rmse_std`). Seed ensemble and bootstrap intervals: `results/phase7_lstm_predictions.csv`. The script checks these against `results/paper_baseline_contrasts.csv`. |
| Fig. 6b (KF-R12E refit on LSTM rows) | `results/flat12_train85_sensitivity.csv`: `ridge_own_era5_flat12_train85` against `lstm_own_era5_ens`, `skill_pct` and `dm_p` |
| Fig. 7a (CSR, against GRACE-FCast) | `results/phase6_li_comparison_headline.csv`, subset `joint_full_cells`, ours first: `skill`, `ci_lo`, `ci_hi`, `dm_p` |
| Fig. 7b (JPL, against GRACE-FCast) | `results/jpl/phase6_li_comparison_headline.csv`, subset `joint_full_cells`, with the conversion above. The script checks the conversion against `results/jpl/phase6_li_comparison_summary.csv` (`rmse_std`). |

## Numbers in the text

| Item | Source file and columns |
|---|---|
| Abstract | `results/paper_baseline_ladder.csv`, `results/jpl/paper_baseline_ladder.csv`, `results/r0_ablation_summary.csv`, `results/paper_baseline_contrasts.csv`, `results/centimeter_contrasts.csv` and the two `phase6_li_comparison_headline.csv` files, as in the rows below |
| Sect. 3.1, climatology drift | `results/climatology_offset.csv` (`rmse`, `offset_share`), from `scripts/climatology_offset.py` |
| Sect. 3.2, sample sizes | `n` in `results/paper_baseline_ladder.csv` and `results/jpl/paper_baseline_ladder.csv` |
| Sect. 3.4, boundary fits | `results/kalman_mission_summary.csv`, `diagnostic` rows (`stat_name`, `stat_value`) |
| Sect. 3.6, comparison basin sets | Coverage: `data/processed/li2026_basin_coverage.csv`. Counts and scores: `n_basins` and `rmse_std` by subset in `results/phase6_li_comparison_summary.csv` and `results/jpl/phase6_li_comparison_summary.csv`. Issue months: `n_months` in the two headline files. |
| Sect. 4.1, KF against the benchmarks | `results/paper_baseline_ladder.csv` (`skill_vs_damped`, `dm_p_vs_damped`) and `results/paper_baseline_contrasts.csv` (`kalman_ar1` against `ridge_own_perbasin` and `ridge_own_lags`) |
| Sect. 4.1, JPL | `results/jpl/paper_baseline_ladder.csv`, `results/jpl/paper_baseline_contrasts.csv` |
| Sect. 4.1, per-basin gain correlates | `results/kalman_gain_correlates.csv` (`spearman_rho`, `p`, and median skill in the driest quarter and the other basins), from `scripts/kalman_gain_correlates.py` |
| Sect. 4.2, 1-month decomposition | `results/r0_ablation_summary.csv` (`rmse_a`, `skill_pct`, `dm_p`) and `rmse_std` of `damped_persistence_rho` at h = 1 in `results/paper_baseline_ladder.csv` |
| Sect. 4.2, two-variance variant | `results/kalman_mission_summary.csv`: `mission_split_term` rows and the per-basin `diagnostic` rows |
| Sect. 4.3, own-basin corrections | `results/flat12_ridge_summary.csv` (`skill_vs_kalman`, `skill_vs_ridge_own`, `dm_p_vs_kalman`), `results/paper_baseline_contrasts.csv`, and `results/paper_baseline_ladder.csv` |
| Sect. 4.3, nonlinear models | `results/phase7_lstm_summary.csv` (`dm_vs_ridge_twin`, `dm_p`) and `results/flat12_train85_sensitivity.csv` |
| Sect. 4.4, comparison with GRACE-FCast | Same sources as Table 5. The damped-persistence check uses the `damped_persistence_rho` rows of both headline files. It also uses `kalman_ar1` against `damped_persistence_rho` at h = 1 in `results/jpl/paper_baseline_contrasts.csv`. |
| Sect. 4.5, basin weighting | `results/conventional_metrics_summary.csv`. Tests in cm: `results/centimeter_contrasts.csv` (`skill`, `dm_p`), from `scripts/centimeter_contrasts.py`. |
| Sect. 4.6, neighboring basins | `results/phase3b_summary.csv` (`skill_vs_own_ridge`, `placebo_beaten`) and `results/phase4_surrogate_summary.csv` (`beats_n_of`), with the same files in `results/jpl/` |
| Sect. 5, Discussion | `results/conventional_metrics_summary.csv` (`pooled_rmse_cm`, `rmse_cm_med`) and `results/phase6_li_comparison_headline.csv` |
