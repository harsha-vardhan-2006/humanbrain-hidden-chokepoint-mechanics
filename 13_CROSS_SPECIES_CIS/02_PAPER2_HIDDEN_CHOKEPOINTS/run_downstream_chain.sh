#!/usr/bin/env bash
# Paper 2 - downstream analysis chain (Stages 7-21, 12-13, 24).
# Run ONLY after Stage 6 repair (Amendment 3) is complete and verified.
# Every stage fails loud: the chain stops on the first non-zero exit.
set -euo pipefail
cd "$(dirname "$0")"
PY="py -3.13"
LOG=14_LOGS

echo "=== [0/10] Stage 6 integrity: redundancy != clustering ==="
$PY - <<'EOF'
import pandas as pd, numpy as np, sys
fm = pd.read_parquet("03_FEATURE_EXTRACTION/NODE_FEATURE_MATRIX.parquet")
d = (fm["redundancy"] - fm["clustering"]).abs()
r = np.corrcoef(fm["redundancy"], fm["clustering"])[0, 1]
print(f"max|diff|={d.max():.6f} pearson_r={r:.4f}")
if d.max() == 0.0:
    sys.exit("AMENDMENT 3 NOT APPLIED: redundancy still equals clustering")
EOF

echo "=== [1/10] Stage 7 feature QC ==="
$PY 05_MECHANISM_ANALYSIS/feature_qc.py 2>&1 | tee $LOG/stage7_feature_qc.log

echo "=== [2/10] Stage 8 univariate mechanism ==="
$PY 05_MECHANISM_ANALYSIS/univariate_mechanism.py 2>&1 | tee $LOG/stage8_univariate.log

echo "=== [3/10] Stage 9 nested models ==="
$PY 05_MECHANISM_ANALYSIS/nested_models.py 2>&1 | tee $LOG/stage9_nested.log

echo "=== [4/10] Stage 10 ML benchmark ==="
$PY 08_STATISTICS/ml_benchmark.py 2>&1 | tee $LOG/stage10_ml.log

echo "=== [5/10] Stage 11 subject-aware model ==="
$PY 08_STATISTICS/subject_aware_models.py 2>&1 | tee $LOG/stage11_subject_aware.log

echo "=== [6/10] Stage 20 robustness matrix ==="
$PY 07_ROBUSTNESS/robustness.py 2>&1 | tee $LOG/stage20_robustness.log

echo "=== [7/10] Stage 21 negative controls ==="
$PY 07_ROBUSTNESS/negative_controls.py 2>&1 | tee $LOG/stage21_negative_controls.log

echo "=== [8/10] Stage 15 degree-preserving null arbitration ==="
$PY 06_NULL_MODELS/feature_nulls.py 2>&1 | tee $LOG/stage15_nulls.log

echo "=== [9/10] Stages 12-13 fly case study (ME.131) ==="
$PY 11_CASE_STUDIES/fly_case_study.py 2>&1 | tee $LOG/stage12_13_fly.log

echo "=== [10/10] Stage 24 verification ==="
$PY 13_MANUSCRIPT/verify_stage24.py 2>&1 | tee $LOG/stage24_verification.log

echo "=== CHAIN COMPLETE ==="
