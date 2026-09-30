# MATHEMATICAL FRAMEWORK (Paper 2)

Frozen with `01_CONFIG/CONFIG_FREEZE.md` (2026-09-27), before computation.

## 1. Graph and node quantities (inherited, frozen from Paper 1)

- G_s: undirected binary graph of subject s, N = 456 nodes,
  k = round(0.15 · N(N−1)/2) = 15,561 edges (top-|w| threshold on SIFT
  streamline counts; diagonal zeroed).
- k_i: degree of node i in G_s.
- s_i: strength (sum of raw |weights| of incident edges).
- E(G): global efficiency = (1/(N(N−1))) Σ_{u≠v} 1/d(u,v) on shortest
  path lengths d.
- CIS_i (exact, Paper 1 frozen definition, binary graph):

  CIS_i = (E(G) − E(G−i)) / E(G)

  computed by removing node i and recomputing exact all-pairs efficiency
  on the induced (N−1)-node subgraph with (N−1)(N−2) normalization.
  Validated in Paper 1 to 6.1e-16 vs the naive reference implementation.
  CIS is consumed read-only from `04_CIS/subject_cis/sub-XXXX.csv`
  (frozen Paper 1 artifact); Paper 2 never recomputes it for the human
  cohort.

## 2. Degree expectation and residual (the Paper 2 object)

For subject s, the degree expectation is a function m_s(·) estimated
from that subject's own 456 (k_i, CIS_i) pairs:

    E_s[CIS | k] := m_s(k)

Estimators (frozen set; primary first — AMENDED twice pre-unblinding, see
CONFIG_FREEZE.md Amendments 1–2; final form):

- M1 (PRIMARY, Amendment 2): least-squares natural cubic spline of RAW CIS
  on degree, df = 4, fit per subject. No transform, no retransformation
  (transform variants were retired: log invalid for negative CIS;
  asinh retransmission-biased). This is the literal E[CIS | degree].
- M2 (secondary): linear OLS, CIS ~ degree.
- Robustness: polynomial df ∈ {2,3,5,6}; quantile binning (20 equal-count
  degree bins, bin median CIS).

Per-node residual and standardized residual:

    R_i = CIS_i − m_s(k_i)
    ZR_i = R_i / SD_s(R)     (SD across the 456 nodes of subject s)

Negative CIS values are retained exactly as stored (removal can raise
efficiency for redundant nodes); the +1e-6 log offset exists only inside
M1's fit and is recorded as a frozen implementation constant.

## 3. Orthogonality gate (Freeze 1 criterion)

After residualization, per subject s:

    ρ_s = Spearman(R_i, k_i) over i = 1..456

PASS (freeze): median_s(ρ_s) has absolute value < 0.05 AND
mean |ρ_s| < 0.1 (an order of magnitude below the Paper 1 CIS–degree
ρ = 0.943). Also report the M2 (linear) residuals' ρ for contrast.

## 4. Cross-check to Paper 1 (E03b) — AMENDED (Amendment 2)

Paper 1's residual was defined by degree-matched controls (±10% total
degree, 1:1 greedy, nearest-50 fallback) on the top-CIS-decile nodes:
median subject δ = 0.100, IQR [0.078, 0.129], positive in 778/801.
The E03b per-subject statistics are computed on ~46 matched-pair nodes per
subject, NOT all 456 — comparing all-node residual summaries against them
is a unit mismatch (retired).

Frozen cross-check (Stage 3b, `crosscheck_same_pairs.py`): recompute
Cliff's δ per subject from Paper 2 residuals restricted to Paper 1's exact
matched node pairs; require Spearman(δ_ours, δ_paper1) ≥ 0.5 across the
801 subjects. An exact-identity assertion (R_ours(node) − R_ours(control)
= frozen pair residual, max abs error ~ 1e-18) validates that both
residuals act on identical (node, degree, CIS) inputs.

## 5. Cross-subject validation quantities (Stage 4)

- Subject effect: per-subject median R and fraction of nodes with R > 0.
- Population: median across subjects with bootstrap 95% CI (subject-level
  bootstrap, 10,000 resamples, seed 20270927).
- Replication fraction: fraction of subjects whose residual structure is
  directionally consistent (per-subject: median R > 0).
- Heterogeneity: IQR of per-subject effects.
- Leave-one-subject-out (LOSO): recompute population median effect with
  each subject removed; max absolute deviation reported.

## 6. Extreme-node definitions (Stage 5, pre-registered)

Within each subject: ZR thresholds |ZR| at the 99th/95th percentiles
(two-sided: top/bottom 1% and 5%). Outputs:
`positive_extreme_nodes.csv` (ZR above threshold),
`negative_extreme_nodes.csv` (ZR below), `continuous_residuals.csv`
(all subject×node rows). System identities (atlas labels) are joined for
QC only; biological interpretation of extremes is deferred to later stages.

## 7. Fly-side definitions (later stages; frozen now to prevent drift)

The fly study's CIS is a DIFFERENT estimator (fixed-source-panel BFS,
k=4–32, directed binary FAFB graph, 139,255 nodes): documented as
dataset-specific, never silently normalized against human exact-CIS
values. Fly comparisons use normalized comparators only (effect sizes,
z-scores, fractions), per Paper 1 discipline tags. The fly residual-null
result (z = 1.21, p = 0.109, NOT null-surviving) is a frozen input fact.

## 8. Statistical models (Stages 8–11, specified now)

- Univariate: per-feature Spearman + robust Theil–Sen on R ~ feature,
  BH-FDR within family.
- Nested models (Stage 9): M0 CIS ~ degree; M1 + strength; M2 + single
  feature; M3 + pre-registered non-redundant feature set; compared by
  adjusted R², AIC, BIC, 5-fold CV R² (grouped by subject), partial R².
- Subject-aware (Stage 11): mixed effects R_ij ~ features + (1|subject),
  with cluster-robust SE cross-check.
- Coupling note: betweenness-style path metrics mathematically relate to
  the efficiency functional inside CIS. Any feature whose computation
  shares the all-pairs shortest-path structure with CIS is flagged
  `coupling_risk=true` and is interpreted only through ΔR² vs
  degree-only and through the degree-preserving nulls — never alone.
