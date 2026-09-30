"""Write the Paper-2 documentation set (docs stage).

Creates, in 00_DOCS/ (study tree convention inherited from the parent repo):
  BIOLOGICAL_ANNOTATION_SOURCES.md
  ROBUSTNESS_REPORT.md
  SYNTHESIS_SUMMARY.md          (spatial control status + master verdict)
And appends the P2-01 research-log entry (append-only).
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

TREE = Path(__file__).resolve().parents[1]
DOCS = TREE / "00_DOCS"

# ---------------------------------------------------------------- sources
SOURCES_MD = """# Biological annotation sources (Paper 2 / human)

Evidence discipline: every field in
`results_annotation/human_node_biological_annotations.csv` is traceable to a
source below. Anything not derivable is `NOT_AVAILABLE`; anything not
testable in this dataset is `NOT_ESTABLISHED`. A macroscopic atlas parcel is
NEITHER an individual neuron NOR a cell type.

## S1 - Node identity / atlas labels

- **Dataset:** AOMIC ID1000 derived connectomes, Zenodo record 19796783
  (CC-BY-4.0), `atlas_4S456Parcels` parcellation.
- **Evidence used:** region-label field extracted 2026-09-23 from
  `connectomes_part_1.zip` (field `atlas_4S456Parcels_region_labels`),
  frozen at `00_MANIFEST/manifests/atlas_4S456_system_labels.csv`
  (+ PROVENANCE sidecar).
- **Mapping:** node_id -> parcel label (direct, 1:1). Cortical labels carry
  Yeo-7 network prefixes (Yeo et al. 2011, 7-network scheme as embedded in
  the labels); subcortical/cerebellar labels are standard abbreviations
  expanded only where unambiguous (e.g. `Pu` -> Putamen); ambiguous forms
  remain UNKNOWN.
- **Confidence:** HIGH for label identity (direct); MAPPED_HIGH_CONFIDENCE
  for hemisphere/lobe/system derived from the labels.
- **Limitations:** the atlas ships no parcel centroids -> MNI x/y/z are
  NOT_AVAILABLE (no invented coordinates); no layer information -> cortical
  layer NOT_AVAILABLE.

## S2 - Functional network assignment

- **Source:** Yeo-7 prefixes on cortical labels (as in S1); subcortical /
  cerebellar parcels -> `subcortical` / `cerebellar` functional tags.
- **Method:** direct prefix mapping, no re-estimation.
- **Limitations:** Yeo-7 is a cortical scheme; subcortical tags are
  structural, not functional-parcellation assignments.

## S3 - Cell class / neuronal class / neurotransmitter / transcriptomics

- **Status:** NOT_AVAILABLE for all 456 parcels.
- **Reason:** the dataset contains no single-cell or histological ground
  truth at parcel resolution; a parcel-level majority cell class cannot be
  established from connectivity. Enrichment tests against these fields are
  therefore NOT_ESTABLISHED (reported as such in
  `results_annotation/BIOLOGICAL_ENRICHMENT.json`).
- **Species discipline:** no mouse/macaque cell-type transfer was applied.
  External atlases (Allen HBA, HPA) were NOT integrated because no
  parcel-level mapping without invented coordinates could be defended.

## S4 - Cell-type annotation on the fly side (comparison only)

- **Source:** frozen `fruitfly` v1.0.0 release tables (`e07_annotated`:
  `nt_type`, `super_class` per neuron).
- **Use:** fly-side descriptive annotation ONLY; never mapped onto human
  parcels; never presented as human cell-type evidence.
"""

# ------------------------------------------------------------- robustness
rb = pd.read_csv(TREE / "07_ROBUSTNESS" / "ROBUSTNESS_MATRIX.csv")
n_r1 = int((rb["analysis"] == "R1_estimator").sum())
n_r2 = int((rb["analysis"] == "R2_threshold").sum())
n_r5 = int((rb["analysis"] == "R5_winsorized_R").sum())
sign_ok = {
    "bridge": True, "participation": True,
}
ROB_MD = f"""# Robustness report (Paper 2)

Families (Stage 20, frozen seeds; matrix: `07_ROBUSTNESS/ROBUSTNESS_MATRIX.csv`):

- **R1 estimator ladder** ({n_r1} rows): linear-OLS and df=3 spline vs the
  primary df=4 spline, and 20-bin quantile proxy. Bridge and participation
  associations keep sign across all estimators; magnitudes vary
  (bridge +0.435..+0.524; participation -0.115..-0.346), consistent with the
  pre-registered coupling-risk flag for path-length metrics.
- **R2 extreme-threshold sensitivity** ({n_r2} rows): median standardized
  residual +3.70 (top-1%) and +1.68 (top-5%) - monotone with threshold, as
  expected for an upper-tail effect.
- **R5 winsorized residual** ({n_r5} rows): all headline associations
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
"""

# -------------------------------------------------------------- synthesis
SYN_MD = """# Synthesis summary - Paper 2 (Hidden Chokepoints)

## Master verdict (numbers on disk; framing bounded accordingly)

1. **Residual exists and is degree-independent.** delta = 0.104
   (801/801 subjects > 0; bootstrap CI [0.1007, 0.1073]); orthogonality
   gate median |rho(R, degree)| = 0.0327. Freeze-1 + V01-V12 all PASS.
2. **Network position predicts the residual out-of-sample.** Ridge on 11
   features: cv-R2 = 0.574 (subject-grouped CV, 3 seeds) vs degree-only
   ~ 0; within-subject permutation control 0.0024. Strongest univariate
   associates (within-subject median rho): bridge +0.4985, closeness_d
   +0.2489, redundancy -0.2179, participation -0.1676, clustering -0.1658.
3. **The mechanism does NOT survive its degree-preserving null.**
   Stage 15 (12 x 100 nulls, exact degree preservation, full CIS +
   feature recomputation per null): every feature's observed |median rho|
   lies inside the null p95 band (Outcome C). The Stage-8/11 associations
   characterize real-graph structure; they are not licensed as
   degree-independent mechanisms.
4. **Chokepoint label is operational only.** Joint-criterion candidates
   (CIS top-k AND residual top-k AND upper-half bridge): 1 node at k = 1%,
   3 at 5%, 7 at 10%. Per-node null arbitration: NOT_ESTABLISHED.
5. **Biology.** Top-CIS nodes significantly UNDER-represent cortex
   (top-10% share 0.44 vs expected 0.88; permutation q < 0.001). All
   cell-type fields NOT_AVAILABLE (parcels are not cell types); cell-type
   enrichment NOT_ESTABLISHED.
6. **Fly comparison.** Fly null verdict preserved (z = 1.21, p = 0.109,
   negative). Human Stage-15 is a same-direction negative at a different
   scale. Shared: degree dominance + small positive residual. Not shared:
   anatomy (visual 2% vs 80%), unit scale, cell-type ground truth.
   No universal-law or same-mechanism claim.

## Spatial control status

MNI centroids are absent from the frozen manifests; the atlas label file
ships names only. Therefore Moran's I / distance-constrained nulls are
**NOT_ESTABLISHED** for this dataset version - recorded rather than
approximated. Risk acknowledged: system-label associations could partially
reflect spatial autocorrelation; the residual itself is defined on graph
structure and the degree-preserving null (which randomizes topology while
preserving degrees, i.e. scrambles spatial clustering) bounds rather than
removes this concern. Any spatial claim requires parcel centroids in a
future protocol.

## What this paper does NOT claim

- No causal claim (observational connectomes; no perturbation).
- No universal mechanism claim (two same-direction null negatives).
- No cell-type claim at parcel resolution.
- No per-node chokepoint claim beyond the operational, null-qualified
  candidate list.
"""

(DOCS / "BIOLOGICAL_ANNOTATION_SOURCES.md").write_text(SOURCES_MD + "\n")
(DOCS / "ROBUSTNESS_REPORT.md").write_text(ROB_MD + "\n")
(DOCS / "SYNTHESIS_SUMMARY.md").write_text(SYN_MD + "\n")

# ------------------------------------------------- research log append-only
LOG = DOCS / "RESEARCH_LOG.md"
entry = """
---

## P2-01 — Stages 6–24 completion (2026-09-30)

```
Date:       2026-09-30
Scope:      downstream chain completion (Stages 6-24) + synthesis + docs.
Stage 6:    feature matrix 801x456 x 12 features (Amendment-3 redundancy
            repair verified in-chain: max|diff| vs clustering > 0).
Stages 7-9: feature QC, univariate (12 features, all q < 1e-27; bridge
            strongest rho = +0.4985), nested models (M4 cvR2 = 0.294 vs
            M1 ~ 0; closeness_d/redundancy/bridge best M3 adds).
Stage 10:   ML benchmark - ridge cvR2 = 0.5740 vs degree_only ~ 0;
            permuted-R control 0.0024. MLP arm unstable (cvR2 -4.09 +- 4.57,
            documented benchmark artifact; numpy-native SGD, not a
            mechanism claim). FIX during run: mlp_fit backward pass
            err @ W2 -> np.outer(err, W2) (shape bug; pre-result, no
            numbers consumed before the fix).
Stage 11:   subject-aware within-subject model, CR1 SEs: all 8 features
            q < 1e-7 (bridge t = 109.2; clustering t = 56.3).
Stage 15:   degree-preserving nulls COMPLETE 1200/1200 (12 subjects x 100,
            seed 20270927, exact degree verification per null, full CIS +
            9-feature recomputation per null). VERDICT: Outcome C - all 9
            observed |median rho| INSIDE null p95 bands
            (bridge obs +0.4985 vs null p95 0.6538; clustering obs
            -0.1658 vs null p95 0.7314; etc.). Null machinery is WIDE:
            degree-preserving rewiring alone generates rho magnitudes
            comparable to the observed ones.
Stage 20:   robustness matrix (R1/R2/R5) - sign-consistent bridge/
            participation; winsorization-invariant headline associations.
Stage 21:   negative controls NC1/NC2 - observed exceeds bands, margins
            >= 0.13 for all features.
Stage 12-13: fly case study - ME.131 vs 86 degree-matched peers:
            CIS z = +23.4 (154x peer median), directed betweenness
            (sampled k=512, frozen seed) z = +4.08; case-study bounds
            preserved. FIX during run: to_markdown -> to_string
            (missing optional dep 'tabulate'; formatting only).
Stage 22:   chokepoint operationalization + sensitivity (1/2/3/7 joint-
            criterion candidates at 1/2/5/10%) + human-vs-fly comparison
            table (12 properties; fly z=1.21 p=0.109 negative preserved).
Stage 24:   independent verification V01-V12: 12/12 PASS.
Spatial:    Moran's I / distance nulls NOT_ESTABLISHED (no parcel
            centroids in frozen manifests) - recorded, not approximated.
Data protection: Paper 1 + fly artifacts read-only; frozen outputs
            untouched; nulls checkpointed JSONL (resume-safe).
Next step:  figures + manuscript package + QC + release (P2-02).
Verdict:    residual real and learnable; mechanism claim NULL-QUALIFIED
            (Outcome C); chokepoint = operational label only.
```
"""
with open(LOG, "a") as f:
    f.write(entry)
print("docs written: BIOLOGICAL_ANNOTATION_SOURCES, ROBUSTNESS_REPORT, SYNTHESIS_SUMMARY; log P2-01 appended")
