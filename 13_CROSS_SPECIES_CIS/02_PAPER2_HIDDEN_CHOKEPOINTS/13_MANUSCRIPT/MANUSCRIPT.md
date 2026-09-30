# Hidden Chokepoints: Graph-Geometric Determinants of Degree-Independent Control Impact in Connectome Networks

**Paper 2 of the cross-species control-impact series.**
Harsha Vardhan Malipeddi. Working manuscript — 2026-09-30.
All numbers trace to frozen artifacts in this study tree (see
`REPRODUCIBILITY.md`); verification gates V01–V12 pass 12/12.

---

## Abstract

**Question.** After accounting for connectivity (degree/strength), which
graph-geometric properties explain node-level variation in removal-based
control impact (CIS) in the human structural connectome — and do any nodes
qualify as operationally defined "hidden chokepoints"?

**Methods.** 801 QC-pass subjects (AOMIC ID1000; 4S456 parcellation; 15%
cost threshold) × 456 nodes. CIS consumed read-only from the frozen Paper 1
release. The degree-independent residual R_i = CIS_i − ĈIS(degree_i) is
estimated per subject with a frozen cubic-spline family (orthogonality
gate: median |ρ(R, degree)| = 0.0327). Eleven network features (path
metrics, redundancy, bridge, participation, core, clustering, eigenvector,
PageRank) are associated with R within-subject, arbitrated by exact
degree-preserving nulls (12 subjects × 100 nulls with per-null full CIS +
feature recomputation), benchmarked out-of-sample (subject-grouped CV), and
mapped onto evidence-leveled biological annotations.

**Results.** (1) The residual is universal in sign: δ = 0.104, positive in
801/801 subjects (95% CI [0.1007, 0.1073]). (2) Network position predicts
the residual out-of-sample: ridge cv-R² = 0.574 (permuted-R control 0.002;
degree-only ≈ 0), with the strongest within-subject associates being bridge
score (ρ = +0.4985), closeness (d-directed; +0.2489), path redundancy
(−0.2179) and participation (−0.1676). (3) **Degree-preserving-null
arbitration is negative (Outcome C):** under exact degree-sequence
preservation, every feature's observed association falls inside the null
p95 band — the association machinery is reproducible in real graphs but is
not licensed as a degree-independent mechanism. (4) Joint-criterion
"chokepoint" candidates are rare and threshold-sensitive (1/2/3/7 nodes at
k = 1/2/5/10%); per-node null arbitration is NOT_ESTABLISHED. (5) Top-CIS
nodes under-represent cortex (share 0.44 vs expected 0.88; q < 0.001).
Cell-type fields are NOT_AVAILABLE (parcels are not cell types). (6) The
fly connectome's residual also fails its degree-preserving null
(z = 1.21, p = 0.109, frozen): two same-direction negatives at different
scales license no universal-mechanism claim.

**Conclusion.** Degree-independent control impact is a real, learnable,
anatomically non-uniform property of human connectome architecture whose
fine structure is **null-qualified**: exact degree preservation explains
the observed feature–residual associations at the population level. The
"hidden chokepoint" remains an operational, bounded construct rather than a
validated node class.

---

## 1. Introduction and research question

Paper 1 established that CIS in human structural connectomes is strongly
degree-confounded (ρ = 0.943), that a small degree-matched residual exists
(δ = 0.100), and that anatomy does not transfer across scales ("architecture
replicates, anatomy doesn't"; fly visual contribution ≈ 80% vs human ≈ 2%).
Paper 2 asks the mechanistic follow-up **frozen before unblinding**
(`01_CONFIG/CONFIG_FREEZE.md`):

> H1 (primary): degree-controlled CIS residuals are associated with specific
> graph-geometric properties beyond degree/strength.

Secondary hypotheses H2–H5 concern low redundancy, inter-community
participation, core/bridge positions and multivariate explainability;
H6–H7 (cross-scale) are exploratory and are never promoted to confirmatory
claims.

## 2. Data and node semantics

- **Human:** AOMIC ID1000 derived structural connectomes (Zenodo 19796783,
  CC-BY-4.0), 4S456 parcellation, SIFT streamline counts, 15% cost
  threshold (k = 15,561 edges), primary weight `sift_radius2_count`.
  A **network node is an atlas PARCEL** — a macroscopic brain region, never
  an individual neuron. Node identity derives from the frozen label file
  (`00_MANIFEST/manifests/atlas_4S456_system_labels.csv` + PROVENANCE).
- **Fly (comparison):** FAFB v783 frozen release artifacts (individual
  neurons); consumed read-only.

## 3. CIS and the residual

CIS_i = (E(G) − E(G−i)) / E(G), exact recomputation (Paper 1, validated to
6.1e-16). The primary residual is R_i = CIS_i − E[CIS | degree_i] with the
conditional expectation estimated per subject by OLS on raw CIS against a
df=4 natural cubic spline of degree (Amendment 1 lineage; see
`MATHEMATICAL_FRAMEWORK.md`). Gates: |median ρ(R, degree)| < 0.05
(achieved 0.0327) and same-pairs agreement with Paper 1's matched-pair δ
(ρ = 0.785; input identity exact to 8.7e-19).

## 4. Feature set

Strength, betweenness, closeness (directed-transposed proxy), path
redundancy, bridge score, participation coefficient, within-module z,
k-core, eigenvector centrality, PageRank, clustering (11 + degree).
Path metrics carry a pre-registered coupling-risk flag; subject-aware
within-subject estimation and sign-stability across the estimator ladder
address it.

## 5. Results

### 5.1 The residual replicates (Stage 4)

δ_ours = 0.104 (median), subject-bootstrap CI [0.1007, 0.1073], 801/801
positive; LOSO max deviation 5.4e-8.

### 5.2 Univariate and subject-aware associations (Stages 8, 11)

All 12 features associate with R at q < 1e-27 (within-subject medians:
bridge +0.4985, closeness_d +0.2489, redundancy −0.2179, participation
−0.1676, clustering −0.1658, betweenness +0.1333, eigenvector +0.0834,
kcore +0.0556, PageRank −0.0379, strength −0.0689). The 8-feature
within-subject model with CR1 cluster-robust SEs retains all features at
q < 1e-7 (N = 801 subjects, 365,256 rows).

### 5.3 Multivariate and predictive benchmarks (Stages 9–10)

Pruned 7-predictor model: Δcv-R² = +0.294 vs degree-only. Full ridge:
cv-R² = 0.574 (elastic net 0.561; MLP arm unstable and reported as a
documented benchmark artifact). Permuted-R controls ≈ 0.002.

### 5.4 Negative controls (Stage 21)

NC1 (feature-label permutation) and NC2 (residual permutation) bands are
|ρ| ≤ 0.004; observed associations exceed both with margins ≥ 0.13.

### 5.5 Degree-preserving null arbitration (Stage 15) — Outcome C

Under Maslov–Sneppen rewiring preserving the exact degree sequence
(verified per null), with full CIS + feature recomputation per null
(12 subjects × 100 nulls, seed 20270927): null |ρ(R, feature)| bands are
wide (p95: clustering 0.731, redundancy 0.681, bridge 0.654, participation
0.461, betweenness 0.210) and **every observed association lies inside its
band**. Interpretation (pre-registered Outcome C): the feature–residual
associations of the real graphs do not exceed what degree-preserving
randomization already produces; they are structural descriptions, not
degree-independent mechanisms.

### 5.6 Robustness (Stage 20)

Sign-consistency across the estimator ladder (linear, df=3, bin-20) for
bridge (+0.435…+0.524) and participation; winsorization at the 99.9th
percentile leaves headline associations unchanged; extreme-set median
standardized residual +3.70 (top-1%) / +1.68 (top-5%).

### 5.7 Biological annotation and enrichment

456/456 nodes mapped to atlas parcel identities, hemisphere, major
structure and functional network at HIGH confidence
(`results_annotation/human_node_biological_annotations.csv`). Top-10%-CIS
nodes under-represent cortex (observed share 0.44 vs expected 0.88;
10,000-permutation two-sided p < 1e-4, q = 0.00017). Cell-class,
neuronal-class, neurotransmitter and transcriptomic fields: NOT_AVAILABLE
(a macroscopic parcel is not a cell type); the corresponding enrichment
tests: NOT_ESTABLISHED. MNI centroids are not shipped by the atlas:
spatial statistics NOT_ESTABLISHED (§7).

### 5.8 Operational chokepoints (Stage 22)

Candidates satisfying (CIS top-k) ∧ (residual top-k) ∧ (bridge upper
half): 1 node at k = 1%, 2 at 2%, 3 at 5%, 7 at 10%
(`12_SYNTHESIS/CHOKEPOINT_CANDIDATES.csv`). Per-node degree-preserving-null
verdicts: NOT_ESTABLISHED — the Stage-15 design arbitrates the
feature–residual machinery, not individual nodes. The chokepoint construct
is therefore operational and bounded, not a validated node class.

### 5.9 Fly comparison (Stages 12–13, 22b)

ME.131 (OCT, visual centrifugal) vs 86 degree-matched targets: CIS z = +23.4
(154× peer median), sampled directed betweenness z = +4.08 — case study
only. The fly population-level residual did not survive its
degree-preserving null (z = 1.21, p = 0.109; frozen v1.0.0). Human Stage-15
Outcome C is a same-direction negative at a different scale. Shared:
degree dominance; small positive residual. Not shared: anatomical
concentration, visual contribution, unit of analysis, cell-type ground
truth, predictive benchmark. No universal-law or same-mechanism claim.

## 6. Discussion

The human connectome's degree-independent control-impact residual is
reproducible, sign-universal across subjects, anatomically biased away
from cortex, and substantially learnable from network position — yet its
feature associations are matched by degree-preserving nulls. The most
defensible reading: **what looks like a "chokepoint signature" (bridging,
sparse alternative paths) is largely a consequence of degree architecture
plus randomized-topology baselines**, and the residual's true fine
structure, if any, is finer than this design can arbitrate. This bounds
Paper 1's residual honestly: real, but not yet mechanistically explained.

## 7. Spatial status and limitations

- **Spatial controls NOT_ESTABLISHED:** the atlas label file ships no
  parcel centroids; Moran's I / distance-constrained nulls cannot be run
  without inventing coordinates. Residual-vs-degree orthogonality and the
  (topology-randomizing) degree-preserving null bound, but do not remove,
  spatial-autocorrelation concerns.
- Atlas parcels ≠ neurons; no cell-type ground truth at parcel resolution.
- CIS is observational network importance, not causal perturbation.
- The fly case study (n = 1) does not generalize; fly and human CIS
  estimators differ and are never equated.
- 12-subject null design is compute-bound (100 nulls/subject with exact
  CIS); bands are Monte-Carlo estimates at frozen seed.
- MLP benchmark instability; reported for completeness, not interpreted.

## 8. Reproducibility

Every stage: script, frozen seed, fail-loud gates, artifact on disk;
verification V01–V12 re-derives all headline numbers from artifacts
(12/12 PASS). See `REPRODUCIBILITY.md` for exact commands.
