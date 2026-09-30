# RESEARCH QUESTION (Paper 2 — frozen)

Frozen 2026-09-27 with `01_CONFIG/CONFIG_FREEZE.md`, before any Paper 2
residual computation. Amendments append-only.

## Primary question

**Which graph-geometric properties explain node-level CIS beyond the effect
expected from connectivity (degree/strength)?**

Formally (master prompt):

    CIS_i = E[CIS_i | k_i]  (connectivity-driven component)
          + R_i             (degree-independent component)

and the Paper 2 object is R_i: which features f explain R_i?

    R_i ~ β1·bridge + β2·redundancy + β3·module_participation
        + β4·core_position + …

## Hypotheses

- **H1 (primary):** Degree-controlled CIS residuals are associated with
  specific graph-geometric properties beyond degree/strength.
  Test: Stage 8/9 feature families with BH-FDR; subject-aware confirmation
  (Stage 11); null arbitration (Stages 15–18).
- **H2:** Extreme positive-residual nodes possess unusually low
  alternative-path redundancy.
- **H3:** Extreme positive-residual nodes have elevated inter-community
  participation.
- **H4:** Extreme positive-residual nodes occupy distinctive core/bridge
  positions.
- **H5:** A multivariate model containing graph-geometric variables explains
  additional variance in CIS beyond degree alone (ΔR² > 0, CV-validated).
- **H6 (exploratory):** The structural signature differs across
  network scales/species.
- **H7 (exploratory):** Human positive-residual nodes and fly extreme cases
  show partially overlapping mathematical signatures.

H6/H7 are never promoted to confirmatory claims regardless of p-values.

## Frozen context facts (from Paper 1, preserved verbatim)

- Human: residual positive in 778/801 subjects; matched-pair
  δ = 0.100, across-subject IQR [0.078, 0.129]; 43/456 nodes survive
  BH-FDR; median split-half rank stability 0.996; R2b (system-specificity)
  NEGATIVE.
- Fly: matched-pair effect NOT null-surviving (z = 1.21, empirical
  p = 0.109) — H1-analog REJECTED in the fly at the matched-pair level.
  Paper 2 inherits this as a prior expectation of scale divergence, NOT as
  an obstacle: the human result stands on its own nulls (200/200 for the
  concentration layer; δ layer via matched controls).

## Language rules (binding)

- "consistent with" not "proves"; "associated with" not "causes";
  "degree-independent component" not "universal residual";
  no "first ever"; no mechanism claim before Stages 15–18 nulls.
- Outcome A/B/C rule (master prompt FINAL SCIENTIFIC CONCLUSION RULE)
  applies verbatim at Stage 24; Outcome C is acceptable.

## What would falsify the program

- Stage 4 shows the model-based residual does NOT reproduce across
  subjects (replication fraction near chance) or grossly disagrees with
  the E03b matched-pair residual → halt, reconcile, re-freeze.
- Stage 15+ degree-preserving nulls reproduce the feature–residual
  associations → the "mechanism" is a degree-sequence artifact → Outcome
  C for that feature; reported as a negative, in the paper.
