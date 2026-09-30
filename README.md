# humanbrain-hidden-chokepoint-mechanics

**Paper 2 of the cross-species control-impact series (CIS).**
*Hidden Chokepoints: Graph-Geometric Determinants of Degree-Independent
Control Impact in the Human Structural Connectome — and Their Null
Arbitration.* Harsha Vardhan Malipeddi.

**Status: analysis COMPLETE and FROZEN (2026-09-30). Release v2.0.0.**

## Headline (all numbers from frozen artifacts; gates V01–V12 = 12/12 PASS)

- The degree-independent CIS residual is **real and universal**:
  δ = 0.104, positive in 801/801 subjects, CI [0.1007, 0.1073].
- It is **learnable from network position**: ridge cv-R² = 0.574
  (degree-only ≈ 0; permuted-R control 0.0024). Strongest associate:
  bridge score, within-subject median ρ = +0.4985.
- **Central negative (Outcome C):** under 1,200 exact degree-preserving
  nulls (12 subjects × 100, seed 20270927, per-null full CIS + feature
  recomputation), *every* observed feature–residual association falls
  inside its null p95 band. The mechanism claim is **null-qualified**.
- "Hidden chokepoints" are an **operational label only**: 1/2/3/7
  joint-criterion candidates at k = 1/2/5/10%; node-level null verdict
  NOT_ESTABLISHED.
- Biology: top-10%-CIS nodes **under-represent cortex** (0.444 vs 0.877,
  q = 0.00017) and over-represent subcortex/thalamus. Spatial controls
  NOT_ESTABLISHED (no parcel centroids shipped — none invented).
- Cross-scale: the fly connectome's residual also fails its
  degree-preserving null (z = 1.21, p = 0.109, frozen) — two
  same-direction negatives; **no** universal-mechanism claim.

## Repository layout (study tree flattened to root)

| Path | Contents |
|---|---|
| `00_DOCS/`, `01_CONFIG/` | frozen protocol (+ Amendments 1–3, STUDY FREEZE), research question/log, mathematical framework |
| `03_`–`08_` | feature extraction, degree control, mechanism analysis, null models, robustness, statistics |
| `09_FIGURES/` | 10 figures (+ `13_MANUSCRIPT/FIGURE_LEGENDS.md`) |
| `10_TABLES/` | auto-generated result tables |
| `11_CASE_STUDIES/` | fly ME.131 case study |
| `12_SYNTHESIS/` | chokepoint definition/sensitivity/candidates, human-vs-fly comparison |
| `13_MANUSCRIPT/` | **`RESEARCH_PAPER.md`** (formal manuscript), supplementary, reproducibility, Stage-24 verification gates (`verify_stage24.py`) |
| `QC/` | full-project QC (`run_full_qc.py`, 25 PASS / 0 FAIL / 1 WARNING) |
| `AUDIT/` | phase-0 project baseline |
| `results_annotation/` | 456-node biological annotations + enrichment |
| `data/` | node atlas mapping + frozen summary parquet inputs (read-only lineage) |
| `dist/` | release checksum manifest |

## Reproduce

```bash
py -3.13 13_MANUSCRIPT/verify_stage24.py   # V01-V12, expects 12/12 PASS
py -3.13 QC/run_full_qc.py                 # full QC sweep
```

Heavy regenerable artifacts (raw per-null records, per-subject caches,
the 58 MB release ZIP) are not tracked; every summary JSON/CSV table is.
Full commands: `13_MANUSCRIPT/REPRODUCIBILITY.md`; frozen protocol:
`01_CONFIG/CONFIG_FREEZE.md`.

## Provenance

This repo is a **flattened standalone mirror** of the Paper 2 study tree
`13_CROSS_SPECIES_CIS/02_PAPER2_HIDDEN_CHOKEPOINTS/` in
[`humanbrain_cross_species_cis`](https://github.com/harsha-vardhan-2006/humanbrain_cross_species_cis)
(frozen lineage; see `PROVENANCE.md` for exact parent commits/tags).
Frozen inputs: Paper 1 release v1.1.0 (human CIS, read-only) and the fly
release v1.0.0 (FAFB v783, read-only). Data: AOMIC ID1000 derived
structural connectomes (Zenodo 19796783, CC-BY-4.0), 4S456 parcellation.

## Rules

- The frozen outputs in this repo are **read-only**; new analyses are new
  labeled studies.
- Negative results are first-class outcomes.
- No causal, homology, mechanism, or universal-law claims; bounded novelty
  wording only.

## License

MIT — see `LICENSE`.
