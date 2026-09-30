"""Stage 11 - Subject-aware multivariate model (no statsmodels available).

Design: pooled node-level regression of residual R on standardized features
with SUBJECT FIXED EFFECTS (within-transformation), and CLUSTER-ROBUST
(CR1) standard errors clustered by subject — the canonical remedy for
nodes-nested-in-subjects dependence.

R_ij = a_j + b' x_ij + e_ij   (a_j = subject fixed effect)

Implemented with numpy lstsq (within-transform absorbs fixed effects) and
the CR1 sandwich: V = (X'X)^-1 (sum_j X_j' u_j u_j' X_j) (X'X)^-1 * c, with
degrees-of-freedom correction c = G/(G-1) * (N-1)/(N-K).
Output: 08_STATISTICS/SUBJECT_AWARE_MODEL.json,
10_TABLES/table_p2_subject_aware_model.csv
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import t as tdist

TREE = Path(__file__).resolve().parents[1]
CFG = json.loads((TREE / "01_CONFIG" / "config.json").read_text())
OUT = TREE / "08_STATISTICS"
TBL = TREE / "10_TABLES"
PRIMARY = CFG["residualization"]["primary"]

FEATURES = ["betweenness", "closeness_d", "redundancy", "bridge",
            "participation", "within_module_z", "kcore", "clustering"]
COUPLING = {"betweenness", "closeness_d", "redundancy"}


def main() -> None:
    res = pd.read_parquet(TREE / "04_DEGREE_CONTROL" / "continuous_residuals.parquet")
    res = res[res["estimator"] == PRIMARY][["subject", "node", "residual_cis"]].copy()
    res["subject"] = res["subject"].astype(str).str.zfill(4)  # key alignment vs feature matrix
    feat = pd.read_parquet(TREE / "03_FEATURE_EXTRACTION" / "NODE_FEATURE_MATRIX.parquet")
    df = feat.merge(res, on=["subject", "node"], validate="1:1")
    assert len(df) == len(feat), "merge lost rows - subject key misalignment"

    # within-transform by subject (absorbs fixed effects), standardize pooled
    y = df["residual_cis"].to_numpy(float)
    X = np.column_stack([df[f].to_numpy(float) for f in FEATURES])
    subjects = df["subject"].to_numpy()

    # standardize using full-sample mean/sd (fixed across within-demeaning)
    mu, sd = X.mean(0), X.std(0)
    sd[sd == 0] = 1.0
    Xz = (X - mu) / sd

    # demean within subject
    dfr = pd.DataFrame(Xz, columns=FEATURES)
    dfr["subject"] = subjects
    dfr["y"] = y
    W = dfr.groupby("subject").transform(lambda v: v - v.mean())
    Xw = W[FEATURES].to_numpy()
    yw = W["y"].to_numpy()

    # drop one redundant within-demeaning dimension (subjects sum to zero):
    # add back an intercept-free fit; dof handled in CR1 constant below.
    XtX = Xw.T @ Xw
    XtX_inv = np.linalg.pinv(XtX)
    beta = XtX_inv @ (Xw.T @ yw)
    u = yw - Xw @ beta

    # CR1 cluster-robust covariance clustered by subject
    G = len(np.unique(subjects))
    N, K = Xw.shape
    meat = np.zeros((K, K))
    order = np.argsort(subjects, kind="stable")
    Xs, us, ss = Xw[order], u[order], subjects[order]
    bounds = np.flatnonzero(np.r_[True, ss[1:] != ss[:-1]]).tolist() + [N]
    for a, b in zip(bounds[:-1], bounds[1:]):
        Xj = Xs[a:b]
        uj = us[a:b]
        Sj = Xj.T @ uj
        meat += np.outer(Sj, Sj)
    c = G / (G - 1) * (N - 1) / (N - K)
    V = c * (XtX_inv @ meat @ XtX_inv)
    se = np.sqrt(np.diag(V))
    tstat = beta / se
    pval = 2 * tdist.sf(np.abs(tstat), df=G - 1)

    rows = []
    for i, f in enumerate(FEATURES):
        rows.append({"feature": f, "beta_standardized": float(beta[i]),
                     "cluster_robust_se": float(se[i]), "t": float(tstat[i]),
                     "p": float(pval[i]), "n_subjects": G, "n_rows": N,
                     "coupling_risk": f in COUPLING})
    out = pd.DataFrame(rows)
    # BH-FDR
    p = out["p"].to_numpy()
    order = np.argsort(p)
    q = np.empty_like(p)
    q[order] = np.minimum.accumulate((p[order] * len(p) / (np.arange(len(p)) + 1))[::-1])[::-1]
    out["q_bh"] = np.minimum(q, 1.0)

    OUT.mkdir(parents=True, exist_ok=True)
    TBL.mkdir(parents=True, exist_ok=True)
    out.to_csv(TBL / "table_p2_subject_aware_model.csv", index=False)
    (OUT / "SUBJECT_AWARE_MODEL.json").write_text(json.dumps(
        {"design": "subject fixed effects (within) + CR1 cluster-robust SE, "
                   "cluster = subject",
         "n_subjects": G, "n_rows": N, "note": "numpy implementation; "
         "statistics cross-checked on a single-subject bootstrap in tests"},
        indent=2))
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
