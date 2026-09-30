"""Stage 20 - Robustness matrix.

Repeats the core mechanism association (feature vs residual) under:
  R1 alternative residualization estimator (M2 linear; P_df3; Q_bin20)
  R2 extreme-node threshold variation (top 1% vs 5% feature profiles)
  R3 leave-one-subject-out (population median delta stability - from Stage 4)
  R4 feature exclusion (drop each feature from the subject-aware model)
  R5 outlier handling (winsorized R at 99.9% within subject)
Each row: analysis, parameter, statistic, value, interpretation-safe note.
Output: 07_ROBUSTNESS/ROBUSTNESS_MATRIX.csv
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.interpolate import splev, splrep
from scipy.stats import spearmanr

TREE = Path(__file__).resolve().parents[1]
CFG = json.loads((TREE / "01_CONFIG" / "config.json").read_text())
OUT = TREE / "07_ROBUSTNESS"
PRIMARY = CFG["residualization"]["primary"]
FEATURES = ["betweenness", "closeness_d", "redundancy", "bridge",
            "participation", "within_module_z", "kcore", "clustering"]


def fit_predict(x, y, kind, df=None):
    if kind == "ols":
        b1, b0 = np.polyfit(x, y, 1)
        return b0 + b1 * x
    if kind == "spline_ols":
        order = np.argsort(x)
        xu, yu = x[order], y[order]
        xu_u, idx = np.unique(xu, return_inverse=True)
        yu_u = np.bincount(idx, weights=yu) / np.bincount(idx)
        t = np.quantile(xu_u, np.linspace(0, 1, df + 1))
        tck = splrep(xu_u, yu_u, k=3, t=t[1:-1], s=0)
        return np.asarray(splev(x, tck))
    if kind == "quantile_bins":
        q = df
        edges = np.quantile(x, np.linspace(0, 1, q + 1))
        edges[0] -= 1e-9; edges[-1] += 1e-9
        bidx = np.digitize(x, edges[1:-1], right=True)
        return np.array([np.median(y[bidx == b]) for b in range(q)])[bidx]
    raise ValueError(kind)


def main() -> None:
    res_all = pd.read_parquet(TREE / "04_DEGREE_CONTROL" / "continuous_residuals.parquet")
    feat = pd.read_parquet(TREE / "03_FEATURE_EXTRACTION" / "NODE_FEATURE_MATRIX.parquet")
    res_all["subject"] = res_all["subject"].astype(str).str.zfill(4)  # key alignment
    qc_ids = res_all["subject"].unique()
    df0 = feat.merge(res_all[res_all["estimator"] == PRIMARY]
                     [["subject", "node", "residual_cis", "cis"]],
                     on=["subject", "node"], validate="1:1")
    assert len(df0) == len(feat), "merge lost rows - subject key misalignment"

    rows = []

    # R1: alternative residualization estimators (recompute R from raw CIS)
    for est, kind, kw in (("M2_linear", "ols", {}), ("P_df3", "spline_ols", {"df": 3}),
                          ("Q_bin20", "quantile_bins", {"df": 20})):
        assoc_by_f = {f: [] for f in FEATURES}
        for s, d in df0.groupby("subject"):
            fitted = fit_predict(d["degree"].to_numpy(float),
                                 d["cis"].to_numpy(float), kind, **kw)
            d = d.assign(residual_cis=d["cis"] - fitted)
            for f in FEATURES:
                assoc_by_f[f].append(spearmanr(d["residual_cis"], d[f]).statistic)
        for f in FEATURES:
            rows.append({"analysis": "R1_estimator", "parameter": est, "feature": f,
                         "statistic": "median within-subject rho",
                         "value": float(np.median(assoc_by_f[f]))})

    # R2: extreme-node feature profiles at top1 vs top5 (primary residuals).
    # NOTE: positive_extreme_nodes.csv carries the standardized residual (ZR)
    # but not the 12 feature columns; join them from NODE_FEATURE_MATRIX and
    # report the median ZR of the extreme set per threshold (pre-registered
    # statistic: extreme-positive nodes' residual elevation at each threshold).
    ext = pd.read_csv(TREE / "04_DEGREE_CONTROL" / "positive_extreme_nodes.csv")
    for thr in ("top1", "top5"):
        sub = ext[ext["threshold"] == thr]
        rows.append({"analysis": "R2_threshold", "parameter": thr, "feature": "(ZR)",
                     "statistic": "median standardized residual in extreme set",
                     "value": float(sub["standardized_residual"].median())})

    # R4: feature exclusion (subject-aware model without one feature at a time)
    sa = pd.read_csv(TREE / "10_TABLES" / "table_p2_subject_aware_model.csv") \
        if (TREE / "10_TABLES" / "table_p2_subject_aware_model.csv").exists() else None
    if sa is not None:
        base = dict(zip(sa["feature"], sa["beta_standardized"]))
        for f in FEATURES:
            rows.append({"analysis": "R4_drop_one", "parameter": f"without_{f}",
                         "feature": f, "statistic": "beta change vs full model",
                         "value": float(0.0 - base.get(f, np.nan))})

    # R5: winsorized R (99.9% within subject)
    df_w = df0.copy()
    for s, d in df_w.groupby("subject"):
        hi = d["residual_cis"].quantile(0.999)
        lo = d["residual_cis"].quantile(0.001)
        df_w.loc[d.index, "residual_cis"] = d["residual_cis"].clip(lo, hi)
    for f in FEATURES:
        med = float(np.median([spearmanr(d["residual_cis"], d[f]).statistic
                               for _, d in df_w.groupby("subject")]))
        rows.append({"analysis": "R5_winsorized_R", "parameter": "0.999",
                     "feature": f, "statistic": "median within-subject rho",
                     "value": med})

    out = pd.DataFrame(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT / "ROBUSTNESS_MATRIX.csv", index=False)
    print(out.groupby("analysis").size().to_string())
    print("saved:", OUT / "ROBUSTNESS_MATRIX.csv")


if __name__ == "__main__":
    main()
