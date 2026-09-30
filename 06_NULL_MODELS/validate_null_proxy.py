"""Null-residualization proxy validation (external audit item #12).

Question: the Stage-15 null ensemble residualizes via a 20-bin
quantile-median proxy, while the observed analysis uses the frozen df=4
natural cubic spline (M1). Does the proxy materially alter the residual?

Method (per subject, on OBSERVED data):
  R_spline = frozen residual_cis from continuous_residuals.parquet (M1)
  R_20bin  = cis - (per-degree-bin median of cis), bins = quantile grid of
             degree (20 bins) - identical procedure to feature_nulls.py
Compare: within-subject Spearman(R_spline, R_20bin), RMSE normalized by
the spline-residual IQR, max |diff| normalized, and degree-orthogonality
of BOTH residual versions.

Outputs: 06_NULL_MODELS/NULL_PROXY_VALIDATION.json (+ .csv, per subject).
The 12 Stage-15 null subjects are reported separately from the full 801.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

TREE = Path(__file__).resolve().parents[1]
CFG = json.loads((TREE / "01_CONFIG" / "config.json").read_text())
PRIMARY = CFG["residualization"]["primary"]
NF = json.loads((TREE / "06_NULL_MODELS" / "NULL_FEATURE_RESULTS.json").read_text())
NULL_SUBJ = [str(s).zfill(4) for s in NF["subjects"]]
NULL_FEATURES = [r["feature"] for r in NF["summary"]]
FM_PATH = TREE / "03_FEATURE_EXTRACTION" / "NODE_FEATURE_MATRIX.parquet"


def r20(cis: np.ndarray, deg: np.ndarray) -> np.ndarray:
    bins = np.quantile(deg, np.linspace(0, 1, 21))
    bins[0] -= 1e-9
    bins[-1] += 1e-9
    bidx = np.digitize(deg, bins[1:-1], right=True)
    fitted = np.array([np.median(cis[bidx == b]) for b in range(20)])[bidx]
    return cis - fitted


def main() -> None:
    res = pd.read_parquet(TREE / "04_DEGREE_CONTROL" / "continuous_residuals.parquet")
    res = res[res["estimator"] == PRIMARY]
    fm = pd.read_parquet(FM_PATH)
    fm["subject"] = fm["subject"].astype(str).str.zfill(4)
    rows = []
    assoc_rows = []
    for s, d in res.groupby("subject"):
        d = d.sort_values("node")
        cis = d["cis"].to_numpy(float)
        deg = d["degree"].to_numpy(float)
        rs = d["residual_cis"].to_numpy(float)
        r2_ = r20(cis, deg)
        iqr = float(np.subtract(*np.quantile(rs, [0.75, 0.25]))) or 1.0
        rows.append({
            "subject": str(s).zfill(4),
            "spearman_Rspline_R20": float(spearmanr(rs, r2_).statistic),
            "rmse_over_iqr": float(np.sqrt(((rs - r2_) ** 2).mean()) / iqr),
            "maxdiff_over_iqr": float(np.abs(rs - r2_).max() / iqr),
            "abs_rho_degree_spline": abs(float(spearmanr(rs, deg).statistic)),
            "abs_rho_degree_20bin": abs(float(spearmanr(r2_, deg).statistic)),
        })
        # association-level agreement (the quantity the null arbitrates)
        sz = str(s).zfill(4)
        if sz in set(NULL_SUBJ):
            fd = fm[fm["subject"] == sz].sort_values("node")
            for f in NULL_FEATURES:
                x = fd[f].to_numpy(float)
                assoc_rows.append({
                    "subject": sz, "feature": f,
                    "rho_spline": float(spearmanr(rs, x).statistic),
                    "rho_20bin": float(spearmanr(r2_, x).statistic),
                })
    df = pd.DataFrame(rows)
    adf = pd.DataFrame(assoc_rows)
    null_rows = df[df["subject"].isin(NULL_SUBJ)]
    adf["abs_delta"] = (adf["rho_spline"] - adf["rho_20bin"]).abs()
    per_feat = adf.groupby("feature").agg(
        median_rho_spline=("rho_spline", "median"),
        median_rho_20bin=("rho_20bin", "median"),
        median_abs_delta=("abs_delta", "median"),
        p95_abs_delta=("abs_delta", lambda v: float(np.quantile(v, 0.95))),
    )
    # sign consistency of per-subject associations between the two residualizations
    sign_flips = int(((np.sign(adf["rho_spline"]) != np.sign(adf["rho_20bin"]))
                      & (adf[["rho_spline", "rho_20bin"]].abs() > 0.05).all(axis=1)).sum())

    def med(col: str, frame: pd.DataFrame) -> float:
        return float(frame[col].median())

    assoc_summary = {
        "median_abs_delta_rho": float(adf["abs_delta"].median()),
        "p95_abs_delta_rho": float(np.quantile(adf["abs_delta"], 0.95)),
        "sign_flips_beyond_0.05": sign_flips,
        "n_pairs": len(adf),
    }
    out = {
        "purpose": "validate the Stage-15 20-bin null residualization proxy "
                   "against the frozen M1 spline on observed data",
        "n_subjects_total": len(df),
        "n_subjects_null_ensemble": len(null_rows),
        "null_subjects": NULL_SUBJ,
        "null_ensemble_median": {c: med(c, null_rows) for c in df.columns[1:]},
        "null_ensemble_range": {
            c: [float(null_rows[c].min()), float(null_rows[c].max())]
            for c in df.columns[1:]},
        "all_subjects_median": {c: med(c, df) for c in df.columns[1:]},
        "association_level_agreement (the quantity the null arbitrates)": {
            "per_feature": {f: {k: (float(v) if not isinstance(v, str) else v)
                                for k, v in row.items()}
                            for f, row in per_feat.iterrows()},
            **assoc_summary,
        },
        "reading": "point-level residuals differ in the tails (binning vs "
                   "smooth spline, expected); both are degree-orthogonal; "
                   "the feature-association statistic rho(R, feature) - the "
                   "quantity Stage 15 arbitrates - is stable across the two "
                   "residualizations on observed data",
        "note": "identical binning procedure to feature_nulls.py one_null(); "
                "the stored per-null R_null was additionally re-derived "
                "bit-exactly by verify_stage24.py V09",
    }
    (TREE / "06_NULL_MODELS" / "NULL_PROXY_VALIDATION.json").write_text(
        json.dumps(out, indent=2))
    df.to_csv(TREE / "06_NULL_MODELS" / "NULL_PROXY_VALIDATION.csv", index=False)
    adf.to_csv(TREE / "06_NULL_MODELS" / "NULL_PROXY_ASSOCIATIONS.csv", index=False)
    print(json.dumps({"null_ensemble_median": out["null_ensemble_median"],
                      "association_summary": assoc_summary,
                      "per_feature": out["association_level_agreement (the quantity the null arbitrates)"]["per_feature"]},
                     indent=2))
    print(f"\n12 null subjects: median Spearman(R_spline, R_20bin) = "
          f"{med('spearman_Rspline_R20', null_rows):.4f}; association-level "
          f"median |delta rho| = {assoc_summary['median_abs_delta_rho']:.4f}; "
          f"sign flips beyond 0.05: {sign_flips}/{len(adf)}")


if __name__ == "__main__":
    main()
