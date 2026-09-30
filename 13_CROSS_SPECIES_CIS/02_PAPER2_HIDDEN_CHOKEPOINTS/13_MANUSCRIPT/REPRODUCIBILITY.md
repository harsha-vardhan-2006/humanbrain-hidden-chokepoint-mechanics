# Reproducibility (Paper 2 — 02_PAPER2_HIDDEN_CHOKEPOINTS)

Environment: Windows 11, Python 3.13.2, 8 GB RAM (vectorized/streamed code;
no GPU required — the 12×100 exact-CIS null design ran locally in ~7 h on 6
workers). Frozen seeds: 20270927 (primary), bootstrap/permutation seeds in
`01_CONFIG/config.json`.

## 0. Environment

```bash
py -3.13 -m pip install numpy pandas scipy pyarrow matplotlib
# versions used: numpy 2.4.2, pandas 2.3.3, scipy 1.18.0,
#                pyarrow 23.0.1, matplotlib 3.11.2
```

## 1. Data verification (prerequisite)

Paper 1 acquisition/QC pipeline already validated the AOMIC cache
(`02_PREPROCESSING/cache_parts/`, 25,200 matrices). Paper 2 consumes it
read-only via `02_PREPROCESSING/cache_io.py`. Fly artifacts consumed
read-only from `D:\humanbrain\fruitfly`.

## 2. Stage-by-stage commands (from the study tree)

```bash
cd 13_CROSS_SPECIES_CIS/02_PAPER2_HIDDEN_CHOKEPOINTS

# Stages 0-2 (frozen protocol/config/framework) - documents, no compute.
# Stage 3 + 3b + 4 + 5 (Freeze 1 block; already frozen at HEAD):
py -3.13 04_DEGREE_CONTROL/compute_residuals.py
py -3.13 04_DEGREE_CONTROL/crosscheck_same_pairs.py
py -3.13 04_DEGREE_CONTROL/validate_subjects.py
py -3.13 04_DEGREE_CONTROL/extract_extremes.py
py -3.13 -m pytest 15_TESTS -q

# Stage 6 (feature matrix; requires Amendment-3 repair - verified in-chain):
py -3.13 03_FEATURE_EXTRACTION/extract_features.py

# Stages 7-11 (mechanism + statistics):
py -3.13 05_MECHANISM_ANALYSIS/feature_qc.py
py -3.13 05_MECHANISM_ANALYSIS/univariate_mechanism.py
py -3.13 05_MECHANISM_ANALYSIS/nested_models.py
py -3.13 08_STATISTICS/ml_benchmark.py
py -3.13 08_STATISTICS/subject_aware_models.py

# Stage 20-21 (robustness + negative controls):
py -3.13 07_ROBUSTNESS/robustness.py
py -3.13 07_ROBUSTNESS/negative_controls.py

# Stage 15 (degree-preserving nulls; ~7 h on 6 workers; checkpointed JSONL,
# resume-safe):
py -3.13 06_NULL_MODELS/feature_nulls.py

# Stages 12-13 (fly features + ME.131 case study):
py -3.13 11_CASE_STUDIES/fly_case_study.py

# Annotation + biological enrichment:
py -3.13 scripts_annotation/build_annotations.py
py -3.13 scripts_annotation/master_and_enrichment.py

# Stage 22 (synthesis):
py -3.13 12_SYNTHESIS/chokepoint_definition.py
py -3.13 12_SYNTHESIS/human_vs_fly.py

# Figures:
py -3.13 09_FIGURES/make_figures.py

# Docs (annotation sources, robustness report, synthesis, log entry):
py -3.13 00_DOCS/write_docs.py

# Stage 24 - independent verification of every headline number (12 gates):
py -3.13 13_MANUSCRIPT/verify_stage24.py   # exit 0 = all PASS
```

Alternatively run the full downstream chain (Stages 7-24) with fail-loud
semantics: `bash run_downstream_chain.sh`.

## 3. One-command full rerun

```bash
bash run_downstream_chain.sh && py -3.13 09_FIGURES/make_figures.py \
  && py -3.13 12_SYNTHESIS/chokepoint_definition.py \
  && py -3.13 12_SYNTHESIS/human_vs_fly.py \
  && py -3.13 13_MANUSCRIPT/verify_stage24.py
```

## 4. Reproducibility guarantees

- Seeds frozen in `01_CONFIG/config.json` + script headers; null jobs are
  (subject, seed) addressed and checkpointed to
  `06_NULL_MODELS/null_records_checkpoint.jsonl` (resume-safe).
- Every gate fails loud (non-zero exit) — no silent skips.
- Frozen prior results (Paper 1, fly v1.0.0) are never modified; this study
  reads them read-only.
- Known non-bitwise caveat: ProcessPoolExecutor completion order varies, so
  JSONL append ORDER varies across reruns; record SET and aggregated
  statistics are deterministic given the frozen seed set.
- GPU: none required; the full design ran on local CPU. A Kaggle GPU arm
  was prepared (`08_STATISTICS/dl_kaggle/`) for the optional deep-learning
  benchmark only and is not needed for any headline number.
