# Figure legends (Paper 2)

**Fig. P2-1 `degree_vs_CIS.png` (Stage 3).** CIS vs degree, population
level. Degree dominance (median ρ = 0.943) motivates explicit
residualization; raw CIS is never interpreted directly.

**Fig. P2-2 `degree_vs_residual.png` (Stage 3).** Residual R vs degree
after spline residualization. Orthogonality gate passed (median
|ρ(R, degree)| = 0.0327).

**Fig. P2-3 `residual_distribution.png` (Stage 3).** Residual
distribution; upper-tail concentration motivates the pre-registered
extreme-set analyses (top-1/5%).

**Fig. P2-4 `fig_p2_feature_associations.png` (Stage 8).** Within-subject
median ρ(R, feature) for all 12 features with null-derived significance;
bridge is the strongest associate (+0.4985).

**Fig. P2-5 `fig_p2_null_arbitration.png` (Stage 15).** Observed
|median ρ| per feature vs the degree-preserving null p95 band
(12 subjects × 100 nulls, exact degree preservation, full CIS + feature
recomputation per null). Every observed point lies inside its band —
Outcome C.

**Fig. P2-6 `fig_p2_ml_benchmark.png` (Stage 10).** Out-of-sample cv-R²
for degree-only, ridge, elastic net and MLP with permuted-R controls
(5-fold subject-grouped CV × 3 seeds). Ridge +0.574 vs degree-only ≈ 0;
permuted control 0.002. MLP arm unstable (documented artifact).

**Fig. P2-7 `fig_p2_subject_aware.png` (Stage 11).** Within-subject
standardized betas with CR1 cluster-robust 95% CIs (N = 801 subjects,
365,256 rows); all 8 features q < 1e-7.

**Fig. P2-8 `fig_p2_chokepoint_sensitivity.png` (Stage 22).**
Operational chokepoint candidate counts vs threshold k under the joint
criteria (CIS top-k ∧ residual top-k ∧ bridge upper half):
1/2/3/7 nodes at k = 1/2/5/10%.

**Fig. P2-9 `fig_p2_bio_enrichment.png` (annotation stage).** Share
difference vs expected for top-10%-CIS nodes by major structure
(10,000 permutations, two-sided; * q < 0.05). Cortex is significantly
under-represented. Cell-type rows: NOT_ESTABLISHED (parcels are not cell
types).

**Fig. P2-10 `fig_p2_fly_case.png` (Stages 12–13).** ME.131 z-profile vs
86 degree-matched fly targets (CIS z = +23.4 shown in text only, off-scale).
Case study only; no population claim.
