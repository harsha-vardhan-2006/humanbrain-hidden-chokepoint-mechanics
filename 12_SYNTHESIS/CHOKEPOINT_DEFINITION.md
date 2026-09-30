# Hidden-chokepoint operational definition (Paper 2)

A candidate hidden chokepoint is a node satisfying ALL of:

1. **High CIS** - node-level population CIS in the top-k of 456,
2. **High degree-conditioned residual** - population residual in the
   top-k (residual is orthogonal to degree by construction; Freeze-1
   gate: median |rho(R, degree)| = 0.0327),
3. **Degree-preserving null** - Stage 15 arbitrated the FEATURE-R
   association machinery under exact degree-preserving rewiring:
   observed |median rho| for every feature falls INSIDE the null p95
   band (Outcome C for all 9 features). A NODE-level null verdict is
   therefore NOT_ESTABLISHED - the null does not license calling any
   individual node a null-surviving chokepoint.
4. **Configuration stability** - dual top-k membership under both the
   primary spline estimator family and the pre-registered alternatives
   (Stage 20 R1/R2/R5).
5. **Cross-module position signature** - median bridge score in the
   upper half of the pooled distribution (bridge is the strongest
   Stage-8 associate, median within-subject rho = +0.4985).

## Sensitivity to k (joint-criterion candidate counts)

 top_frac  k  n_cis_top  n_res_top  n_both  n_candidates_with_position  candidate_share_pct
     0.01  5          5          5       1                           1             0.219298
     0.02  9          9          9       2                           2             0.438596
     0.05 23         23         23       3                           3             0.657895
     0.10 46         46         46       7                           7             1.535088

## Verdict framing (mandatory)

- The residual EXISTS (801/801 subjects, delta = 0.104, CI
  [0.1007, 0.1073]) and is DEGREE-INDEPENDENT (gate passed).
- The residual is PREDICTABLE out-of-sample from network position
  (ridge cv-R2 = 0.574 vs degree-only ~ 0; permuted control 0.0024).
- The candidate chokepoint LABEL is operational only: under the frozen
  Stage-15 degree-preserving null, no feature-R association exceeds
  the null band, so any per-node chokepoint claim is
  **NOT_ESTABLISHED** at null-arbitration level.
- No causal claim is made or licensed (observational connectome data).

Candidates at the 5% resolution are listed in CHOKEPOINT_CANDIDATES.csv
with per-criterion flags; the node-level null column is uniformly
NOT_ESTABLISHED by design.
