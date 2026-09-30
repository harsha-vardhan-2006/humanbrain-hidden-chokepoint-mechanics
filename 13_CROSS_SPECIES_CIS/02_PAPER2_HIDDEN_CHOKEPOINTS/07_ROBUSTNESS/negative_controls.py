"""Stage 21 - Negative controls.

The proposed mechanism (feature-residual associations) must DISAPPEAR under
controls that destroy the feature-residual link while preserving each
control's marginal structure:

  NC1 permuted-R:   R permuted within subject (destroys R-feature pairing,
                    keeps R and feature marginals)
  NC2 permuted-f:   each feature permuted within subject (same, symmetric)
  NC3 random nodes: extreme-node feature profile vs degree-matched RANDOM
                    nodes (selection-matched; profile excess must vanish)
  NC4 null-CIS:     R computed from degree-preserving null CIS (Stage 15
                    nulls) — associations at observed-R level must vanish

Acceptance: |median rho| under each control within the null 95% band from
100 control draws; observed association must exceed it (one-sided).
Output: 10_TABLES/table_p2_negative_controls.csv,
07_ROBUSTNESS/NEGATIVE_CONTROLS.json
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

TREE = Path(__file__).resolve().parents[1]
CFG = json.loads((TREE / "01_CONFIG" / "config.json").read_text())
OUT = TREE / "07_ROBUSTNESS"
TBL = TREE / "10_TABLES"
PRIMARY = CFG["residualization"]["primary"]
SEED = CFG["seeds"]["bootstrap"]
N_DRAWS = 100
FEATURES = ["betweenness", "closeness_d", "redundancy", "bridge",
            "participation", "within_module_z", "kcore", "clustering"]


def assoc(df, f, rcol="residual_cis"):
    return float(spearmanr(df[rcol], df[f]).statistic)


def main() -> None:
    res = pd.read_parquet(TREE / "04_DEGREE_CONTROL" / "continuous_residuals.parquet")
    res = res[res["estimator"] == PRIMARY][["subject", "node", "residual_cis"]].copy()
    res["subject"] = res["subject"].astype(str).str.zfill(4)  # key alignment vs feature matrix
    feat = pd.read_parquet(TREE / "03_FEATURE_EXTRACTION" / "NODE_FEATURE_MATRIX.parquet")
    df = feat.merge(res, on=["subject", "node"], validate="1:1")
    assert len(df) == len(feat), "merge lost rows - subject key misalignment"

    rng = np.random.default_rng(SEED)
    rows = []
    for f in FEATURES:
        obs = float(np.median([assoc(d, f) for _, d in df.groupby("subject")]))
        # NC1: permute R within subject
        nc1 = []
        df_p = df.copy()
        for _ in range(N_DRAWS):
            for s, d in df.groupby("subject"):
                df_p.loc[d.index, "residual_cis"] = rng.permutation(
                    d["residual_cis"].to_numpy())
            nc1.append(float(np.median([assoc(d_p, f)
                                        for _, d_p in df_p.groupby("subject")])))
        # NC2: permute feature within subject
        nc2 = []
        df_p2 = df.copy()
        for _ in range(N_DRAWS):
            for s, d in df.groupby("subject"):
                df_p2.loc[d.index, f] = rng.permutation(d[f].to_numpy())
            nc2.append(float(np.median([assoc(d_p2, f)
                                        for _, d_p2 in df_p2.groupby("subject")])))
        lo, hi = np.quantile(nc1, [0.025, 0.975])
        rows.append({"feature": f, "median_rho_observed": obs,
                     "nc1_permuted_R_median": float(np.median(nc1)),
                     "nc1_p95_abs": float(np.quantile(np.abs(nc1), 0.95)),
                     "nc2_permuted_f_median": float(np.median(nc2)),
                     "nc2_p95_abs": float(np.quantile(np.abs(nc2), 0.95)),
                     "obs_exceeds_nc1_band": bool(abs(obs) > abs(hi)),
                     "obs_exceeds_nc2_band": bool(abs(obs) > abs(hi))})
        print(f"{f:18s} obs={obs:+.3f} nc1_p95={rows[-1]['nc1_p95_abs']:.3f} "
              f"exceeds={rows[-1]['obs_exceeds_nc1_band']}", flush=True)

    out = pd.DataFrame(rows)
    TBL.mkdir(parents=True, exist_ok=True)
    out.to_csv(TBL / "table_p2_negative_controls.csv", index=False)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "NEGATIVE_CONTROLS.json").write_text(json.dumps(
        {"n_draws": N_DRAWS, "seed": SEED,
         "note": "NC1/NC2 within-subject permutation; NC3/NC4 covered by "
                 "ml_benchmark negative control and feature_nulls Stage 15",
         "results": out.to_dict(orient="records")}, indent=2))
    print("saved:", OUT / "NEGATIVE_CONTROLS.json")


if __name__ == "__main__":
    main()
