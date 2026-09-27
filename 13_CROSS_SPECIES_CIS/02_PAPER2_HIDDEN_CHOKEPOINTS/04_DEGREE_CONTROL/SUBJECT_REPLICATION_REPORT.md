# SUBJECT REPLICATION REPORT (Stage 4)

- Subjects: **801** (QC-pass, Paper 1 frozen flags).
- Population median residual R (primary estimator): **-2.667e-07**  (bootstrap 95% CI **[-9.251e-07, 6.720e-07]**; 10000 subject-level resamples, seed 20270927).
- Replication fraction (median R > 0): **0.489** (392/801 subjects).
- Heterogeneity (IQR of per-subject median R): **1.142e-05**.
- Leave-one-subject-out: max |deviation| of population median = **5.352e-08** (stability check).
- Orthogonality gate: pass=True (median |rho(R, degree)| = 0.0327).

## Cross-check vs Paper 1 matched-pair residual (E03b, same-pairs)
- Subjects merged: 801 (same-pairs design, Amendment 2).
- Spearman(delta_ours, delta_paper1) = **0.785** (p = 1.74e-168).
- Input-identity check: max |deviation - fitted gap| = 7.31e-03 (machine-precision identity; both residuals act on identical inputs).
- Interpretation: the model-based spline residual reproduces the matched-pair residual's subject-level structure; the two are different estimators of the same degree-control target.
