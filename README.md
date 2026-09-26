# HumanBrain Cross-Species CIS

**Cross-scale control-impact study: human structural connectomes (AOMIC-ID1000)
vs the Drosophila connectome (FAFB v783).**

**Status: frozen scientific result; publication-ready release v1.1.0
(2026-09-26).** The analysis is complete and frozen; reviewer-requested
analyses, if any, will be added only as clearly labeled post-hoc/secondary
analyses — never by modifying the pre-registered primary results. Code is
licensed MIT (`LICENSE`).

## Research Paper (published in this repository)

The final journal-style research paper is typeset, compiled, and committed
here:

- **Paper (PDF):** [`13_CROSS_SPECIES_CIS/SUBMISSION_PACKAGE/FINAL_MANUSCRIPT/main.pdf`](13_CROSS_SPECIES_CIS/SUBMISSION_PACKAGE/FINAL_MANUSCRIPT/main.pdf)
  — *“Control-impact architecture of the human structural connectome:
  degree dominance, a small near-universal residual, and a cross-scale
  architectural comparison with the fly connectome”* (12 pp;
  Harsha Vardhan Malipeddi, Independent Researcher).
- **Supplementary material (PDF):** [`13_CROSS_SPECIES_CIS/SUBMISSION_PACKAGE/SUPPLEMENTARY/supplementary.pdf`](13_CROSS_SPECIES_CIS/SUBMISSION_PACKAGE/SUPPLEMENTARY/supplementary.pdf)
  (S1–S14 equivalents; 5 pp).
- **LaTeX source:** `FINAL_MANUSCRIPT/main.tex` + `references.bib`,
  auto-generated booktabs tables (`tables/`), and vector figures
  (`figures/`). Rebuild: `tectonic main.tex` (see
  [`SUBMISSION_PACKAGE/README.md`](13_CROSS_SPECIES_CIS/SUBMISSION_PACKAGE/README.md)).
- **QC:** all 17 pages programmatically inspected; zero placeholders,
  zero unresolved references; every frozen number verified in the
  typeset PDFs (`FINAL_PAPER_QC_REPORT.md` in the package root).

The paper is a faithful presentation of the frozen results below — it adds
no new analysis and makes no claims beyond those documented here.

## Research Question

Can removal-based Control Impact Score (CIS) identify structurally
influential nodes in human structural connectomes, and does the resulting
architecture show a comparable pattern across biological scales?

## Hypotheses

Pre-registered in
`13_CROSS_SPECIES_CIS/00_MANIFEST/PROTOCOL_FREEZE.md` before any
computation:

- **H1.** Top-50 CIS concentration exceeds degree-preserving null
  expectations in individual subjects.
- **H2.** A degree-independent residual of control impact remains after
  explicit degree/strength adjustment.
- **H3.** The residual is robustly system-specific (canonical brain
  systems).
- **H4.** A comparable architecture appears at the fly connectome scale.

## Scientific Contribution

The individual components are established methods (node-removal efficiency
analysis, cost thresholding, matched controls, configuration-model nulls,
FDR, cross-species connectomics). The contribution is the **integrated
framework** — per-node removal CIS + population-scale per-subject computation
+ explicit degree/strength-controlled residualization + degree-preserving
null-model arbitration + FDR-controlled residual inference +
robustness/rank-stability analysis + a pre-specified cross-species comparison
with Drosophila — and the resulting cross-scale empirical comparison.
To our knowledge, no prior study has combined these analyses in a
per-subject population-scale human structural-connectome framework with a
cross-scale comparison. Full audit:
`13_CROSS_SPECIES_CIS/10_REPORT/NOVELTY_AUDIT.md`; claim-by-claim evidence:
`13_CROSS_SPECIES_CIS/CLAIM_EVIDENCE_MATRIX.md`.

## Core Method

### Control Impact Score

For each subject's undirected graph G, global efficiency is
E(G) = mean over node pairs of the inverse shortest-path length. The Control
Impact Score of node i is

    CIS(i) = (E(G) − E(G−i)) / E(G)

computed **exactly** by removing node i and recomputing global efficiency on
the remaining graph — for all 456 nodes in every subject (reference
implementation validated to 6.1e-16; fast estimator used only for null
graphs, gated at 1e-9). CIS is a unitless fraction of baseline efficiency
lost: **higher CIS = a structurally more influential node**. Graphs are
thresholded at 15% connection cost (k = 15,561 edges) on SIFT streamline
counts (4S456 parcellation).

### Degree/Strength Control

Node importance is degree-confounded, so raw CIS comparisons are never
interpreted directly. Each node is matched to controls within ±10% total
degree (1:1 greedy; nearest-50 fallback, flagged), with strength association
reported separately (ρ = 0.486). The **degree-independent residual** is the
CIS advantage of each node over its degree-matched controls; it is analyzed
per subject and across the population.

### Degree-Preserving Nulls

Maslov–Sneppen rewiring preserves each graph's **exact per-node degree
sequence** (verified per null: 10,000/10,000 exact, 0 self-loops; seeds
100+i). Two batteries arbitrate every headline claim: battery A (100
subjects × 100 nulls, full-CIS) and battery B (200 subjects × 100 nulls,
top-50 concentration). Subject samples are nested under one RNG (seed
20260922).

### Population Analysis

801 QC-pass subjects of 900 acquired (frozen, CIS-blind flags — retained,
never deleted). Per-node empirical p (add-one) → Stouffer combination →
BH-FDR (q < .05, 456 tests); population sign tests; effect sizes as Cliff's
δ; rank stability over 100 half-splits (median Spearman 0.996).

### Cross-Species Analysis

The human study is compared with the frozen fly (FAFB v783) study using
**normalized comparators only** (effect size δ, enrichment z_B,
concentration shares), per explicit discipline tags (DIRECT/NORMALIZED/
QUALITATIVE). Human and fly nodes are not treated as homologous structures;
the comparison operates at the level of network architecture and statistical
organization. Absolute CIS values are never compared across species
(different units, graphs, and designs).

## Data

### Human

AOMIC-ID1000 structural connectomes — Zenodo record **19796783**
(CC-BY-4.0), 900 subjects × 7 atlases; the 4S456 connectome derivative is
used. Byte-exact local verification against the Zenodo API
(`00_Metadata/AOMIC_VERIFICATION_REPORT.md`, `CHECKSUMS_AOMIC.sha256`).
Raw zips are **not redistributed** in this repository.

### Fly

Frozen result artifacts of the fly study on FAFB v783 (139,255 neurons,
FlyWire release, CC BY-NC 4.0) — read-only, release v1.0.0 of the companion
project. No fly raw data are redistributed.

## Results

### Human Results

- **Degree dominance.** CIS is strongly associated with degree (median
  Spearman ρ = 0.943; 801 QC-pass subjects; 456-node atlas).
- **Concentration beyond nulls (H1 supported).** Top-50 CIS concentration
  exceeds degree-preserving null expectations in **200/200** tested subjects
  (median z = 16.36; sign p = 1.24 × 10⁻⁶⁰; 100% of subjects at the 1/101
  empirical-p floor — inference via z + sign test).
- **Degree-independent residual (H2 supported).** Detectable in **778/801**
  subjects (Cliff's δ = 0.100 [0.078–0.129]; sign p = 2.6 × 10⁻¹⁹⁷;
  36,846 matched pairs); **43/456** nodes survive BH-FDR q < .05 (max
  Stouffer z = 23.30).
- **Not system-specific (H3 NOT supported).** The pre-registered
  system-enrichment gate was **negative**: visual systems hold only 2% of
  the top-50, and the single nominal signal (Subcortical/Cerebellar, z_B =
  2.08, p = .031, 1.25×) is degree-anchored and absent at K = 25.
- **Robustness (descriptive).** 9 atlas/weight/cost configurations reproduce
  the primary architecture; max like-for-like top-50-mean deviation 0.00262
  (atlas_AAL116; no numeric tolerance was pre-registered — see E06 note in
  `13_CROSS_SPECIES_CIS/10_REPORT/RESOLUTION.md`).

### Fly Results

- Visual-centrifugal enrichment **2.63×** after degree matching
  (z = 5.30, p ≈ 1 × 10⁻⁴); 13/50 top nodes beat matched peers.
- **GABA-specific hypothesis REJECTED**: the raw matched-pair effect did not
  survive degree-preserving nulls (p_delta = 0.109; p_median = 0.782;
  z = 1.21).
- Fly residual δ = **0.0979** did **not** survive its null test (p = 0.109)
  — reported as such.

### Cross-Species Results

A qualitatively similar two-component organization appears at both scales
(human δ = 0.100; fly δ = 0.0979) across a ~10³-fold node-count difference,
while the residual's anatomical identity diverges: human 2% visual vs fly
80% visual-centrifugal.

## Key Interpretation

**"Architecture replicates; anatomy does not."** A dominant
connectivity-dependent component plus a smaller degree-independent residual
recurs across scales; the anatomical identity of the residual does not.
This is an architectural, hypothesis-generating observation.

## What This Study Does NOT Claim

- No anatomical homology (explicit no-homology rules CP03/CP05).
- No functional equivalence.
- No causal mechanism.
- No universal law.
- No one-to-one human/fly anatomical correspondence — human and fly nodes
  are not treated as homologous structures; the comparison is at the level
  of network architecture and statistical organization.

## Reproducibility

An independent stdlib-only audit recomputes every headline number from the
frozen artifacts: `python 13_CROSS_SPECIES_CIS/10_REPORT/verify_final_numbers.py`
→ **46/46 PASS** (2026-09-26). Full pipeline map with exact commands, seeds,
parameters, and runtimes: `13_CROSS_SPECIES_CIS/REPRODUCIBILITY.md`; frozen
parameters: `13_CROSS_SPECIES_CIS/10_REPORT/ANALYSIS_FREEZE.md`; append-only
decision log: `13_CROSS_SPECIES_CIS/RESEARCH_LOG.md`. No unexplained
discrepancy exists anywhere in the tree.

## Data Provenance

- AOMIC raw zips: SHA256-verified (10/10) —
  `00_Metadata/CHECKSUMS_AOMIC.sha256`, `AOMIC_VERIFICATION_REPORT.md`.
- Release archive `dist/cross_species_cis_v1.0.0.zip` with
  `dist/SHA256SUMS_cross_species_cis.txt`.
- Cross-acquisition provenance (BigBrain/FAFB/AOMIC):
  `00_Metadata/ACQUISITION_REPORT.md`, `INTEGRITY_REPORT.md`,
  `cross_species_manifest.*`, `NOT_ACQUIRED.md`, `dataset_catalog.md`.

## Raw Data Protection

RAW data are never modified, moved, or committed: the AOMIC raw zips under
`12_HumanConnectome_AOMIC/zenodo_19796783_raw/` are READ-FOREVER; the fly
dataset (G:\fruitfly) is READ-ONLY; no `.nii`, `.mat`, `.h5`, or raw `.zip`
payloads are tracked in git (whitelist `.gitignore`). Conversions happen
only under the derived trees; failed/suspicious files go to quarantine,
never deleted.

## Figures and Tables

Figures: `13_CROSS_SPECIES_CIS/08_FIGURES/` (fig01–fig09, incl.
`fig05_fdr_anatomical`) with publication captions in
`08_FIGURES/FIGURE_CAPTIONS.md` and per-figure provenance in
`10_REPORT/FIGURE_PROVENANCE.md` (all rendered from frozen artifacts; none
manually edited). Tables: `13_CROSS_SPECIES_CIS/09_TABLES/`
(table_01–table_10; table_09_cross_scale.csv lives in
`07_CROSS_SCALE/`).

## Manuscript

**Final research paper (typeset):**
`13_CROSS_SPECIES_CIS/SUBMISSION_PACKAGE/FINAL_MANUSCRIPT/` — `main.pdf`
(compiled, QC-checked) with full LaTeX source (`main.tex`,
`references.bib`, generated `tables/`, vector `figures/`) and
`../SUPPLEMENTARY/supplementary.pdf`. Package guide:
`SUBMISSION_PACKAGE/README.md`.

Provenance Markdown (frozen v2.0 source of the paper's content):
`13_CROSS_SPECIES_CIS/10_REPORT/MANUSCRIPT_FINAL.md` (author block, CRediT,
COI, ethics, references) — identical copy in
`13_CROSS_SPECIES_CIS/SUBMISSION_PACKAGE/manuscript.md`, with rendered
PDF/DOCX in `SUBMISSION_PACKAGE/rendered/` and the full submission package
(cover letter, highlights, statements) in `SUBMISSION_PACKAGE/`.

## Supplementary Material

`13_CROSS_SPECIES_CIS/10_REPORT/SUPPLEMENTARY_MATERIAL.md` (S1–S14; rendered
PDF/DOCX in `SUBMISSION_PACKAGE/rendered/`).

## Limitations

Undirected graphs only (directed variant impossible in these derivatives);
single pipeline/acquisition site; residual is near the CIS noise floor
(hence null arbitration); battery-B per-subject p-values sit at the 1/101
null-resolution floor (inference via z + population sign test); the
subcortical residual is not robust across the pre-registered K ladder; the
original `ENVIRONMENT_MANIFEST` provenance gap is disclosed (versions
reconstructed from logs); Kudriavtsev 2026 full text was verified via
proxy extraction (direct access blocked). No homology, mechanism, or
scale-invariance claims are made anywhere.

## License

Repository code and documentation: **MIT** (`LICENSE`). Third-party data
keep their own terms: AOMIC-ID1000 CC-BY-4.0; FAFB v783 CC BY-NC 4.0;
BigBrain 2015 CC BY-NC-SA 4.0 (text archived at
`00_Metadata/BigBrain_License.txt`).

## Citation

If you use this work, cite the study and the underlying datasets:

```bibtex
@misc{malipeddi2026crossspeciescis,
  author       = {Malipeddi, Harsha Vardhan},
  title        = {Control-impact architecture of the human structural
                  connectome: degree dominance, a small near-universal
                  residual, and a cross-scale architectural comparison with
                  the fly connectome},
  year         = {2026},
  howpublished = {github.com/harsha-vardhan-2006/humanbrain_cross_species_cis},
  note         = {Release v1.1.0; frozen analysis; all numbers trace to
                  archived artifacts. Typeset paper:
                  13_CROSS_SPECIES_CIS/SUBMISSION_PACKAGE/
                  FINAL_MANUSCRIPT/main.pdf}
}
```

Datasets: Snoek et al. 2021, *Scientific Data* 8:85 (AOMIC-ID1000;
doi:10.1038/s41597-021-00870-6, Zenodo 19796783) and the FlyWire FAFB v783
release (CC BY-NC 4.0).

---

# Acquisition workspace (original documentation, retained)

*(The sections below are the original acquisition-workspace documentation.
They are retained unchanged: the study tree `13_CROSS_SPECIES_CIS/` depends
on these datasets and protection rules.)*

## Workspace safety policy

Safety policy (binding for all tooling in this workspace):
- G: is strictly READ-ONLY. Nothing may be written, moved, or deleted there.
  (Verified: G:\fruitfly untouched at 261 files / 17,521,318,473 bytes throughout.)
- No deletes anywhere. Suspicious/failed files go to *_QUARANTINE folders only.
- RAW data untouched; conversions only under 11_DERIVED (D:) or 05_DERIVED (F:).
- Disk rule: stop downloads if a drive falls below 15 GB free (enforced in downloader).

## Layout
- D:\HumanBrain\00_Metadata  manifests, checksums, license, reports, download lists
- D:\HumanBrain\01..09       BigBrain 2015 core data (volumes, classified, MRI, surfaces, ROIs,
                             layers, hippocampus, parcellations, BigBrainWarp)
- D:\HumanBrain\10_MSM_2023  EMPTY (BigBrain1_MSM_2023.tar is access-denied anonymously; see
                             00_Metadata\NOT_ACQUIRED.md)
- D:\HumanBrain\11_DERIVED   derived products only (never touch RAW)
- D:\HumanBrain\12_HumanConnectome_AOMIC  AOMIC-ID1000 structural connectomes
                             (Zenodo 19796783, CC-BY-4.0; 10 zips / 6.58 GiB / 900
                             subjects × 7 atlases) — downloaded 2026-09-20, verified
                             2026-09-22 (CHECKSUMS_AOMIC.sha256 +
                             AOMIC_VERIFICATION_REPORT.md)
- D:\HumanBrain\13_CROSS_SPECIES_CIS  cross-scale CIS study tree (STUDY_DESIGN.md;
                             RAW zips in 12_ stay READ-FOREVER)
- F:\HumanBrain\01_Histology 7404 coronal full-resolution PNG sections (64.1 GB)
- F:\HumanBrain\00_Metadata\remote_listings  52 official FTP directory listing snapshots
- G:\humanbrain\full18       5 pre-existing full8 volumes (EXISTING_LOCAL; verified, credited)
- G:\fruitfly                FAFB v783 fly dataset (READ-ONLY reference; CC BY-NC 4.0)

## Acquisition tooling

All acquisition tooling is under D:\HumanBrain\99_Logs (downloaders, probes,
verifiers, report generators). Re-running any script is safe: downloads
resume, verification re-runs, reports regenerate.
