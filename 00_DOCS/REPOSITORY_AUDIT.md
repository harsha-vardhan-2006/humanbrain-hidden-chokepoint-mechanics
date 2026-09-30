# REPOSITORY AUDIT — Paper 2 (Stage 0)

Executed 2026-09-27 (paths verified by listing/reading, not assumed).

## Layout resolved

- Workspace root: `<workspace>/humanbrain/` (the D:\HumanBrain acquisition
  workspace; NO nested `humanbrain/humanbrain` duplication exists).
- Study tree: `<workspace>/humanbrain/13_CROSS_SPECIES_CIS/` — frozen Paper 1
  release v1.1.0 (tag pushed; GitHub Release created 2026-09-27).
- Paper-series folders: `<workspace>/paper-1/` (snapshot, complete),
  `<workspace>/paper-2/` (this paper's series slot; holds only README).
- Paper 2 study tree (NEW, this stage):
  `13_CROSS_SPECIES_CIS/02_PAPER2_HIDDEN_CHOKEPOINTS/` with subdirs
  00_DOCS … 15_TESTS per the master prompt.

## Verified data inputs (exact paths, read-only)

| Artifact | Path | Verified content |
|---|---|---|
| Per-subject exact CIS | `13_CROSS_SPECIES_CIS/04_CIS/subject_cis/` | 900 CSVs; columns `node,cis,degree,strength,cis_rank,e0` (456 rows each) |
| Population CIS summary | `04_CIS/population_cis.csv`, `population_cis_summary.csv` | present (Paper 1) |
| E03 summary | `04_CIS/e03_summary.json` | 900 subjects, 801 QC-pass, 456 nodes; cis_mean_pop_max 0.004624584563433848 @ node 414 |
| Matched-pair control (E03b) | `04_CIS/degree_strength_control_per_subject.csv` (+`_results.csv`, `degree_strength_control_summary.json`, `DEGREE_STRENGTH_CONTROL.md`) | Paper 1 residual cross-check (δ median 0.100) |
| QC gate | `03_BASELINE/qc_primary.csv` | 900 rows; boolean `qc_pass`; flags: isolated/strength-IQR/density/components (columns verified) |
| Atlas system labels | `00_MANIFEST/manifests/atlas_4S456_system_labels.csv` | 456 rows + header; columns `node,label,system` |
| Null batteries | `05_NULLS/degree_preserving/` | battery A (100 subj × 100 nulls), battery B (200 × 100); npz + manifests + validation |
| Raw connectomes | `12_HumanConnectome_AOMIC/zenodo_19796783_raw/` (READ-FOREVER) + cache `02_PREPROCESSING/cache_parts/` (regenerable; git-ignored) | not touched by Paper 2 Stage 0–5 |
| Fly frozen artifacts | `<workspace>/fruitfly/results/final/e10b_final.json`, `results/tables/e12_strong_results.json`, `e14_chokepoint_catalogue_v2.csv`, `e14_v2_summary.json` | read-only reference; residual null z = 1.21, p = 0.109 |

## Scripts reused from Paper 1 (read-only imports; no modification)

- `02_PREPROCESSING/cache_io.py` — frozen threshold/efficiency/CIS math
  (needed only if raw graphs must be reloaded in Stage 6+; NOT used in
  Stages 3–5, which consume frozen CIS/degree/strength CSVs).
- `04_CIS/cis_primary.py`, `degree_control.py`, `e05_statistics.py` —
  reference implementations for conventions (not executed).
- QC cohort definition: `qc_pass == True` rows of `qc_primary.csv`
  (Paper 1 frozen flags; flag-never-delete).

## Scripts newly created (Paper 2)

- `01_CONFIG/freeze_config.py` — machine-readable config.json writer (Stage 3)
- `04_DEGREE_CONTROL/compute_residuals.py` — Stage 3 (per-subject
  residualization, all estimator variants, orthogonality gate)
- `04_DEGREE_CONTROL/validate_subjects.py` — Stage 4 (bootstrap CI,
  replication, heterogeneity, LOSO) + cross-check vs E03b
- `04_DEGREE_CONTROL/extract_extremes.py` — Stage 5 (pre-registered
  thresholds → 3 CSVs)
- `15_TESTS/test_stage3_residuals.py` — unit tests (pytest, stdlib/numpy only)
- `14_LOGS/run_stages_3_5.log` — full run log

## Dependencies

Python 3.13.2; numpy 2.4.2, pandas 2.3.3, scipy 1.18.0 (versions from the
frozen environment manifest). No new dependencies for Stages 0–5
(scipy splines → `scipy.interpolate`; tests via pytest if available, else
a stdlib runner).

## Known limitations / unresolved issues

1. CIS values are consumed frozen from Paper 1; any Paper 1 CIS error would
   propagate (mitigation: Paper 1's 46/46 independent numeric audit; the
   E03b cross-check in Stage 4).
2. Model-based residualization (Stage 3) is statistically dependent on
   estimator choice — hence the frozen estimator ladder and the
   orthogonality gate rather than a single unvalidated choice.
3. Strength is available per node but not used in the primary
   residualization (degree-only, per master prompt Stage 3); strength
   enters at Stage 9 (nested models) — this ordering is deliberate.
4. Fly-side analyses are deferred to Freeze 3+ (master prompt Stage 22).
5. The `paper-1/` snapshot folder is documentation only; all computation
   uses the frozen study tree paths above.
