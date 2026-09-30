# DL / GNN arm (Kaggle GPU) — Paper 2 Stage 10 supplement

**Why Kaggle:** this workstation has no GPU and no PyTorch; Kaggle provides
free T4 GPUs. The DL arm is therefore run as a versioned notebook whose
outputs return to this repo as audited artifacts. The notebook is
`paper2_gnn_benchmark.ipynb` (in this folder).

## What the DL arm tests (pre-registered, same as the ML arm)

> Is the degree-controlled residual R learnable out-of-sample from graph
> structure, subject-grouped — beyond degree alone?

- **Positive result** ⇒ the residual contains learnable structure beyond
  connectivity; magnitude quantified by Δ CV-R² vs the degree-only model.
- **Null result** ⇒ strong negative control: R ≈ noise floor for current
  features/architectures.
- **Neither is a mechanism claim** (Paper 2 discipline: interpretation runs
  through Stages 8/9 associations, 15/16 nulls, and 21 negative controls).

## Models

| Arm | Model | Split | Status |
|---|---|---|---|
| Reference | closed-form ridge on degree | 5-fold grouped by subject × 3 seeds | local (`ml_benchmark.py`) |
| ML | ridge / ElasticNet / MLP(32) on 12 features | same | local (`ml_benchmark.py`, numpy-native) |
| DL | MLP(64×2) on features | same | this notebook |
| DL | 2-layer GraphSAGE over the frozen 15% binary graph | same (subject-grouped) | this notebook (needs edge files) |
| Control | all of the above with R permuted within subject | same | both |

## Leakage rules (binding)

1. Folds are grouped by **subject**; no node crosses the train/test split.
2. Standardization parameters come from the training folds only.
3. The target R is already degree-controlled (Freeze 1 estimator); degree
   is included as a predictor so "beyond degree" is measurable directly.
4. No test-fold metric is used for model selection (fixed epochs/lr/λ).

## How to run

1. Upload to Kaggle as a notebook; attach the parquet files
   (`NODE_FEATURE_MATRIX.parquet` with merged `residual_cis`; for the GNN
   arm also rebuild per-subject edges — the notebook rebuilds them from
   `02_PREPROCESSING/cache_io.py` if the cache is attached as a dataset).
2. Select GPU T4; Run all.
3. Download `DL_BENCHMARK_RESULTS.json` into this folder and commit.

## In-repo status

The local numpy-native ML arm (`08_STATISTICS/ml_benchmark.py`) runs
without a GPU and produces `table_p2_ml_benchmark.csv`. The DL/GNN arm
completes only via Kaggle; until its JSON lands here, the manuscript
reports the ML arm and marks the DL arm as protocol-registered,
results-pending (never fabricated).
