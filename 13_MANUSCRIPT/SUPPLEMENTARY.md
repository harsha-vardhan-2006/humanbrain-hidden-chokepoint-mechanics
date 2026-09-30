# Supplementary material (Paper 2)

Companion to `MANUSCRIPT.md`. All artifacts referenced here live in this
study tree; all gates verified by `13_MANUSCRIPT/verify_stage24.py` (12/12
PASS, 2026-09-30).

## S1. Frozen configuration lineage

- `01_CONFIG/CONFIG_FREEZE.md` — pre-registration (2026-09-27) +
  append-only Amendments 1–3 (log10-transform retirement; same-pairs
  cross-check redefinition; Stage-6 redundancy repair). No gate was changed
  after seeing a passing result.
- `00_DOCS/RESEARCH_QUESTION.md`, `00_DOCS/MATHEMATICAL_FRAMEWORK.md` —
  frozen question/hypotheses and estimator definitions.
- `00_DOCS/RESEARCH_LOG.md` — append-only log, entries P2-00, P2-01.

## S2. Freeze-1 validation block (Stages 3–5)

- Orthogonality: median |ρ(R, degree)| = 0.0327 (gate < 0.05; 801 subjects).
- Same-pairs cross-check vs Paper 1 E03b: ρ = 0.785 (p = 1.7e-168);
  input identity exact to 8.7e-19.
- Replication: δ = 0.1040, 801/801 positive, CI [0.1007, 0.1073];
  LOSO max deviation 5.4e-8.
- Artifacts: `04_DEGREE_CONTROL/`, `00_DOCS/FREEZE_1_REPORT.md`.

## S3. Feature matrix QC (Stage 6–7)

801 subjects × 456 nodes × 12 features = 365,256 rows; 0 non-finite;
Amendment-3 redundancy repair verified (max |redundancy − clustering| > 0).
Artifacts: `03_FEATURE_EXTRACTION/NODE_FEATURE_MATRIX.parquet`,
`05_MECHANISM_ANALYSIS/feature_qc_report.md`.

## S4. Full association tables

- Univariate (12 features): `05_MECHANISM_ANALYSIS/UNIVARIATE_RESULTS.json`,
  `10_TABLES/table_p2_univariate_associations.csv`.
- Feature correlations + VIF: `10_TABLES/table_p2_feature_correlations.csv`,
  `10_TABLES/VIF_REPORT.csv` (pruning rule |ρ| ≥ 0.9).
- Nested models: `10_TABLES/table_p2_nested_models.csv` (M4 Δcv-R² = +0.294).
- Subject-aware CR1: `10_TABLES/table_p2_subject_aware_model.csv`.
- ML benchmark: `08_STATISTICS/ML_BENCHMARK.json`,
  `10_TABLES/table_p2_ml_benchmark.csv`.

## S5. Negative controls (Stage 21)

`07_ROBUSTNESS/NEGATIVE_CONTROLS.json`: NC1 (label permutation) and NC2
(residual permutation) p95 bands ≤ 0.0044 for every feature; observed
exceeds both with margins ≥ 0.129. Vectorized rank-permutation with exact
Spearman equivalence asserted per feature (max deviation ≤ 1.7e-16).

## S6. Degree-preserving null ensemble (Stage 15)

Design: 12 stratified subjects (seed 20270927) × 100 Maslov–Sneppen nulls
each (10× edge-count swap attempts); exact per-node degree verification +
edge-match + zero self-loops required per null (fail-loud); per-null exact
CIS + 9-feature recomputation; null residualization via 20-bin quantile
median (documented proxy of the df=4 spline). Verdict table:
`06_NULL_MODELS/NULL_FEATURE_RESULTS.json`,
`10_TABLES/table_p2_null_features.csv`. Raw per-null records:
`06_NULL_MODELS/null_records_checkpoint.jsonl` (1,200 records).

## S7. Robustness matrix (Stage 20)

`07_ROBUSTNESS/ROBUSTNESS_MATRIX.csv`: R1 estimator ladder (24 rows),
R2 extreme-threshold (2 rows), R5 winsorized (8 rows). See
`00_DOCS/ROBUSTNESS_REPORT.md` for reading.

## S8. Biological annotation + enrichment

- `data/node_atlas_mapping.csv`, 
  `results_annotation/human_node_biological_annotations.csv`
  (456 rows; evidence-leveled; cell-type fields NOT_AVAILABLE).
- `results_annotation/human_cis_biological_master.csv` (CIS + residual +
  annotation per node, Stouffer z, BH q).
- `results_annotation/BIOLOGICAL_ENRICHMENT.json` (10k permutations;
  cortex under-representation q = 0.00017; cell-type rows NOT_ESTABLISHED).
- Sources + limitations: `00_DOCS/BIOLOGICAL_ANNOTATION_SOURCES.md`.

## S9. Fly case study (Stages 12–13)

`11_CASE_STUDIES/fly_target_features.parquet` (3,518 targets × features),
`ME131_MECHANISTIC_PROFILE.csv`, `ME131_CASE_STUDY.md`. Frozen fly CIS
consumed read-only; sampled directed betweenness (k = 512 pivots, frozen
seed) computed fresh for the descriptive profile only.

## S10. Synthesis

`12_SYNTHESIS/CHOKEPOINT_DEFINITION.md`, `CHOKEPOINT_SENSITIVITY.csv`,
`CHOKEPOINT_CANDIDATES.csv` (per-node criteria flags; node-level null
column uniformly NOT_ESTABLISHED), `HUMAN_VS_FLY_COMPARISON.{csv,md}`
(12 properties; fly z = 1.21, p = 0.109 negative preserved).

## S11. Stage-24 verification log

`14_LOGS/stage24_verification.log` — V01–V12, 12/12 PASS (2026-09-30).
