# Hidden Chokepoints — Degree-Independent Control Impact in the Human Structural Connectome

**Paper 2 of the cross-species control-impact series (CIS).**
Harsha Vardhan Malipeddi. Frozen release **v2.0.1** (2026-09-30).

## Research question

After accounting for connectivity (degree/strength), do graph-geometric
properties explain node-level variation in removal-based control impact
(CIS) in the human structural connectome — and do any nodes qualify as
operationally defined "hidden chokepoints"?

## Main result

> **A degree-independent CIS residual replicates across all 801 QC-pass
> subjects and is predictable from measured network features — but none of
> the observed feature–residual associations survives exact
> degree-preserving null arbitration. The proposed graph-geometric
> mechanism is therefore NOT established by this study (pre-registered
> Outcome C).**

## What we found

- The residual is **real and replicated**: δ = 0.104, positive in
  **801/801** subjects, CI [0.1007, 0.1073].
- It is **predictable out-of-sample** from measured network features:
  ridge cv-R² = 0.574 (degree-only ≈ 0; permuted-R control 0.0024).
  This is a predictive statement, **not** a mechanism claim.
- Strongest associate: bridge score (within-subject median
  ρ = +0.4985), then closeness (+0.249), redundancy (−0.218),
  participation (−0.168).
- **Outcome C (central negative):** under 1,200 exact degree-preserving
  nulls (12 subjects × 100, seed 20270927, per-null full CIS + feature
  recomputation), *every* observed association lies **inside** its null
  p95 band. Independently deep-verified from the raw null records
  (verification gate V09): degree preservation exact, stored null
  residuals re-derive bit-exactly, null statistics reproduce to 1e-9.
- Biology: top-10%-CIS nodes **under-represent cortex** (0.444 vs 0.877,
  q = 0.00017) and over-represent subcortex/thalamus — permutation-
  supported but **not spatially controlled** (no parcel centroids
  available).

## What we did NOT establish

- **No mechanism.** The graph-geometric "chokepoint signature" is matched
  by degree-preserving randomization; H1 is not licensed.
- **No validated node class.** "Hidden chokepoints" are an operational
  label only: 1/2/3/7 joint-criterion candidates at k = 1/2/5/10%;
  node-level null verdict NOT_ESTABLISHED.
- **No spatial controls** (parcel centroids unavailable — none invented);
  enrichment results are not spatially corrected.
- **No cell-type claims** (parcels ≠ neurons; fields NOT_AVAILABLE).
- **No universal law.** The fly residual also fails its degree-preserving
  null (z = 1.21, p = 0.109, frozen, preserved verbatim); two
  same-direction negatives at different scales license no
  universal-mechanism claim.
- **No causal claims** (observational connectome data throughout).

## Data

| Source | Role | License/identifier |
|---|---|---|
| AOMIC ID1000 derived structural connectomes (Snoek et al. 2021) | human CIS, 801 × 456 (read-only) | CC-BY-4.0; Zenodo 19796783 |
| 4S456 parcellation | node identity (frozen labels) | see `data/node_atlas_mapping.csv` |
| FAFB v783 fly connectome (Dorkenwald et al. 2024) | cross-scale comparison (read-only) | frozen `fruitfly` v1.0.0 release |

Raw imaging data are **not redistributed**; derived summary artifacts are
tracked here. The raw 1,200-record null ensemble
(`06_NULL_MODELS/null_records_checkpoint.jsonl`, 117 MB) is gitignored for
size and shipped in the release archive + checksummed.

## Reproducibility

```bash
pip install -r requirements.txt
python run_all.py --verify          # V01-V12 independent verification (deep)
python run_all.py --qc              # full QC sweep
```

Every stage is scripted with frozen seeds and fail-loud gates.
`13_MANUSCRIPT/REPRODUCIBILITY.md` has exact commands;
`01_CONFIG/CONFIG_FREEZE.md` is the frozen protocol (Amendments 1–3 +
STUDY FREEZE). The manuscript is
`13_MANUSCRIPT/RESEARCH_PAPER.md` (+ `SUBMISSION/` package).

## Repository structure

| Path | Contents |
|---|---|
| `00_DOCS/`, `01_CONFIG/` | frozen protocol, research question/log, mathematical framework |
| `03_`–`08_` | features, degree control, mechanism, null models, robustness, statistics |
| `06_NULL_MODELS/validate_null_proxy.py` | null-estimator equivalence validation |
| `09_FIGURES/`, `10_TABLES/` | 10 figures, auto-generated tables |
| `11_CASE_STUDIES/`, `12_SYNTHESIS/` | fly ME.131 case; chokepoint definition + human-vs-fly |
| `13_MANUSCRIPT/` | manuscript + `SUBMISSION/` (LaTeX/PDF, supplementary) + verification gates |
| `QC/`, `AUDIT/` | full QC; phase-0 baseline |
| `results_annotation/`, `data/` | 456-node annotations + enrichment; atlas mapping |
| `dist/` | release checksum manifest |

## Frozen release

Tag `v2.0.1` (this repository). Parent lineage:
`humanbrain_cross_species_cis` v2.0.0 + freeze commit `5ee7ecc`
(see `PROVENANCE.md`). Release archive:
`humanbrain_hidden_chokepoint_mechanics_v2.0.0.zip`
(SHA256 in `dist/SHA256SUMS_paper2.txt`).

## Citation

See `CITATION.cff`.

## License

MIT — see `LICENSE`.
