"""Stage 9 - Incremental explanatory power (nested models, subject-aware).

Models (per subject, then population-aggregated):
  M0: R ~ 1                        (null)
  M1: R ~ degree                   (should add ~0: R is degree-orthogonal)
  M2: R ~ degree + strength        (strength is the remaining connectivity axis)
  M3: R ~ degree + f_j             (single non-redundant feature)
  M4: R ~ degree + pre-selected non-redundant feature set
Selection of the M4 set is FIXED A PRIORI from Stage 7 redundancy groups:
one representative per group (highest interpretability), all low-redundant
features retained, coupling-risk features kept but flagged.
CV: 5-fold by subject (grouped) for honest population-level CV-R2.
Output: 10_TABLES/table_p2_nested_models.csv
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

TREE = Path(__file__).resolve().parents[1]
CFG = json.loads((TREE / "01_CONFIG" / "config.json").read_text())
TBL = TREE / "10_TABLES"
OUT = TREE / "05_MECHANISM_ANALYSIS"
PRIMARY = CFG["residualization"]["primary"]


def r2(y, yhat):
    ss = float(((y - yhat) ** 2).sum())
    st = float(((y - y.mean()) ** 2).sum())
    return 1 - ss / st


def fit_r2(d, cols):
    X = np.column_stack([np.ones(len(d))] + [d[c].to_numpy(float) for c in cols])
    y = d["residual_cis"].to_numpy(float)
    for c in cols:
        v = d[c].to_numpy(float)
        X[:, cols.index(c) + 1] = (v - v.mean()) / (v.std() or 1.0)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return r2(y, X @ beta)


def main() -> None:
    res = pd.read_parquet(TREE / "04_DEGREE_CONTROL" / "continuous_residuals.parquet")
    # no 'degree' selection - avoids degree_x/degree_y merge collision;
    # the feature matrix's degree column is authoritative.
    res = res[res["estimator"] == PRIMARY][["subject", "node", "residual_cis"]].copy()
    res["subject"] = res["subject"].astype(str).str.zfill(4)  # key alignment vs feature matrix
    feat = pd.read_parquet(TREE / "03_FEATURE_EXTRACTION" / "NODE_FEATURE_MATRIX.parquet")
    df = feat.merge(res, on=["subject", "node"], validate="1:1")
    assert len(df) == len(feat), "merge lost rows - subject key misalignment"
    df["zstrength"] = df["strength"]
    df["zbetweenness"] = df["betweenness"]
    df["zcloseness_d"] = df["closeness_d"]
    df["zredundancy"] = df["redundancy"]
    df["zbridge"] = df["bridge"]
    df["zparticipation"] = df["participation"]
    df["zwmz"] = df["within_module_z"]
    df["zkcore"] = df["kcore"]
    df["zeigenvector"] = df["eigenvector"]
    df["zpagerank"] = df["pagerank"]
    df["zclustering"] = df["clustering"]

    # a-priori M4 set: one per Stage-7 redundancy block + all standalone.
    # The frozen rule (header) is applied MECHANICALLY from the Stage 7
    # correlation table: within any pair with median within-subject
    # |Spearman| >= 0.9, keep ONE representative. Tie-break preference is
    # fixed a priori (not result-dependent): hypothesis-bearing/coupling-
    # flagged features are kept - redundancy (H2) over clustering,
    # betweenness (H4) over closeness_d; otherwise the first-listed wins.
    corr_path = TREE / "10_TABLES" / "table_p2_feature_correlations.csv"
    candidates = ["strength", "betweenness", "closeness_d", "redundancy",
                  "bridge", "participation", "within_module_z", "kcore",
                  "clustering"]
    keep_pref = {"redundancy": 2, "betweenness": 2, "clustering": 1,
                 "closeness_d": 1}  # higher = kept in a redundant pair
    pruned = []
    if corr_path.exists():
        Rm = pd.read_csv(corr_path, index_col=0)
        dropped = set()
        for a in candidates:
            for b in candidates:
                if a >= b or a in dropped or b in dropped:
                    continue
                if a in Rm.index and b in Rm.columns and abs(Rm.loc[a, b]) >= 0.9:
                    lose = a if keep_pref.get(a, 0) < keep_pref.get(b, 0) else b
                    dropped.add(lose)
                    pruned.append((a, b, lose))
        M4 = [c for c in candidates if c not in dropped]
    else:
        M4 = candidates  # Stage 7 not run: fail loud instead? No - keep full set, flag it
        pruned.append(("(stage7-missing)", "", ""))
    M4 = [f"z{c}" for c in M4]

    singles = ["zstrength", "zbetweenness", "zcloseness_d", "zredundancy",
               "zbridge", "zparticipation", "zwmz", "zkcore", "zeigenvector",
               "zpagerank", "zclustering"]
    models = {"M0_null": [], "M1_degree": ["degree"], "M2_degree_strength": ["degree", "zstrength"]}
    models.update({f"M3_{c[1:]}_plus_degree": ["degree", c] for c in singles})
    models["M4_degree_plus_set"] = ["degree"] + M4

    subjects = df["subject"].unique()
    rng = np.random.default_rng(CFG["seeds"]["bootstrap"])
    folds = rng.permutation(len(subjects)) % 5
    fold_map = dict(zip(subjects, folds))

    rows = []
    for name, cols in models.items():
        r2s, cv_sse, cv_sst = [], 0.0, 0.0
        for s, d in df.groupby("subject"):
            r2s.append(fit_r2(d, cols))
        # grouped CV: fit on 4 folds' subjects, evaluate R2 on held-out subjects
        for k in range(5):
            tr = df[[fold_map[s] != k for s in df["subject"]]]
            te = df[[fold_map[s] == k for s in df["subject"]]]
            Xtr = np.column_stack([np.ones(len(tr))] + [tr[c].to_numpy(float) for c in cols])
            ytr = tr["residual_cis"].to_numpy(float)
            beta, *_ = np.linalg.lstsq(Xtr, ytr, rcond=None)
            Xte = np.column_stack([np.ones(len(te))] + [te[c].to_numpy(float) for c in cols])
            yte = te["residual_cis"].to_numpy(float)
            cv_sse += float(((yte - Xte @ beta) ** 2).sum())
            cv_sst += float(((yte - yte.mean()) ** 2).sum())
        rows.append({"model": name, "n_predictors": len(cols),
                     "median_within_subject_R2": float(np.median(r2s)),
                     "iqr_within_subject_R2": float(np.subtract(*np.quantile(r2s, [0.75, 0.25]))),
                     "cv_R2_grouped_by_subject": 1 - cv_sse / cv_sst})

    out = pd.DataFrame(rows)
    out["delta_cvR2_vs_M1"] = out["cv_R2_grouped_by_subject"] - out.loc[
        out["model"] == "M1_degree", "cv_R2_grouped_by_subject"].iloc[0]
    out.attrs["m4_pruned_pairs"] = pruned
    TBL.mkdir(parents=True, exist_ok=True)
    out.to_csv(TBL / "table_p2_nested_models.csv", index=False)
    print("M4 pruning decisions (stage7 |rho|>=0.9 rule):", pruned)
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
