# Robustness report (Paper 2)

Families (Stage 20, frozen seeds; matrix: `07_ROBUSTNESS/ROBUSTNESS_MATRIX.csv`):

- **R1 estimator ladder** (24 rows): linear-OLS and df=3 spline vs the
  primary df=4 spline, and 20-bin quantile proxy. Bridge and participation
  associations keep sign across all estimators; magnitudes vary
  (bridge +0.435..+0.524; participation -0.115..-0.346), consistent with the
  pre-registered coupling-risk flag for path-length metrics.
- **R2 extreme-threshold sensitivity** (2 rows): median standardized
  residual +3.70 (top-1%) and +1.68 (top-5%) - monotone with threshold, as
  expected for an upper-tail effect.
- **R5 winsorized residual** (8 rows): all headline associations
  unchanged at the 99.9th-percentile winsorization (e.g. bridge +0.4985
  identical to primary) - not outlier-driven.

Additional arms:

- **Negative controls (Stage 21):** NC1 (label permutation) and NC2
  (residual permutation) bands are ~|rho| <= 0.004 for every feature;
  observed associations exceed both bands with large margins.
- **Degree-preserving null (Stage 15):** under exact degree-sequence-
  preserving rewiring (12 subjects x 100 nulls, per-null full CIS +
  feature recomputation), the null distributions of |rho(R, feature)| are
  WIDE (p95 up to 0.73 for clustering) and every observed association falls
  INSIDE its null band - the pre-registered Outcome C. This qualifies all
  Stage-8 associations: they describe the real graphs' structure but do not
  survive as degree-independent mechanisms under the frozen null.
- **Subject-aware model (Stage 11):** within-subject estimates with CR1
  cluster-robust SEs, q < 1e-7 for all 8 features - inference is not driven
  by between-subject variation.
- **Configuration selection discipline:** all configurations were frozen
  BEFORE unblinding (CONFIG_FREEZE + amendments 1-3); none was selected
  post hoc by result strength.

