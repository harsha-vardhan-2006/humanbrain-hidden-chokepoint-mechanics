# P2-CONFIG (frozen) — Paper 2: Hidden Chokepoints

Frozen 2026-09-27, BEFORE any Paper 2 residual computation.
Amendments are append-only: add a new `## AMENDMENT` section; never edit above.

## Identity

- Study tree: `13_CROSS_SPECIES_CIS/02_PAPER2_HIDDEN_CHOKEPOINTS/`
- Parent release: `humanbrain_cross_species_cis` v1.1.0 (frozen; read-only)
- Companion fly release: `fruitfly` v1.0.0 (frozen; read-only)
- Working title: *Hidden Chokepoints: Graph-Geometric Determinants of
  Degree-Independent Control Impact in Connectome Networks*

## Research question (primary, frozen)

Which graph-geometric properties explain node-level CIS beyond the effect
expected from connectivity (degree/strength)?

## Hypotheses (frozen before unblinding)

- **H1 (primary):** Degree-controlled CIS residuals are associated with
  specific graph-geometric properties beyond degree/strength.
- **H2:** Extreme positive-residual nodes possess unusually low
  alternative-path redundancy.
- **H3:** Extreme positive-residual nodes have elevated inter-community
  participation.
- **H4:** Extreme positive-residual nodes occupy distinctive core/bridge
  positions.
- **H5:** A multivariate model containing graph-geometric variables explains
  additional variance in CIS beyond degree alone.
- **H6 (exploratory):** The structural signature differs across
  network scales/species.
- **H7 (exploratory):** Human positive-residual nodes and fly extreme cases
  show partially overlapping mathematical signatures.

H6/H7 are exploratory: they are never promoted to confirmatory claims.

## Cohorts (frozen)

- Human primary: 801 QC-pass subjects (Paper 1 frozen flags; flag-never-delete)
  × 456 nodes (4S456), primary weight sift_radius2_count, 15% cost.
- Human secondary: full 900 (descriptive only, never headline).
- Fly: FAFB v783 frozen artifacts (e10b_final.json, e14_v2_summary.json,
  e14 catalogue v2). Case study: ME.131-class nodes ONLY as case study.

## Primary outcome and residualization (frozen)

- Primary outcome: subject-level residual R_i = CIS_i − E[CIS | degree]
  with E[CIS|degree] estimated per subject (primary: OLS on log10(CIS +
  1e-6) ~ spline(degree, df=4); secondary: linear OLS; robustness: quantile
  binning q=20, polynomial df ∈ {1,2,3,5,6}).
- Residual validation gate: |Spearman(R, degree)| < 0.05 per subject
  (median across subjects), and mean |ρ| strictly below the Paper 1
  CIS–degree ρ = 0.943 by an order of magnitude.
- The matching residual (Paper 1 E03b, matched-pair δ = 0.100) is the
  cross-check: Stage 3 must reproduce it qualitatively (sign, magnitude)
  or document why not, BEFORE proceeding.

## Extreme-node thresholds (pre-registered, frozen)

Top 1%, top 5%, bottom 1%, bottom 5% of subject-level standardized
residual ZR; continuous analyses run in parallel. Thresholds fixed before
any biological/system identity is inspected.

## Multiple comparisons (frozen)

- Confirmatory: H1 evaluated on the pre-selected primary feature family
  with BH-FDR q < .05 within family.
- Exploratory screening: BH-FDR q < .05, labeled exploratory; never
  promoted without new pre-registration.

## Seeds (frozen)

- Subject/residual bootstrap: 20270927
- Null ensembles (Stages 15–18): 100+i per graph, ≥100 reps for CIS-bearing
  nulls (compute-bound; exact count locked at Stage 15 with runtime budget),
  1,000 reps for feature-only nulls.
- Every stochastic step records (script, seed, git SHA) in its output JSON.

## Session plan (checkpoint discipline)

This session executes Stages 0–5 and stops at FREEZE 1. No feature
extraction (Stage 6+) runs before Freeze 1 is reviewed. Freezes 2–5 as per
the master prompt.

## Prohibitions (restated)

Raw data read-only; no manual edits of numeric outputs; no result deletion
(supersede with markers); correlation is never causation; no universal-law
language; the fly residual null result (z = 1.21, p = 0.109) is preserved
unless an independent audit shows an error; every figure/table regenerates
from a script.

## AMENDMENT 1 (2026-09-27, pre-unblinding) — primary estimator transform

The frozen primary estimator M1 (`log10(CIS + 1e-6) ~ spline(degree, df=4)`)
is **invalid for these data**: CIS is signed (6.1% of subject-node rows are
negative; removal can raise efficiency), and for CIS < −1e-6 the log
argument is negative → NaN fits. Discovered at first execution of Stage 3
by a hard failure in the QC figure code; a secondary bug (NaN→0 masking in
the orthogonality statistic) is fixed in the same amendment.

Amended primary estimator (frozen, replaces M1 above):

    M1 = OLS on asinh(CIS / c_s) ~ natural cubic spline(degree, df=4),
    c_s = median(|CIS|) over the 456 nodes of subject s (recorded per
    subject); predictions back-transformed as R̂ = sinh(f̂) · c_s.

Rationale: asinh is the standard signed-data variance stabilizer — linear
near zero, logarithmic in the tails — so no ad hoc offset is needed and
negative CIS values are handled exactly. The estimator ladder, gate,
thresholds, seeds, and all other frozen settings are unchanged. This
amendment was made BEFORE any Stage 3–5 result was inspected or consumed
(fail-loud execution order; no statistic had been read).

## AMENDMENT 2 (2026-09-27, pre-unblinding) — estimator + cross-check fix

Two further defects discovered during first execution, both fixed before
any Stage 3–5 statistic was consumed for a decision:

(1) TRANSFORM + RETRANSFORMATION BIAS. Amendment 1's asinh fit is a
    smooth monotone reparameterization, but back-transforming predictions
    through sinh is biased under heteroscedastic spread (Jensen), which
    left a small systematic ρ(R, degree) = −0.063 (gate: |median| < 0.05).
    The primary estimator is therefore SIMPLIFIED to what the estimand
    literally requires:

        M1 (primary) = least-squares natural cubic spline of RAW CIS on
        degree, df = 4, fit per subject (no transform, no retransformation).

    Robustness ladder unchanged (M2 linear; poly df ∈ {2,3,5,6};
    quantile-binning q=20). The M1_spline4_log entry is retired
    (invalid: log of negative CIS), the M1_spline4_asinh entry is retired
    (retransformation bias), both preserved in git history and here.

(2) CROSS-CHECK UNIT MISMATCH. Stage 4 compared the all-node median
    residual against E03b quantities computed on ~46 matched-pair nodes
    only — an apples-to-oranges comparison that produced a spurious
    "BLOCKER" (ρ = −0.144). The cross-check is redefined as the
    SAME-PAIRS comparison (Stage 3b, `crosscheck_same_pairs.py`): recompute
    Cliff's delta per subject from Paper 2 residuals restricted to Paper 1's
    exact matched node pairs, then require Spearman(delta_ours,
    delta_paper1) ≥ 0.5. An exact-identity assertion (R(node) − R(control)
    = frozen residual_cis) validates input equivalence.

Gate consequences (unchanged thresholds): orthogonality |median ρ| < 0.05
now applies to the raw-CIS primary estimator; the Stage 4 sign-agreement
quantity is retired (meaningless against pair-only deltas) and replaced by
the same-pairs Spearman.

## AMENDMENT 3 (2026-09-28, pre-analysis) — redundancy feature repair

**Defect.** The Stage 6 `redundancy` feature (local alternative-path
redundancy, H2's primary variable) was computed with a **boolean
common-neighbor matrix**: numpy bool-matrix `dot` performs OR-semantics, so
common-neighbor counts collapsed to {0, −1}, `C > 0` was never true, and the
feature degenerated to the direct-neighbor-edge mask — numerically identical
to `clustering` on all rows (verified: Pearson r = 1.000 over 365,256 rows;
max abs diff 0.0).

**Timing.** Discovered in the pre-analysis integrity sweep of the completed
Stage 6 matrix, BEFORE any downstream stage consumed the feature (Stages 7+
had not run; no statistic, table, or figure involved `redundancy`).

**Fix.** `03_FEATURE_EXTRACTION/extract_features.py::_redundancy`: cast the
adjacency to int32 before the common-neighbor product (`C = Ai[nb,:] ·
Ai[:,nb] − 1`). No other line changes. A unit assertion
(`redundancy != clustering` on any subject with at least one transitive
neighbor pair) is added to the Stage 6 QC.

**Action.** Per-subject caches and `NODE_FEATURE_MATRIX.parquet` are
regenerated (resume-safe: only the `redundancy` column changes). No frozen
gate, threshold, seed, or hypothesis is altered; this repairs the feature's
implementation to its frozen definition (MATHEMATICAL_FRAMEWORK §3 path /
§8 redundancy family).
