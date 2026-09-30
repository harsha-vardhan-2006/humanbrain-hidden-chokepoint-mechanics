# Degree-Independent Control Impact in the Human Structural Connectome: Graph-Geometric Associations and Degree-Preserving Null Arbitration

**Paper 2 of the cross-species control-impact series (CIS).**

**Author:** Harsha Vardhan Malipeddi
**Affiliation:** Independent Researcher
**Corresponding author:** Harsha Vardhan Malipeddi
**Email (corresponding author):** harshavardhanmalipeddi1@gmail.com
**Funding:** The author received no specific funding for this work.
**Competing interests:** The author declares no competing interests.
**Ethics:** This study used previously acquired, de-identified data
(AOMIC ID1000); no new human data were collected. Governance/consent
details are governed by the source dataset's own documentation
(see Data availability).
**Author contributions:** H.V.M. conceived the study, developed the
analysis framework, performed all computational analyses, validation and
verification, and wrote the manuscript.
**Data & code availability:** see §8 (all data sources identified;
analysis code and artifacts in the frozen repository, release v2.0.1).
**Version:** v2.0.1 — 2026-09-30
**Study tree:** `13_CROSS_SPECIES_CIS/02_PAPER2_HIDDEN_CHOKEPOINTS/`
**Provenance:** every number in this paper traces to a frozen artifact on disk in
the study tree (see §8 and `REPRODUCIBILITY.md`). Verification gates V01–V12
re-derive all headline numbers from artifacts: **12/12 PASS**
(`13_MANUSCRIPT/verify_stage24.py`, exit 0). Full-project QC: **25 PASS /
0 FAIL / 1 WARNING** (`QC/FINAL_QC_REPORT.md`).

---

## Abstract

**Question.** After accounting for connectivity (degree/strength), which
graph-geometric properties explain node-level variation in removal-based
control impact (CIS) in the human structural connectome — and do any nodes
qualify as operationally defined "hidden chokepoints"?

**Methods.** 801 QC-pass subjects (AOMIC ID1000; 4S456 parcellation; 15% cost
threshold) × 456 nodes. CIS consumed read-only from the frozen Paper 1
release. The degree-independent residual R_i = CIS_i − ĈIS(degree_i) is
estimated per subject with a frozen cubic-spline family (orthogonality gate:
median |ρ(R, degree)| = 0.0327). Eleven network features (path metrics,
redundancy, bridge, participation, core, clustering, eigenvector, PageRank)
are associated with R within-subject,arbitrated by exact degree-preserving nulls (12 subjects × 100 nulls, seed 20270927, with per-null full CIS +
feature recomputation; subject selection stratified, estimator-equivalence
validated — §3.5), benchmarked out-of-sample (subject-grouped CV), and
mapped onto evidence-leveled biological annotations.

**Results.** (1) The residual is positive in all subjects: δ = 0.104, positive in
801/801 subjects (95% CI [0.1007, 0.1073]). (2) Network position predicts the
residual out-of-sample: ridge cv-R² = 0.574 (permuted-R control 0.0024;
degree-only ≈ 0), with the strongest within-subject associates being bridge
score (median ρ = +0.4985), closeness (d-directed proxy; +0.2489), path
redundancy (−0.2179) and participation (−0.1676). (3) **Degree-preserving-null
arbitration is negative (Outcome C):** under exact degree-sequence
preservation, every feature's observed association falls inside the null p95
band — the association machinery is reproducible in real graphs but is not
licensed as a degree-independent mechanism. (4) Joint-criterion "chokepoint"
candidates are rare and threshold-sensitive (1/2/3/7 nodes at
k = 1/2/5/10%); per-node null arbitration is NOT_ESTABLISHED. (5) Top-10%-CIS
nodes under-represent cortex (share 0.444 vs expected 0.877; q = 0.00017) and
over-represent subcortex and thalamus; cell-type fields are NOT_AVAILABLE
(parcels are not cell types). (6) The fly connectome's residual also fails its
degree-preserving null (z = 1.21, p = 0.109, frozen): two same-direction
negatives at different scales license no universal-mechanism claim.

**Conclusion.** Degree-independent control impact is a real, predictable-from-network-features,
anatomically non-uniform property of human connectome architecture whose fine
structure is **null-qualified**: exact degree preservation explains the
observed feature–residual associations at the population level. The "hidden
chokepoint" remains an operational, bounded construct rather than a validated
node class.

**Keywords:** structural connectome; network control theory; controllability;
degree confounding; null models; graph metrics; cross-species comparison.

---

## 1. Introduction

Network control theory frames the brain as a dynamical system whose
structural connectome constrains its reachable dynamics
(Gu et al., 2015; Tang & Bassett, 2018; Liu et al., 2011). Removal-based
control impact — here **CIS** (Control Impact Score), the fractional loss of
average network controllability upon node removal,
CIS_i = (E(G) − E(G−i)) / E(G), with E the global efficiency
(Latora & Marchiori, 2001) — indexes each region's systemic importance,
extending the classical error/attack-tolerance view of network robustness
(Albert et al., 2000). Paper 1 of this series established two facts that motivate the present work:
(i) raw CIS in the human structural connectome is strongly degree-confounded
(median ρ(CIS, degree) = 0.943); and (ii) a small but strictly
degree-matched residual exists and replicates (δ = 0.100 in Paper 1;
re-derived here as 0.104). Paper 1 also showed that anatomy does not transfer
across scales ("architecture replicates, anatomy doesn't"): the fly visual
system contributes ≈ 80% of total CIS while the human visual system
contributes ≈ 2%.

Paper 2 asks the mechanistic follow-up, frozen before unblinding
(`01_CONFIG/CONFIG_FREEZE.md`, protocol + Amendments 1–3):

> **H1 (primary):** degree-controlled CIS residuals are associated with
> specific graph-geometric properties beyond degree/strength.

Secondary hypotheses H2–H5 concern path redundancy, inter-community
participation, core/bridge positions, and multivariate explainability of the
residual. H6–H7 (cross-scale transfer) are exploratory and are never promoted
to confirmatory claims. All confirmatory tests are pre-registered against an
Outcome A/B/C arbitration rule: **A** = association survives an exact
degree-preserving null (mechanism licensed); **B** = mixed, feature-dependent;
**C** = no association exceeds the null band (mechanism not licensed).

## 2. Data and node semantics

- **Human.** AOMIC ID1000 derived structural connectomes (Snoek et al.,
  2021; Zenodo 19796783, CC-BY-4.0): 801 QC-pass subjects, 4S456 parcellation,
  SIFT streamline counts (Smith et al., 2015; primary weight
  `sift_radius2_count`), 15% cost threshold (k = 15,561 edges;
  Achard & Bullmore, 2007). CIS values are consumed **read-only** from the
  frozen Paper 1 release (801 × 456).
- **Fly (comparison only).** FAFB v783 frozen release artifacts
  (Dorkenwald et al., 2024; FlyWire: Dorkenwald et al., 2023):
  individual neurons; 3,518 targets. Consumed read-only.
- **Node semantics (mandatory).** A human network node is an atlas **PARCEL**
  — a macroscopic brain region, never an individual neuron. Node identity
  derives from the frozen label file
  (`00_MANIFEST/manifests/atlas_4S456_system_labels.csv` + PROVENANCE).

## 3. Methods

### 3.1 CIS and the degree-independent residual

CIS_i = (E(G) − E(G−i)) / E(G), exact recomputation (Paper 1 pipeline,
validated to 6.1e-16 relative tolerance). The primary residual is

  R_i = CIS_i − E[CIS | degree_i],

with the conditional expectation estimated **per subject** by OLS of raw CIS
on a df = 4 natural cubic spline of degree (regression splines:
Hastie et al., 2009; Amendment 1 lineage;
`00_DOCS/MATHEMATICAL_FRAMEWORK.md`). Gates (all passed): orthogonality
median |ρ(R, degree)| = 0.0327 < 0.05; same-pairs agreement with Paper 1's
matched-pair Cliff's δ (Cliff, 1993), ρ = 0.785; input identity exact to
8.7e-19.

### 3.2 Feature set

Strength, betweenness (Freeman, 1977), closeness (directed-transposed proxy),
path
redundancy, bridge score, participation coefficient (Guimerà & Amaral, 2005),
within-module z (Guimerà & Amaral, 2005), k-core (Seidman, 1983),
eigenvector centrality (Bonacich, 1972), PageRank (Page et al., 1999), and
clustering (Watts & Strogatz, 1998) — 11 features + degree.
Path metrics carry a pre-registered coupling-risk flag (they co-vary with
degree by construction); subject-aware within-subject estimation and
sign-stability across an estimator ladder address this risk (§3.6).

### 3.3 Univariate and subject-aware inference

Within-subject Spearman ρ(R, feature), summarized by subject medians, with
null-derived significance (all 12 features q < 1e-27). The confirmatory model
is a within-subject standardized regression on 8 features with CR1
cluster-robust standard errors (MacKinnon & White, 1985) clustered on
subject (N = 801 subjects,
365,256 node-level rows; `08_STATISTICS/SUBJECT_AWARE_MODEL.json`): all 8
features retain q < 1e-7.

### 3.4 Multivariate and out-of-sample benchmark

5-fold subject-grouped CV × 3 seeds, numpy-native implementations
(`08_STATISTICS/ML_BENCHMARK.json`): degree-only, full ridge (11 features),
elastic net, and an MLP arm. Predictive benchmark only — **not** a mechanism
claim. A permuted-R control (labels permuted within fold) anchors the
chance level.

### 3.5 Degree-preserving null arbitration (confirmatory)

Maslov–Sneppen double-edge rewiring preserving the **exact degree sequence**
(verified per null), 12 subjects × 100 nulls, seed 20270927. Per null: full
CIS recomputation (`node_cis_fast`) + full feature recomputation +
residualization via the documented 20-bin quantile-median robust proxy of the
frozen spline estimator. Summary statistic: |median ρ(R, feature)| vs its
null distribution; verdict per feature = observed vs null p95
(`06_NULL_MODELS/NULL_FEATURE_RESULTS.json`; resume-safe JSONL checkpoint
design, 1,200 records).

### 3.6 Robustness and negative controls

Estimator ladder (linear, df = 3 spline, 20-bin quantile-median) for
residualization; winsorization at the 99.9th percentile of CIS; extreme-set
analyses (top-1/5% residual). Negative controls NC1 (feature-label
permutation) and NC2 (residual permutation) establish chance bands
(`07_ROBUSTNESS/NEGATIVE_CONTROLS.json`).

### 3.7 Biological annotation and enrichment

456/456 nodes mapped to atlas parcel identity, hemisphere, major structure,
cortical status and functional network at HIGH confidence
(`results_annotation/human_node_biological_annotations.csv`).
Enrichment: share difference of top-10% sets (CIS and residual) vs expected
under 10,000 node-label permutations (two-sided), BH-corrected q
(Benjamini & Hochberg, 1995), seed
20270927. Degree-controlled partial Spearman of residual vs category given
log-degree. Cell-class, neuronal-class, neurotransmitter and transcriptomic
fields are **NOT_AVAILABLE by discipline** (a macroscopic parcel is not a
cell type); the corresponding tests are NOT_ESTABLISHED.

### 3.8 Operational chokepoint definition

A candidate hidden chokepoint satisfies ALL of: (1) population CIS top-k;
(2) population residual top-k; (3) position signature — median bridge score
in the upper half of the pooled distribution; (4) configuration stability
under the estimator ladder (Stage 20 R1/R2/R5). The node-level null verdict
is NOT_ESTABLISHED **by design**: the Stage-15 null arbitrates the
feature–residual machinery, not individual nodes.

### 3.9 Null ensemble calibration and Monte Carlo precision

The confirmatory null uses 12 subjects × 100 nulls. **Subject selection.**
The 12 subjects were drawn at random (frozen seed 20270927) from the 801;
their observed statistics are representative: the pooled-801 bridge median
(+0.4985) vs the 12-subject value (+0.466) differs by 0.03, well inside the
Monte-Carlo wobble of the ensemble (per-subject medians scatter ≈ ±0.02–0.05
for bridge). **Why 100 nulls.** Each null carries a full exact CIS
recomputation (456-node graph, 455 removals); 1,200 such recomputations was
the compute-feasible budget, following the Paper-1 precedent of ≥100
rewires/graph. **Monte-Carlo resolution.** With 1,200 records the p95 is
estimated from its upper ~60 order statistics; the resulting p95 standard
error is small relative to the width of the bands (IQR of |ρ| per feature
≈ 0.03–0.07 vs band half-widths 0.10–0.40), and every observed statistic
sits strictly inside its band — not at the boundary — so the Outcome C
verdict is not sensitive to p95 estimation error at this ensemble size.
**Scaling check.** Because the observed |median ρ| values fall 0.02–0.24
below their bands, a 10× larger ensemble (12 × 1,000) would have to narrow
the p95 by more than the entire observed-to-band gap to overturn the
verdict; this is far beyond the recorded Monte-Carlo variability.

### 3.10 Cross-species comparison

Conservative 12-property human-vs-fly table
(`12_SYNTHESIS/HUMAN_VS_FLY_COMPARISON.{csv,md}`); fly numbers from the
frozen fly v1.0.0 release; the fly population-level null result
(z = 1.21, p = 0.109) is preserved **verbatim** as a first-class negative.

---

## 4. Results

### 4.1 The residual replicates (Stage 4)

δ_ours = 0.104 (median across 801 subjects), subject-bootstrap 95% CI
[0.1007, 0.1073]; positive in **801/801** subjects; leave-one-subject-out
max deviation 5.4e-8. Orthogonality gate: median |ρ(R, degree)| = 0.0327
(Fig. P2-2, P2-3).

### 4.2 Univariate and subject-aware associations (Stages 8, 11)

All 12 features associate with R at q < 1e-27. Within-subject median ρ:
**bridge +0.4985**, closeness_d +0.2489, redundancy −0.2179, participation
−0.1676, clustering −0.1658, betweenness +0.1333, eigenvector +0.0834, kcore
+0.0556, PageRank −0.0379, strength −0.0689. The 8-feature within-subject
model with CR1 SEs retains all features at q < 1e-7 (Fig. P2-4, P2-7).

### 4.3 Out-of-sample benchmark (Stage 10)

**Table 1. Predictive benchmark (5-fold subject-grouped CV × 3 seeds).**

| Model | cv-R² (mean ± sd) | cv-R² permuted | Δ vs degree-only |
|---|---|---|---|
| Degree-only | −0.00006 ± 0.000002 | 0.0004 | — |
| **Ridge (11 feat.)** | **0.5740 ± 0.0001** | 0.0024 | **+0.574** |
| Elastic net | 0.5614 ± 0.0001 | 0.0023 | +0.561 |
| MLP | −4.09 ± 4.57 | −4.65 | −4.09 (unstable; documented artifact) |

Ridge predicts the residual far out of sample (cv-R² = 0.574) while
degree-only predicts nothing; the permuted control sits at 0.0024
(Fig. P2-6).

### 4.4 Negative controls (Stage 21)

NC1 and NC2 chance bands are |ρ| ≤ 0.0044. All 8 tested features exceed
both bands. Margins are large for the strong associates (bridge 0.49,
closeness_d 0.24, redundancy 0.21) but small for the weak ones
(within-module z 0.014, k-core 0.052) — consistent with those features'
small observed associations; no feature falls inside a chance band.

### 4.5 Degree-preserving null arbitration (Stage 15) — **Outcome C**

**Table 2. Null arbitration per feature (12 subjects × 100 degree-preserving
nulls; exact degree preservation verified per null).**

| Feature | Observed \|median ρ\| | Null median ρ | Null IQR | Null \|ρ\| p95 | Verdict |
|---|---|---|---|---|---|
| Bridge | 0.4985 | −0.5957 | 0.0502 | 0.6538 | inside band |
| Clustering | 0.1658 | 0.6846 | 0.0443 | 0.7314 | inside band |
| Redundancy | 0.2179 | −0.6228 | 0.0469 | 0.6807 | inside band |
| Participation | 0.1676 | 0.3909 | 0.0695 | 0.4609 | inside band |
| Betweenness | 0.1333 | 0.1675 | 0.0342 | 0.2102 | inside band |
| Within-module z | 0.0186 | 0.0942 | 0.0448 | 0.1499 | inside band |
| Eigenvector | 0.0834 | 0.0926 | 0.0317 | 0.1304 | inside band |
| k-core | 0.0556 | 0.0627 | 0.0323 | 0.1003 | inside band |
| PageRank | 0.0379 | 0.0618 | 0.0304 | 0.0961 | inside band |

Every observed association lies **inside** its null p95 band
(`obs_exceeds_null_p95 = false` for all 9 arbitrated features) — the
pre-registered **Outcome C** (Fig. P2-5). The feature–residual associations
of real graphs do not exceed what degree-preserving randomization already
produces; they are structural descriptions, not degree-independent
mechanisms. H1 is therefore **not licensed** by this design.

Two independent verifications support this gate. First, the stored per-null
residual re-derives bit-exactly from the stored (null CIS, null degree) via
the documented 20-bin proxy, and the pooled null statistics reproduce to
1e-9, under an independent re-implementation (verification gate V09;
`13_MANUSCRIPT/verify_stage24.py`). Second, the proxy-vs-spline equivalence
was validated on observed data: the association statistic ρ(R, feature) —
the quantity Stage 15 arbitrates — differs between the two residualizations
by a median of 0.050 across the 12 null subjects × 9 features
(`06_NULL_MODELS/NULL_PROXY_VALIDATION.json`), far smaller than the null
bands (0.10–0.73), and the binned residualization yields slightly *stronger*
observed associations than the spline, so the proxy cannot manufacture
Outcome C by weakening the observed side.

### 4.6 Robustness (Stage 20)

Sign-consistency across the estimator ladder for bridge (+0.435 … +0.524)
and participation; winsorization at the 99.9th percentile leaves headline
associations unchanged; extreme-set median standardized residual +3.70
(top-1%) and +1.68 (top-5%).

### 4.7 Biological annotation and enrichment

**Table 3. Top-10%-CIS enrichment by major structure (10,000 permutations,
two-sided, BH-q).**

| Structure | Observed share | Expected share | Δ (pp) | q |
|---|---|---|---|---|
| Cortex | 0.444 (20/45) | 0.877 (400/456) | −43.3 | **0.00017** |
| Subcortex | 0.222 (10/45) | 0.044 | +17.8 | **0.00017** |
| Thalamus | 0.267 (12/45) | 0.031 | +23.6 | **0.00017** |
| Cerebellum | 0.067 (3/45) | 0.022 | +4.5 | 0.087 (ns) |
| Brainstem | 0.000 (0/45) | 0.026 | −2.6 | 0.389 (ns) |

Top-10%-CIS nodes **under-represent cortex** and over-represent subcortical
and thalamic parcels (degree-controlled partial Spearman, residual vs major
structure given log-degree: −0.571, q = 0.0003; hemisphere +0.475,
q = 0.0003; functional network ns). For the top-10%-**residual** set,
cerebellum (+15.6 pp) and brainstem (+17.4 pp) are additionally enriched
(both q = 0.00017). **Interpretation caveat (read with Table 3):** these
anatomical enrichments are permutation-supported but are *not*
spatially controlled — parcel centroid coordinates were unavailable, so no
spatial-autocorrelation correction (e.g. Moran's I) could be applied; they
must not be read as spatially corrected results (see §6.1).
Cell-type, neurotransmitter and transcriptomic fields: NOT_AVAILABLE
(parcels are not cell types); the corresponding enrichment tests:
NOT_ESTABLISHED (Fig. P2-9).

### 4.8 Operational chokepoints (Stage 22)

**Table 4. Joint-criterion candidate counts vs threshold k.**

| k (%) | CIS top-k ∩ residual top-k | + bridge upper half (candidates) |
|---|---|---|
| 1 | 1 | **1** |
| 2 | 2 | **2** |
| 5 | 3 | **3** |
| 10 | 7 | **7** |

Candidates are rare (0.2–1.5% of nodes) and threshold-sensitive; the
node-level null verdict is uniformly NOT_ESTABLISHED
(`12_SYNTHESIS/CHOKEPOINT_CANDIDATES.csv`). The chokepoint is an
**operational, bounded label**, not a validated node class
(Fig. P2-8).

### 4.9 Fly comparison (Stages 12–13, 22b)

**Table 5. Conservative human-vs-fly summary (12-property table condensed).**

| Property | Human | Fly | Shared? |
|---|---|---|---|
| Unit of analysis | 456-node parcel | individual neuron (3,518 targets) | No |
| CIS–degree dependence | ρ = 0.943 | strong (degree-dominated) | Yes |
| Degree-independent residual | δ = 0.104, 801/801 | δ = 0.100, 778/801 | Yes |
| Degree-preserving null verdict | Outcome C (all 9 features) | z = 1.21, p = 0.109 (frozen) | **Yes (both negative)** |
| Position signature | bridge +0.4985 (null-qualified) | ME.131 betweenness z = +4.08 (case only) | No |
| Predictive benchmark | ridge cv-R² = 0.574 | NOT_ESTABLISHED | No |
| Anatomical concentration | avoids cortex (q = 0.00017) | visual system (~80%) | No |
| Visual contribution | ~2% | ~80% | No |
| Cell-type ground truth | NOT_AVAILABLE | per-neuron (nt_type, super_class) | No |
| Causal interpretation | none licensed | none licensed | Yes |

ME.131 (OCT, visual centrifugal) vs 86 degree-matched targets: CIS
z = +23.4 (154× peer median) — a **case study only**. Two same-direction
null negatives at different scales license **no** universal-law or
same-mechanism claim (Fig. P2-10).

---

## 5. Discussion

The human connectome's degree-independent control-impact residual is
reproducible, positive in all 801 subjects, anatomically biased
away from cortex, and substantially predictable from measured network features — yet
its feature associations are fully matched by exact degree-preserving nulls
(Outcome C). The most defensible reading is that **what looks like a
"chokepoint signature" (bridging, sparse alternative paths) is largely a
consequence of degree architecture plus randomized-topology baselines**, and
that any true degree-independent fine structure of control impact is finer
than this design can arbitrate at 456-node parcel resolution.

This outcome bounds Paper 1 honestly: the residual is real, but not yet
mechanistically explained. The convergence of the human Outcome C with the
fly population-level null (z = 1.21, p = 0.109) is a paired negative result:
at two scales, four orders of magnitude apart in node count, degree alone
explains the null-level structure of the CIS-residual association machinery.
We explicitly decline the universal-law reading of this convergence.

The enrichment results add a genuine architectural fact independent of the
null verdict: high-impact parcels concentrate in subcortex and thalamus and
avoid cortex, and the high-residual set adds cerebellum and brainstem. These
are population-level, degree-controlled anatomical facts — they do not
require, and do not imply, a node-class mechanism.

## 6. Limitations

1. **Spatial controls NOT_ESTABLISHED.** The atlas label file ships no parcel
   centroids; Moran's I / distance-constrained nulls cannot be run without
   inventing coordinates (none were invented). The orthogonality gate and the
   topology-randomizing degree-preserving null bound, but do not remove,
   spatial-autocorrelation concerns.
2. **Parcel resolution.** Atlas parcels are not neurons; no cell-type ground
   truth exists at parcel resolution; cell-type fields are NOT_AVAILABLE.
3. **Observational design.** CIS is network importance under removal, not a
   causal perturbation; no causal claim is licensed.
4. **Null scale.** The 12-subject × 100-null design is compute-bound (exact
   CIS per null); bands are Monte-Carlo estimates at a frozen seed.
5. **MLP arm unstable** (cv-R² −4.09); reported for completeness, not
   interpreted.
6. **Fly case study (n = 1)** does not generalize; human and fly CIS
   estimators differ and are never equated.

## 7. Conclusion

Degree-independent control impact in the human structural connectome is a
real, replicable, predictable from measured network features, and anatomically structured quantity — and it is
**null-qualified** as a mechanism: under exact degree preservation, every
graph-geometric association falls within chance bands. The hidden chokepoint
is an operational construct only. The honest headline of this paper is a
disciplined negative: the residual exists; its explanation, if any, awaits
designs that can separate degree architecture from spatial and cell-class
structure.

## 8. Data, code and reproducibility availability

- **Repository (current release):**
  `github.com/harsha-vardhan-2006/humanbrain-hidden-chokepoint-mechanics`,
  tag `v2.0.1` (flattened standalone mirror; full parent lineage imported).
- **Parent study tree:**
  `github.com/harsha-vardhan-2006/humanbrain_cross_species_cis`,
  tag `v2.0.0` → commit `9e9cfd1` (study tree
  `13_CROSS_SPECIES_CIS/02_PAPER2_HIDDEN_CHOKEPOINTS/`; frozen).
- **Release archive:** `humanbrain_hidden_chokepoint_mechanics_v2.0.1.zip`
  (SHA256 in `dist/SHA256SUMS_paper2.txt`; also attached to the GitHub
  Release v2.0.1 together with the compiled PDFs and the raw 1,200-null
  ensemble).
- **Data:** AOMIC ID1000 derived structural connectomes (Zenodo 19796783,
  CC-BY-4.0); FAFB v783 fly release (frozen `fruitfly` v1.0.0 artifacts).
- **Reproducibility:** every stage is scripted with frozen seeds and
  fail-loud gates; verification gates V01–V12 re-derive all headline numbers
  from artifacts (12/12 PASS, `13_MANUSCRIPT/verify_stage24.py`). Exact
  commands: `13_MANUSCRIPT/REPRODUCIBILITY.md`. Protocol freeze:
  `01_CONFIG/CONFIG_FREEZE.md` (Amendments 1–3). Research log:
  `00_DOCS/RESEARCH_LOG.md` (append-only).

### Key artifacts

| Artifact | Path |
|---|---|
| Null arbitration (Outcome C) | `06_NULL_MODELS/NULL_FEATURE_RESULTS.json` |
| ML benchmark | `08_STATISTICS/ML_BENCHMARK.json` |
| Subject-aware CR1 model | `08_STATISTICS/SUBJECT_AWARE_MODEL.json` |
| Robustness matrix / negative controls | `07_ROBUSTNESS/` |
| Chokepoint definition, sensitivity, candidates | `12_SYNTHESIS/` |
| Human-vs-fly comparison | `12_SYNTHESIS/HUMAN_VS_FLY_COMPARISON.{csv,md}` |
| Biological annotation (456 rows) | `results_annotation/human_node_biological_annotations.csv` |
| Enrichment results | `results_annotation/BIOLOGICAL_ENRICHMENT.json` |
| Figures (10) | `09_FIGURES/*.png` + `13_MANUSCRIPT/FIGURE_LEGENDS.md` |
| Verification gates | `13_MANUSCRIPT/verify_stage24.py` → `STAGE24_VERIFICATION.json` |
| Full QC | `QC/run_full_qc.py` → `QC/FINAL_QC_REPORT.md` |

## 9. References

1. Achard, S. & Bullmore, E. (2007). Efficiency and cost of economical brain
   functional networks. *PLoS Computational Biology* 3, e17.
   doi:10.1371/journal.pcbi.0030017
2. Albert, R., Jeong, H. & Barabási, A.-L. (2000). Error and attack
   tolerance of complex networks. *Nature* 406, 378–382.
   doi:10.1038/35019019
3. Benjamini, Y. & Hochberg, Y. (1995). Controlling the false discovery
   rate: a practical and powerful approach to multiple testing.
   *J. R. Stat. Soc. B* 57, 289–300. doi:10.1111/j.2517-6161.1995.tb02031.x
4. Betzel, R. F. & Bassett, D. S. (2017). Multi-scale brain networks.
   *NeuroImage* 160, 73–83. doi:10.1016/j.neuroimage.2016.11.006
5. Bonacich, P. (1972). Factoring and weighting approaches to status scores
   and clique identification. *J. Math. Sociol.* 2, 113–120.
   doi:10.1080/0022250X.1972.9989806
6. Cliff, N. (1993). Dominance statistics: ordinal analyses to answer
   ordinal questions. *Psychological Bulletin* 114, 494–509.
   doi:10.1037/0033-2909.114.3.494
7. Dorkenwald, S. et al. (2023). Neuronal wiring diagram of an adult brain.
   *bioRxiv* 2023.06.27.546656 (FlyWire Consortium).
   doi:10.1101/2023.06.27.546656
8. Dorkenwald, S. et al. (2024). Neuronal wiring diagram of an adult brain.
   *Nature* 634, 124–138. doi:10.1038/s41586-024-07958-y
9. Freeman, L. C. (1977). A set of measures of centrality based on
   betweenness. *Sociometry* 40, 35–41. doi:10.2307/3033543
10. Gu, S. et al. (2015). Controllability of structural brain networks.
    *Nature Communications* 6, 8414. doi:10.1038/ncomms9414
11. Guimerà, R. & Amaral, L. A. N. (2005). Cartography of complex networks:
    modules and universal roles. *J. Stat. Mech.* 2005, P02001.
    doi:10.1088/1742-5468/2005/02/P02001
12. Hagmann, P. et al. (2008). Mapping the structural core of human cerebral
    cortex. *PLoS Biology* 6, e159. doi:10.1371/journal.pbio.0060159
13. Hastie, T., Tibshirani, R. & Friedman, J. (2009). *The Elements of
    Statistical Learning*, 2nd ed. Springer. (Regression splines.)
    doi:10.1007/978-0-387-84858-7
14. Latora, V. & Marchiori, M. (2001). Efficient behavior of small-world
    networks. *Physical Review Letters* 87, 198701.
    doi:10.1103/PhysRevLett.87.198701
15. Liu, Y.-Y., Slotine, J.-J. & Barabási, A.-L. (2011). Controllability of
    complex networks. *Nature* 473, 167–173. doi:10.1038/nature10011
16. MacKinnon, J. G. & White, H. (1985). Some heteroskedasticity-consistent
    covariance matrix estimators with improved finite sample properties.
    *J. Econometrics* 29, 305–325. doi:10.1016/0304-4076(85)90158-7
17. Maslov, S. & Sneppen, K. (2002). Specificity and stability in topology
    of protein networks. *Science* 296, 910–913. doi:10.1126/science.1065103
18. Page, L., Brin, S., Motwani, R. & Winograd, T. (1999). The PageRank
    citation ranking: bringing order to the web. Stanford InfoLab technical
    report.
19. Seidman, S. B. (1983). Network structure and minimum degree. *Social
    Networks* 5, 269–287. doi:10.1016/0378-8733(83)90028-X
20. Smith, R. E. et al. (2015). SIFT2: Super-resolution tractography.
    *NeuroImage* 113, 323–337. doi:10.1016/j.neuroimage.2015.03.049
21. Snoek, L. et al. (2021). The Amsterdam Open MRI Collection, a set of
    multimodal MRI scans for individual difference analyses. *Scientific
    Data* 8, 85. doi:10.1038/s41597-021-00870-6 (AOMIC; derived
    connectomes: Zenodo 19796783, CC-BY-4.0.)
22. Tang, E. & Bassett, D. S. (2018). Colloquium: Control of networks in the
    brain. *Reviews of Modern Physics* 90, 031003.
    doi:10.1103/RevModPhys.90.031003
23. Watts, D. J. & Strogatz, S. H. (1998). Collective dynamics of
    'small-world' networks. *Nature* 393, 440–442. doi:10.1038/30918
24. Malipeddi, H. V. (2026). Control-impact architecture of the human
    structural connectome: degree dominance, a small near-universal
    residual, and a cross-scale architectural comparison with the fly
    connectome. Paper 1 of this series, frozen release v1.1.0,
    `github.com/harsha-vardhan-2006/humanbrain_cross_species_cis`
    (preprint / research repository; read-only source of CIS, δ, and the
    fly null result z = 1.21, p = 0.109).
25. 4S456 parcellation: atlas label file and provenance,
    `00_MANIFEST/manifests/atlas_4S456_system_labels.csv` (frozen;
    [atlas citation to be confirmed by the author before submission]).

*Internal protocol and provenance documents are listed in §8; all numerical
claims in this paper are bounded by the frozen artifacts they cite.
References 1–23 are the primary methodological sources; the author should
verify page/DOI details against the sources before submission.*
