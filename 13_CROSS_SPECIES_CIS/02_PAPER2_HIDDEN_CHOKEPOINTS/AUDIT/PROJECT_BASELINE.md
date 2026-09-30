# PROJECT BASELINE — Phase 0 Audit (Paper 2: Hidden Chokepoint Mechanics)

Audit date: 2026-09-29. Method: direct inspection (listing, git, runtime
probes); nothing assumed from stale documentation.

## 1. Project root

- **True root:** `D:\humanbrain\humanbrain\` (git repo
  `humanbrain_cross_species_cis`, branch `main`, HEAD at audit:
  `2239d4f` "Paper 2 Stages 0-5: freeze protocol, validate
  degree-controlled residualization (Freeze 1)").
- `D:\HumanBrain` and `D:\humanbrain` are the same volume (Windows
  case-insensitive). The master prompt's separate `D:\HumanBrain` root
  does not exist; the repo root is the `humanbrain/` subfolder.
- The fly study is a **sibling** dataset: `D:\humanbrain\fruitfly`
  (frozen, release v1.0.0). Consumed read-only.

## 2. Git state (at audit)

- Branch `main`, clean HEAD; remote
  `origin = github.com/harsha-vardhan-2006/humanbrain_cross_species_cis`.
- Working tree (pre-existing, NOT created by this session):
  - Modified: `02_PAPER2.../01_CONFIG/CONFIG_FREEZE.md`
    (AMENDMENT 3 — Stage-6 `redundancy` feature repair, appended
    append-only; verified consistent with RESEARCH_LOG P2-00).
  - Untracked: Paper 2 stages 03 (feature matrix + repaired caches),
    05 (mechanism analysis), 06 (null models, no outputs yet),
    07 (robustness, no outputs yet), 08 (statistics), 09 (figs),
    10 (tables).

## 3. Data verification (runtime probes, not trust)

- AOMIC raw: `12_HumanConnectome_AOMIC/zenodo_19796783_raw/` —
  `connectomes_part_*.zip` present (Zenodo 19796783, CC-BY-4.0).
- **E01 v2 cache (the pipeline's actual input):**
  `02_PREPROCESSING/cache_parts/` — 20 files, **4.0 GB**;
  `cache_keys.csv` = **25,200 entries** (900 subjects × 7 atlases ×
  4 variants). Probe: subject 100 primary matrix loads,
  shape (456, 456), weight sum 7,474,069. **PIPELINE RUNNABLE LOCALLY.**
- `01_3D_Volumes`: 0 NIfTI at top level (nii live under subject
  subfolders; count claim deferred to manifest QC — not needed for
  Paper 2, which is connectivity-only).

## 4. Frozen prior results (PRESERVED — never overwritten)

| Quantity | Frozen value | Source |
|---|---|---|
| Top-50 CIS vs degree-preserving null | z = 16.36; p = 1.24e-60 (200/200 subjects) | Paper 1 E-series |
| CIS–degree rho | 0.943 (median; strength 0.486) | Paper 1 |
| Matched-pair residual | 778/801 subjects; delta = 0.100; sign p = 2.6e-197 | Paper 1 E03b |
| FDR-significant residual nodes | 43/456 (BH q<.05) | Paper 1 |
| Human/fly rank agreement | rho ≈ 0.94 | Paper 1 cross-scale |
| Visual contribution | human ≈ 2% vs fly ≈ 80% | Paper 1 |
| Rank stability | ≈ 0.996 | Paper 1 |
| 9-configuration robustness | max diff ≈ 0.0026 | Paper 1 |
| Fly null verdict | z = 1.21; p = 0.109 (NOT null-surviving) | fly v1.0.0 |

"Architecture replicates, anatomy doesn't." — existing framing, retained.

## 5. Paper 2 internal state (stages)

| Stage | Status | Evidence |
|---|---|---|
| 0 audit, 1 question/config, 2 framework | COMPLETE (frozen) | 00_DOCS/*, 01_CONFIG/*, HEAD commit |
| 3 residualization + orthogonality gate | COMPLETE — PASS (median abs rho 0.0327) | 04_DEGREE_CONTROL, RESEARCH_LOG P2-00 |
| 3b same-pairs cross-check | COMPLETE — rho 0.785 vs Paper 1; input identity 8.7e-19 | crosscheck_same_pairs.* |
| 4 replication | COMPLETE — 801/801 delta>0; CI [0.1007, 0.1073] | SUBJECT_REPLICATION_REPORT.md |
| 5 extremes | COMPLETE — pre-registered thresholds | extremes_manifest.json |
| 6 feature extraction | COMPLETE (post AMENDMENT-3 repair) | NODE_FEATURE_MATRIX.parquet (365,256 rows × 12 features) |
| 8 univariate + nested + subject-aware | COMPLETE | UNIVARIATE_RESULTS.json, 10_TABLES |
| 15 nulls | RUNNING (this session; checkpointed) | 06_NULL_MODELS/null_records_checkpoint.jsonl |
| 20 robustness | COMPLETE (this session) | 07_ROBUSTNESS/ROBUSTNESS_MATRIX.csv |
| 21 negative controls | COMPLETE (this session; vectorized exact-equivalent) | NEGATIVE_CONTROLS.json |
| 22 figures / manuscript / QC / release | PENDING (this session) | — |

## 6. Environment (measured)

- Python 3.13.2 (`py -3.13`; pandas 2.3.3, numpy 2.4.2, scipy 1.18.0,
  pyarrow 23.0.1 verified via pip).
- OS: Windows 11, bash (Git Bash) shell; 8 GB RAM (~1.2–2 GB free during
  runs; vectorization required, not optional).
- GPU: none local. Kaggle GPU not required so far — all remaining
  workloads fit local CPU (nulls ~3–6 h with 6 workers; feature-only
  stages are minutes). GPU stays available as fallback for a larger
  null ensemble; per §7 it is used only if materially needed.
- Disk free (measured 2026-09-29): D 85 GB, F 104 GB, G 73 GB — the
  stale D≈143.9/F≈47.3/G≈80.6 snapshot in older docs is superseded.

## 7. Risks & mitigations

- **RAM ceiling (~8 GB):** all new code vectorized/streamed; negative
  controls run in 145 s at <2 GB (serial reference estimated 6–20 h).
- **Session interruption:** Stage-15 nulls append per-record JSONL
  checkpoint (resume-safe; added before first execution, no protocol
  change).
- **Stale docs:** NIfTI=18 and storage numbers are stale; do not
  propagate (this file supersedes).
- **Secrets:** none found at audit; `.gitignore` covers env/key files;
  final scan before commit.

## 8. Recommended execution order (this session)

1. Stage 15 nulls (running) → NULL_FEATURE_RESULTS.json
2. Robustness (done) + negative controls (done)
3. Phase-2 deliverables: node semantics doc, atlas mapping CSV,
   biological annotation master table (evidence-leveled; NOT_ESTABLISHED
   where unmappable), enrichment + degree-controlled stats
4. Figures, paper package, REPRODUCIBILITY, QC runner
5. Secret scan → git init/commit → tag v1.0.0 → push → dist/ ZIP
