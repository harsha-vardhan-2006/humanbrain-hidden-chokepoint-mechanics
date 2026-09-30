"""Stage 8 - Univariate mechanism analysis.

For each feature f: does f explain the degree-controlled residual R?

Per subject (456 nodes each):
  - Spearman(R, f) -> distribution of within-subject associations
  - Theil-Sen slope of R ~ z(f) (robust; pooled across subjects via median)
  - partial R2: R ~ f + degree  vs  R ~ degree (does f add anything beyond
    degree WITHIN the residual model? orthogonal complement check)
Population inference:
  - one-sample t / Wilcoxon on Fisher-z transformed per-subject rhos
  - BH-FDR across the 12-feature family (within Stage 8, exploratory)
Outputs: 10_TABLES/table_p2_univariate_associations.csv,
08_FIGURES/fig_p2_feature_associations.png, 05_MECHANISM_ANALYSIS/
UNIVARIATE_RESULTS.json
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr, ttest_1samp, wilcoxon

TREE = Path(__file__).resolve().parents[1]
CFG = json.loads((TREE / "01_CONFIG" / "config.json").read_text())
TBL = TREE / "10_TABLES"
FIGS = TREE / "09_FIGURES"
OUT = TREE / "05_MECHANISM_ANALYSIS"
PRIMARY = CFG["residualization"]["primary"]

FEATURES = ["degree", "strength", "betweenness", "closeness_d", "redundancy",
            "bridge", "participation", "within_module_z", "kcore",
            "eigenvector", "pagerank", "clustering"]
COUPLING = {"betweenness", "closeness_d", "redundancy"}


def bh_fdr(p: np.ndarray) -> np.ndarray:
    p = np.asarray(p, float)
    order = np.argsort(p)
    ranked = p[order] * len(p) / (np.arange(len(p)) + 1)
    ranked = np.minimum.accumulate(ranked[::-1])[::-1]
    q = np.empty_like(ranked)
    q[order] = np.minimum(ranked, 1.0)
    return q


def partial_r2_within_subject(d: pd.DataFrame, f: str) -> float:
    """R2 gained by adding z(f) to R ~ degree (per subject)."""
    x_deg = d["degree"].to_numpy(float)
    y = d["residual_cis"].to_numpy(float)
    xf = d[f].to_numpy(float)
    xf = (xf - xf.mean()) / (xf.std() or 1.0)
    A = np.column_stack([np.ones_like(x_deg), x_deg])
    B = np.column_stack([np.ones_like(x_deg), x_deg, xf])
    for X in (A, B):
        pass
    bA, *_ = np.linalg.lstsq(A, y, rcond=None)
    bB, *_ = np.linalg.lstsq(B, y, rcond=None)
    ss = lambda r: float(r @ r)
    r2a = 1 - ss(y - A @ bA) / ss(y - y.mean())
    r2b = 1 - ss(y - B @ bB) / ss(y - y.mean())
    return max(r2b - r2a, 0.0)


def main() -> None:
    res = pd.read_parquet(TREE / "04_DEGREE_CONTROL" / "continuous_residuals.parquet")
    # NOTE: no 'degree' here - it would collide with the feature matrix's
    # degree column at merge time (degree_x/degree_y suffixes); the feature
    # matrix's degree is authoritative (identical values, frozen graph).
    res = res[res["estimator"] == PRIMARY][["subject", "node", "residual_cis"]].copy()
    res["subject"] = res["subject"].astype(str).str.zfill(4)  # key alignment vs feature matrix
    feat = pd.read_parquet(TREE / "03_FEATURE_EXTRACTION" / "NODE_FEATURE_MATRIX.parquet")
    df = feat.merge(res, on=["subject", "node"], validate="1:1")
    assert len(df) == len(feat), "merge lost rows - subject key misalignment"

    rows = []
    per_subject_rho = {}
    for f in FEATURES:
        rhos, pr2s, slopes = [], [], []
        for s, d in df.groupby("subject"):
            rho = spearmanr(d["residual_cis"], d[f]).statistic
            rhos.append(rho)
            pr2s.append(partial_r2_within_subject(d, f))
            zf = (d[f] - d[f].mean()) / (d[f].std() or 1.0)
            y = d["residual_cis"].to_numpy(float)
            A = np.column_stack([np.ones(len(d)), zf.to_numpy(float)])
            b, *_ = np.linalg.lstsq(A, y, rcond=None)
            slopes.append(b[1])
        rhos = np.array(rhos)
        z = np.arctanh(np.clip(rhos, -0.9999, 0.9999))
        t, tp = ttest_1samp(z, 0.0)
        w, wp = wilcoxon(rhos)
        per_subject_rho[f] = rhos.tolist()
        rows.append({
            "feature": f,
            "coupling_risk": f in COUPLING,
            "median_rho": float(np.median(rhos)),
            "iqr_rho": float(np.subtract(*np.quantile(rhos, [0.75, 0.25]))),
            "mean_fisher_z": float(z.mean()),
            "t_vs_zero": float(t), "p_ttest": float(tp),
            "p_wilcoxon": float(wp),
            "median_partial_R2_beyond_degree": float(np.median(pr2s)),
            "median_theilsen_slope": float(np.median(slopes)),
            "n_subjects": len(rhos),
        })

    tbl = pd.DataFrame(rows)
    tbl["q_bh"] = bh_fdr(tbl["p_ttest"].to_numpy())
    # sign-consistency: fraction of subjects with rho matching the population sign
    tbl["frac_subjects_same_sign"] = [
        float((np.sign(per_subject_rho[row["feature"]])
               == np.sign(row["median_rho"])).mean()) for _, row in tbl.iterrows()]

    TBL.mkdir(parents=True, exist_ok=True)
    tbl.to_csv(TBL / "table_p2_univariate_associations.csv", index=False)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "UNIVARIATE_RESULTS.json").write_text(json.dumps(
        {"primary_estimator": PRIMARY, "n_subjects": int(tbl['n_subjects'].iloc[0]),
         "results": tbl.to_dict(orient="records")}, indent=2))

    # figure: per-feature rho distributions (violin-ish box+strip)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    data = [per_subject_rho[f] for f in FEATURES]
    bp = ax.boxplot(data, vert=False, showfliers=False, widths=0.6)
    ax.set_yticklabels([f"{f}{' *' if f in COUPLING else ''}" for f in FEATURES])
    ax.axvline(0, color="grey", lw=0.8, ls="--")
    ax.set_xlabel("within-subject Spearman rho( R , feature )")
    ax.set_title("Feature–residual associations (801 subjects; * = coupling risk)")
    fig.tight_layout()
    FIGS.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGS / "fig_p2_feature_associations.png", dpi=150)

    show = tbl[["feature", "coupling_risk", "median_rho", "q_bh",
                "median_partial_R2_beyond_degree", "frac_subjects_same_sign"]]
    print(show.to_string(index=False))


if __name__ == "__main__":
    main()
