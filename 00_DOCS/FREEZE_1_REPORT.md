# FREEZE 1 REPORT — CIS + Degree Residualization Validated (Paper 2)

Date: 2026-09-27. Status: **FREEZE 1 ACHIEVED** (all gates PASS).
Checkpoint: no Stage 6+ work has started; feature extraction awaits review.

## What was built (Stages 0–5)

- Frozen config: `01_CONFIG/CONFIG_FREEZE.md` (+ Amendments 1–2),
  `01_CONFIG/config.json` (machine-readable, path-verified).
- Frozen docs: `00_DOCS/RESEARCH_QUESTION.md` (H1–H7, falsification rules),
  `00_DOCS/MATHEMATICAL_FRAMEWORK.md` (CIS, residual, estimator ladder,
  gates, null plan), `00_DOCS/REPOSITORY_AUDIT.md` (Stage 0, verified paths).
- Code: `01_CONFIG/freeze_config.py`,
  `04_DEGREE_CONTROL/{compute_residuals,crosscheck_same_pairs,
  validate_subjects,extract_extremes}.py`, `15_TESTS/test_stage3_residuals.py`
  (7 tests, all PASS).
- Data consumed: Paper 1 frozen per-subject exact CIS (801 QC-pass × 456
  nodes), frozen QC flags, frozen E03b matched-pair tables. Raw datasets
  untouched.

## Primary result (Stage 3, estimator M1_spline4_raw per Amendment 2)

- Orthogonality gate **PASS**: median |Spearman(R, degree)| = **0.0327**
  (mean 0.0382; 95th pct 0.0954) — an order of magnitude below the Paper 1
  CIS–degree ρ = 0.943 and below the frozen 0.05 threshold.
- Linear-estimator contrast: median |ρ| = 0.396 — the spline captures real
  nonlinearity in E[CIS | degree]; residualization is doing measurable work.
- Outputs: `continuous_residuals.{parquet,csv.gz}` (365,256 rows),
  `subject_residual_summary.csv`, `orthogonality_by_subject.csv`,
  `gate_report.json`, figures `degree_vs_CIS / degree_vs_residual /
  residual_distribution.png`.

## Cross-validation (Stage 4) + same-pairs cross-check (Stage 3b)

- Same-pairs cross-check vs Paper 1 E03b **PASS**:
  Spearman(δ_ours, δ_paper1) = **0.785** (p = 1.7e-168, n = 801);
  median δ_ours = **0.1040** vs frozen 0.100 (bias ≈ +0.004, estimator
  difference only).
- Input-identity proven exactly: [R(node) − R(control)] − frozen pair
  residual = fitted(node) − fitted(control) to **8.7e-19** across all
  36,846 pair rows — both residuals act on identical inputs; only the
  baseline (spline fit vs matched control) differs. Mean |deviation|
  1.04e-4; the 888 pairs with deviation > 1e-3 are predominantly
  nearest-50 fallback matches with large degree gaps, as expected.
- Subject replication (proper statistic, δ_ours > 0): **801/801 (100%)**,
  median δ_ours 0.1040, subject-bootstrap 95% CI [0.1007, 0.1073]
  (10,000 resamples, seed 20270927) — reproduces Paper 1's 778/801 with
  δ = 0.100.
- LOSO stability: population median all-node residual shifts ≤ 5.4e-8
  under leave-one-subject-out.
- Retired statistic (documented, not deleted): all-node
  `median_R > 0` fraction (0.489) is meaningless as a replication measure —
  the residual effect lives in the CIS upper tail, which the matched-pair
  design samples by construction.

## Extreme-node extraction (Stage 5, pre-registered thresholds)

- top1%: 4,005 rows; top5%: 18,429; bottom1%: 4,007; bottom5%: 18,427
  (n_subject_node = 365,256). Files: `positive_extreme_nodes.csv`,
  `negative_extreme_nodes.csv`, `extremes_manifest.json`.
- System labels joined for QC only; **no identity inspection performed**
  (that is Stage 6+, post-Freeze-1 review).

## Discipline notes (all pre-unblinding)

- Two estimator amendments (asinh → raw-spline; log retired) and one
  cross-check redefinition (same-pairs) were made **before any downstream
  statistic was consumed**, each documented append-only in
  CONFIG_FREEZE.md with rationale. No threshold was tuned to a result; the
  gates were fixed in the initial freeze and then passed.
- Known residual risks carried forward: betweenness-class features share
  the shortest-path functional with CIS (coupling risk — flagged in the
  framework §8); estimator choice affects residual scale (hence the
  robustness ladder at Stage 20); δ_ours median sits ~0.004 above Paper 1's
  matched-control δ (spline baseline is smoother than 1:1 matched
  controls) — documented, monitored at later stages.

## Verdict

**FREEZE 1 achieved.** Residualization is validated (orthogonal to degree,
reproduces Paper 1's matched-pair structure at ρ = 0.785 / δ = 0.104,
replicates in 100% of subjects on the proper statistic). Proceed to
Stage 6 (graph-geometric feature extraction) only after this report is
reviewed.
