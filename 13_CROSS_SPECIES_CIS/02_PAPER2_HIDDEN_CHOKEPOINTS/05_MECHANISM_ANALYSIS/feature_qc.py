"""Stage 7 - Feature QC: missing/infinite scan, distributions, Spearman
correlation matrix, VIF (on ranks), and redundancy grouping.

Writes 05_MECHANISM_ANALYSIS/feature_qc_report.md,
10_TABLES/table_p2_feature_correlations.csv, VIF_REPORT.csv.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

TREE = Path(__file__).resolve().parents[1]
CFG = json.loads((TREE / "01_CONFIG" / "config.json").read_text())
FEAT = TREE / "03_FEATURE_EXTRACTION"
OUT = TREE / "05_MECHANISM_ANALYSIS"
TBL = TREE / "10_TABLES"
PRIMARY = CFG["residualization"]["primary"]

FEATURES = ["degree", "strength", "betweenness", "closeness_d", "redundancy",
            "bridge", "participation", "within_module_z", "kcore",
            "eigenvector", "pagerank", "clustering"]
COUPLING = {"betweenness", "closeness_d", "redundancy"}


def main() -> None:
    res = pd.read_parquet(TREE / "04_DEGREE_CONTROL" / "continuous_residuals.parquet")
    res = res[res["estimator"] == PRIMARY][["subject", "node", "residual_cis"]].copy()
    res["subject"] = res["subject"].astype(str).str.zfill(4)  # key alignment vs feature matrix
    feat = pd.read_parquet(FEAT / "NODE_FEATURE_MATRIX.parquet")
    df = feat.merge(res, on=["subject", "node"], validate="1:1")
    assert len(df) == len(feat), "merge lost rows - subject key misalignment"

    rep = ["# FEATURE QC REPORT (Stage 7)", "",
           f"Rows: {len(df):,} ({df['subject'].nunique()} subjects x {df['node'].nunique()} nodes).", ""]

    # missing / infinite
    n_missing = int(df[FEATURES].isna().sum().sum())
    n_inf = int(np.isinf(df[FEATURES].to_numpy(float)).sum())
    rep += [f"- Missing values: **{n_missing}**; infinite values: **{n_inf}** "
            f"(must be 0; fail loud otherwise)."]
    if n_missing or n_inf:
        raise SystemExit("non-finite feature values present")

    # distributions (per-feature across all subject-node rows)
    rep += ["| feature | min | p50 | p99 | max | subject-SD (median) |",
            "|---|---|---|---|---|---|"]
    for f in FEATURES:
        v = df[f].to_numpy(float)
        sds = df.groupby("subject")[f].std().median()
        rep.append(f"| {f} | {v.min():.4g} | {np.median(v):.4g} | "
                   f"{np.quantile(v, 0.99):.4g} | {v.max():.4g} | {sds:.4g} |")

    # subject-level median Spearman correlation matrix (averages out per-subject scale)
    n_f = len(FEATURES)
    R = np.zeros((n_f, n_f))
    subs = df["subject"].unique()
    for s in subs:
        d = df[df["subject"] == s]
        m = spearmanr(d[FEATURES].to_numpy(float)).statistic
        R += np.nan_to_num(np.atleast_2d(m))
    R /= len(subs)
    corr = pd.DataFrame(R, index=FEATURES, columns=FEATURES)
    TBL.mkdir(parents=True, exist_ok=True)
    corr.to_csv(TBL / "table_p2_feature_correlations.csv")

    # VIF on subject-pooled ranks (design-matrix VIF, diagnostic only)
    X = df[FEATURES].rank().to_numpy(float)
    X = (X - X.mean(0)) / X.std(0)
    vif = {}
    for i, f in enumerate(FEATURES):
        others = np.delete(X, i, axis=1)
        y = X[:, i]
        beta, *_ = np.linalg.lstsq(others, y, rcond=None)
        resid = y - others @ beta
        ss_res = float(resid @ resid)
        ss_tot = float(((y - y.mean()) ** 2).sum())
        r2 = 1 - ss_res / ss_tot
        vif[f] = float(1 / (1 - r2)) if r2 < 1 else float("inf")
    pd.DataFrame({"feature": list(vif), "vif": list(vif.values()),
                  "coupling_risk": [f in COUPLING for f in vif]}).to_csv(
        TBL / "VIF_REPORT.csv", index=False)

    # redundancy groups (|rho| >= 0.9 within-subject median)
    hi = np.argwhere(np.abs(R) >= 0.9)
    groups = sorted({tuple(sorted((FEATURES[a], FEATURES[b])))
                     for a, b in hi if a < b})
    group_lines = [f"- {a} ~ {b}" for a, b in groups] if groups else ["- none"]
    rep += ["", "## Redundancy groups (median within-subject |rho| >= 0.9)",
            *group_lines,
            "", "## Modeling rule",
            "Highly redundant features are never placed in the same regression",
            "without pre-registered justification; the Stage 9 feature set is",
            "selected for low redundancy and each feature's coupling risk is",
            "carried into interpretation."]

    (OUT / "feature_qc_report.md").write_text("\n".join(rep) + "\n")
    print("\n".join(rep[:24]))
    print("... (full report: feature_qc_report.md)")


if __name__ == "__main__":
    main()
