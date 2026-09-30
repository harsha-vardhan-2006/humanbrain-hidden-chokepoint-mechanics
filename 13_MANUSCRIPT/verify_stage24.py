"""Stage 24 - Independent verification of every Paper 2 headline number.

DESIGN (strengthened per external research-submission audit, 2026-09-30):
this is a genuine independent re-derivation layer, not an existence check.

  V01  Orthogonality gate: median |rho(R, degree)| < 0.05 - RECOMPUTED from
       the frozen per-node residual file (scipy Spearman, 801 subjects).
  V02  Same-pairs cross-check: Spearman(delta_ours, delta_paper1) >= 0.5 -
       RECOMPUTED from per-subject CSV vs the frozen Paper 1 delta values.
  V03  Subject replication: delta_ours > 0 in all 801 QC-pass subjects -
       RECOMPUTED from the per-subject table.
  V04  Stage 6 feature matrix complete: 801 x 456, 0 non-finite.
  V05  Stage 8 univariate table: 12 features, finite rhos, valid q.
  V06  Stage 9 nested models - M1/M4 cv-R2 INDEPENDENTLY RECOMPUTED from the
       merged residual+feature matrix with the analysis' own fold rule and
       a-priori M4 selection; agreement with the frozen table required.
  V07  Stage 10 ML benchmark - degree-only and ridge cv-R2 INDEPENDENTLY
       RECOMPUTED (3 seeds x 5 subject-grouped folds, train-fold scaling,
       lam=1.0 closed-form ridge, permuted-R control); agreement required.
  V08  Stage 11 subject-aware model: 8 features, valid CR1 output.
  V09  Stage 15 null arbitration - DEEP VERIFICATION against the raw null
       records (1,200 lines JSONL): 12 subjects x 100 unique seeds; per-null
       exact degree preservation vs the observed degree sequence (multiset);
       INDEPENDENT re-derivation of R_null from (cis_null, degree) via the
       documented 20-bin quantile-median proxy (also validates the null
       residualization proxy against its stored value); pooled null median/
       IQR/|rho| p95 recomputed and compared; observed signed median rho
       recomputed from all 801 subjects; Outcome C reproduced from raw data.
       Explicit FAIL with remedy if the raw records are absent (gitignored
       for size; shipped in the release archive).
  V10  Stage 20 robustness - sign consistency of bridge/participation across
       ALL median-rho rows CHECKED NUMERICALLY vs Stage 8; R1/R2/R5 grids
       present with expected parameter values.
  V11  Stage 21 negative controls - observed |median rho| exceeds the
       NC1/NC2 p95 bands RECHECKED NUMERICALLY per feature.
  V12  Fly case study: ME.131 profile consistent with frozen catalogue.

Exit code 0 = all checks PASS. Any FAIL exits 1 (fail loud, no silent skip).
Usage:  py 13_MANUSCRIPT/verify_stage24.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

TREE = Path(__file__).resolve().parents[1]
CFG = json.loads((TREE / "01_CONFIG" / "config.json").read_text())
PRIMARY = CFG["residualization"]["primary"]

FEATURES = ["strength", "betweenness", "closeness_d", "redundancy", "bridge",
            "participation", "within_module_z", "kcore", "eigenvector",
            "pagerank", "clustering"]
NULL_FEATURES = ["betweenness", "bridge", "redundancy", "participation",
                 "within_module_z", "kcore", "clustering", "eigenvector",
                 "pagerank"]
N_SUBJECTS_EXPECTED = 801

results: list[dict] = []


def check(vid: str, desc: str, ok: bool, detail: str) -> None:
    results.append({"id": vid, "check": desc, "pass": bool(ok), "detail": detail})
    print(f"[{'PASS' if ok else 'FAIL'}] {vid}  {desc}  ({detail})")


def load_analysis_frame() -> pd.DataFrame:
    """Residual + features, exactly as the analysis scripts build it."""
    res = pd.read_parquet(TREE / "04_DEGREE_CONTROL" / "continuous_residuals.parquet")
    res = res[res["estimator"] == PRIMARY][["subject", "node", "residual_cis"]].copy()
    res["subject"] = res["subject"].astype(str).str.zfill(4)
    feat = pd.read_parquet(TREE / "03_FEATURE_EXTRACTION" / "NODE_FEATURE_MATRIX.parquet")
    df = feat.merge(res, on=["subject", "node"], validate="1:1")
    assert len(df) == len(feat), "merge lost rows - subject key misalignment"
    return df


def nested_models_cv(df: pd.DataFrame) -> dict[str, float]:
    """Independent re-implementation of the Stage 9 grouped CV (M1, M4).

    Replicates nested_models.py exactly: a-priori M4 selection from the
    Stage 7 correlation table (|rho| >= 0.9 prune, fixed tie-break),
    subject-level fold assignment from the frozen bootstrap seed, OLS via
    lstsq, pooled-SSE/SST cv-R2.
    """
    for c in FEATURES:
        df[f"z{c}"] = df[c]

    corr_path = TREE / "10_TABLES" / "table_p2_feature_correlations.csv"
    candidates = ["strength", "betweenness", "closeness_d", "redundancy",
                  "bridge", "participation", "within_module_z", "kcore",
                  "clustering"]
    keep_pref = {"redundancy": 2, "betweenness": 2, "clustering": 1,
                 "closeness_d": 1}
    Rm = pd.read_csv(corr_path, index_col=0)
    dropped: set[str] = set()
    for a in candidates:
        for b in candidates:
            if a >= b or a in dropped or b in dropped:
                continue
            if a in Rm.index and b in Rm.columns and abs(Rm.loc[a, b]) >= 0.9:
                dropped.add(a if keep_pref.get(a, 0) < keep_pref.get(b, 0) else b)
    M4 = [f"z{c}" for c in candidates if c not in dropped]

    subjects = df["subject"].unique()
    rng = np.random.default_rng(CFG["seeds"]["bootstrap"])
    folds = rng.permutation(len(subjects)) % 5
    fold_map = dict(zip(subjects, folds))

    def cv_r2(cols: list[str]) -> float:
        sse = sst = 0.0
        for k in range(5):
            tr = df[[fold_map[s] != k for s in df["subject"]]]
            te = df[[fold_map[s] == k for s in df["subject"]]]
            Xtr = np.column_stack([np.ones(len(tr))] + [tr[c].to_numpy(float) for c in cols])
            ytr = tr["residual_cis"].to_numpy(float)
            beta, *_ = np.linalg.lstsq(Xtr, ytr, rcond=None)
            Xte = np.column_stack([np.ones(len(te))] + [te[c].to_numpy(float) for c in cols])
            yte = te["residual_cis"].to_numpy(float)
            sse += float(((yte - Xte @ beta) ** 2).sum())
            sst += float(((yte - yte.mean()) ** 2).sum())
        return 1 - sse / sst

    return {"M1": cv_r2(["degree"]), "M4": cv_r2(["degree"] + M4)}


def ml_benchmark_ridge_cv(df: pd.DataFrame) -> dict[str, float]:
    """Independent re-implementation of the Stage 10 degree-only and ridge
    arms (3 seeds x 5 subject-grouped folds, train-fold standardization,
    closed-form ridge lam=1.0), plus the within-subject permuted-R control.
    """
    for c in ["degree"] + FEATURES:
        df[f"v_{c}"] = df[c]
    subjects = df["subject"].unique()

    def folds(seed: int) -> dict:
        r = np.random.default_rng(seed)
        return dict(zip(subjects, r.permutation(len(subjects)) % 5))

    def cv(model: str, fold_map: dict, frame: pd.DataFrame | None = None) -> float:
        frame = df if frame is None else frame
        sse = sst = 0.0
        cols = ["v_degree"] + ([] if model == "degree_only" else [f"v_{c}" for c in FEATURES])
        for k in range(5):
            tr_m = frame["subject"].map(fold_map) != k
            tr, te = frame[tr_m], frame[~tr_m]
            mu, sd = tr[cols].mean(), tr[cols].std().replace(0, 1)
            Xtr = ((tr[cols] - mu) / sd).to_numpy()
            Xte = ((te[cols] - mu) / sd).to_numpy()
            ytr = tr["residual_cis"].to_numpy(float)
            yte = te["residual_cis"].to_numpy(float)
            A = Xtr.T @ Xtr + np.eye(Xtr.shape[1])
            beta = np.linalg.solve(A, Xtr.T @ ytr)
            sse += float(((yte - Xte @ beta) ** 2).sum())
            sst += float(((yte - yte.mean()) ** 2).sum())
        return 1 - sse / sst

    seeds = (20270927, 20270928, 20270929)
    deg = float(np.mean([cv("degree_only", folds(s)) for s in seeds]))
    rid = float(np.mean([cv("ridge", folds(s)) for s in seeds]))

    perm = df.copy()
    perm_seed = 20270930
    for s, d in perm.groupby("subject"):
        perm.loc[d.index, "residual_cis"] = d["residual_cis"].to_numpy()[
            np.random.default_rng(perm_seed).permutation(len(d))]
    rid_perm = float(np.mean([cv("ridge", folds(s), perm) for s in seeds]))
    return {"degree_only": deg, "ridge": rid, "ridge_permuted": rid_perm}


def main() -> None:
    # ---- V01: orthogonality gate (recompute from the frozen residual file) --
    res = pd.read_parquet(TREE / "04_DEGREE_CONTROL" / "continuous_residuals.parquet")
    res_p = res[res["estimator"] == PRIMARY]
    rhos = [spearmanr(d["residual_cis"], d["degree"]).statistic
            for _, d in res_p.groupby("subject")]
    med_abs = float(np.median(np.abs(rhos)))
    check("V01", "orthogonality gate median |rho(R, degree)| < 0.05",
          med_abs < 0.05, f"median |rho| = {med_abs:.4f}, n_subjects = {len(rhos)}")

    # ---- V02: same-pairs cross-check (recomputed from per-subject CSV) ------
    e03b = pd.read_csv(CFG["paths"]["e03b_per_subject"])
    e03b["subject"] = e03b["subject"].astype(str).str.zfill(4)
    paper1_delta = e03b.set_index("subject")["cliffs_delta"]
    cc = pd.read_csv(TREE / "04_DEGREE_CONTROL" / "crosscheck_same_pairs.csv")
    cc["subject"] = cc["subject"].astype(str).str.zfill(4)
    m = cc.merge(paper1_delta.rename("delta_paper1"),
                 left_on="subject", right_index=True, how="inner")
    rho_cc = float(spearmanr(m["delta_ours"], m["delta_paper1"]).statistic)
    check("V02", "same-pairs cross-check rho(delta_ours, delta_paper1) >= 0.5",
          rho_cc >= 0.5 and len(m) >= 780,
          f"rho = {rho_cc:.3f} over {len(m)} subjects (recomputed)")

    # ---- V03: subject replication (recomputed from per-subject table) -------
    n_pos = int((cc["delta_ours"] > 0).sum())
    check("V03", "residual effect positive in all QC-pass subjects",
          n_pos == N_SUBJECTS_EXPECTED and len(cc) == N_SUBJECTS_EXPECTED,
          f"{n_pos}/{len(cc)} subjects with delta_ours > 0 (recomputed)")

    # ---- V04: feature matrix completeness -----------------------------------
    fm_path = TREE / "03_FEATURE_EXTRACTION" / "NODE_FEATURE_MATRIX.parquet"
    if fm_path.exists():
        fm = pd.read_parquet(fm_path)
        n_sub = fm["subject"].nunique()
        n_rows = len(fm)
        feats = ["degree"] + FEATURES
        n_bad = int(fm[feats].isna().sum().sum()
                    + np.isinf(fm[feats].to_numpy(float)).sum())
        check("V04", "feature matrix 801 x 456, zero non-finite feature values",
              n_sub == N_SUBJECTS_EXPECTED and n_rows == N_SUBJECTS_EXPECTED * 456 and n_bad == 0,
              f"{n_sub} subjects, {n_rows} rows, {n_bad} non-finite")
    else:
        check("V04", "feature matrix exists", False, "NODE_FEATURE_MATRIX.parquet missing")

    # ---- V05: univariate table ----------------------------------------------
    uni_path = TREE / "05_MECHANISM_ANALYSIS" / "UNIVARIATE_RESULTS.json"
    uni_bridge: dict[str, float] = {}
    if uni_path.exists():
        uni_rows = json.loads(uni_path.read_text())["results"]
        uni_bridge = {r["feature"]: float(r["median_rho"]) for r in uni_rows}
        ok = (len(uni_rows) == 12
              and all(0.0 <= r["q_bh"] <= 1.0 for r in uni_rows)
              and all(np.isfinite(r["median_rho"]) for r in uni_rows))
        top = max(uni_rows, key=lambda r: abs(r["median_rho"]))
        check("V05", "univariate table: 12 features, finite rhos, valid q",
              ok, f"top |median rho| = {top['median_rho']:+.3f} ({top['feature']})")
    else:
        check("V05", "univariate table exists", False, "UNIVARIATE_RESULTS.json missing")

    # ---- V06: nested models (independent CV recomputation) ------------------
    nm_path = TREE / "10_TABLES" / "table_p2_nested_models.csv"
    if nm_path.exists():
        nm = pd.read_csv(nm_path)
        m1_frozen = float(nm.loc[nm["model"] == "M1_degree", "cv_R2_grouped_by_subject"].iloc[0])
        m4_frozen = float(nm.loc[nm["model"] == "M4_degree_plus_set", "cv_R2_grouped_by_subject"].iloc[0])
        re = nested_models_cv(load_analysis_frame())
        tol = 1e-6
        ok = (abs(re["M1"] - m1_frozen) <= tol
              and abs(re["M4"] - m4_frozen) <= tol
              and (m4_frozen - m1_frozen) > 0.25)
        check("V06", "nested models M1/M4 cv-R2 independently recomputed",
              ok, f"recomputed M1 = {re['M1']:.6f} vs frozen {m1_frozen:.6f}; "
                  f"recomputed M4 = {re['M4']:.6f} vs frozen {m4_frozen:.6f}; "
                  f"delta = {m4_frozen - m1_frozen:+.4f}")
    else:
        check("V06", "nested models table exists", False, "table_p2_nested_models.csv missing")

    # ---- V07: ML benchmark (independent ridge CV recomputation) --------------
    ml_path = TREE / "10_TABLES" / "table_p2_ml_benchmark.csv"
    if ml_path.exists():
        ml = pd.read_csv(ml_path)
        deg_frozen = float(ml.loc[ml["model"] == "degree_only", "cv_R2_mean"].iloc[0])
        ridge_frozen = float(ml.loc[ml["model"] == "ridge", "cv_R2_mean"].iloc[0])
        perm_frozen = float(ml.loc[ml["model"] == "ridge", "cv_R2_permuted_mean"].iloc[0])
        re = ml_benchmark_ridge_cv(load_analysis_frame())
        tol = 1e-4
        ok = (abs(re["degree_only"] - deg_frozen) <= tol
              and abs(re["ridge"] - ridge_frozen) <= tol
              and abs(re["ridge_permuted"] - perm_frozen) <= 5e-3
              and (ridge_frozen - deg_frozen) > 0.5
              and perm_frozen < 0.01)
        check("V07", "ML benchmark degree-only/ridge cv-R2 independently recomputed",
              ok, f"recomputed degree_only = {re['degree_only']:.6f} vs frozen {deg_frozen:.6f}; "
                  f"recomputed ridge = {re['ridge']:.6f} vs frozen {ridge_frozen:.6f}; "
                  f"recomputed permuted control = {re['ridge_permuted']:.6f} vs frozen {perm_frozen:.6f}")
    else:
        check("V07", "ML benchmark table exists", False, "table_p2_ml_benchmark.csv missing")

    # ---- V08: subject-aware model ---------------------------------------------
    sa_path = TREE / "10_TABLES" / "table_p2_subject_aware_model.csv"
    if sa_path.exists():
        sa = pd.read_csv(sa_path)
        ok = len(sa) == 8 and sa["cluster_robust_se"].gt(0).all() and sa["q_bh"].between(0, 1).all()
        sig = sa[sa["q_bh"] < 0.05]["feature"].tolist()
        check("V08", "subject-aware model: 8 features, valid CR1 output",
              ok, f"q<0.05 features: {sig if sig else 'none'}")
    else:
        check("V08", "subject-aware model table exists", False,
              "table_p2_subject_aware_model.csv missing")

    # ---- V09: null arbitration (DEEP: raw records -> independent Outcome C) --
    nf_path = TREE / "06_NULL_MODELS" / "NULL_FEATURE_RESULTS.json"
    ckpt = TREE / "06_NULL_MODELS" / "null_records_checkpoint.jsonl"
    if not nf_path.exists():
        check("V09", "null arbitration exists", False, "NULL_FEATURE_RESULTS.json missing")
    elif not ckpt.exists():
        nf = json.loads(nf_path.read_text())
        surviving = [r["feature"] for r in nf["summary"] if r.get("obs_exceeds_null_p95")]
        check("V09", "null arbitration (raw records unavailable - cannot deep-verify)",
              False,
              f"summary: {len(nf['summary'])} features arbitrated, Outcome C "
              f"recorded: {not surviving}; BUT {ckpt.name} not found in the "
              f"repo (gitignored for size). Restore it from the release "
              f"archive to enable deep verification.")
    else:
        nf = json.loads(nf_path.read_text())
        summ = {r["feature"]: r for r in nf["summary"]}
        null_subjects = [str(s).zfill(4) for s in nf["subjects"]]

        # Observed data, keyed consistently: feature matrix (authoritative
        # degree + features) merged with the primary-estimator residuals.
        res_z = res_p.copy()
        res_z["subject"] = res_z["subject"].astype(str).str.zfill(4)
        fmx = pd.read_parquet(fm_path)
        fmx["subject"] = fmx["subject"].astype(str).str.zfill(4)
        merged = fmx.merge(res_z[["subject", "node", "residual_cis"]],
                           on=["subject", "node"], validate="1:1")
        obs_by_subj: dict[str, dict] = {}
        for s in null_subjects:
            fd = fmx[fmx["subject"] == s].sort_values("node")
            rd = res_z[res_z["subject"] == s].sort_values("node")
            obs_by_subj[s] = {
                "degree": fd["degree"].to_numpy(float),
                "R": rd["residual_cis"].to_numpy(float),
            }

        n_rec = 0
        n_bad_deg, worst_deg_dev = 0, 0.0
        n_bad_rnull, worst_rnull_dev = 0, 0.0
        seeds_seen: set[tuple[str, int]] = set()
        per_null_rho: dict[str, list[float]] = {f: [] for f in NULL_FEATURES}
        with open(ckpt) as fh:
            for line in fh:
                rec = json.loads(line)
                n_rec += 1
                s = str(rec["subject"]).zfill(4)
                seeds_seen.add((s, int(rec["seed"])))
                deg = np.asarray(rec["degree"], float)
                cis = np.asarray(rec["cis_null"], float)
                # (a) exact degree preservation vs the observed graph (multiset)
                o = obs_by_subj.get(s)
                if o is None or len(o["degree"]) != len(deg):
                    n_bad_deg += 1
                    continue
                dev = float(np.abs(np.sort(o["degree"]) - np.sort(deg)).max())
                worst_deg_dev = max(worst_deg_dev, dev)
                if dev > 0.0:
                    n_bad_deg += 1
                # (b) independently re-derive R_null from (cis_null, degree)
                #     via the documented 20-bin quantile-median proxy
                bins = np.quantile(deg, np.linspace(0, 1, 21))
                bins[0] -= 1e-9
                bins[-1] += 1e-9
                bidx = np.digitize(deg, bins[1:-1], right=True)
                fitted = np.array([np.median(cis[bidx == b]) for b in range(20)])[bidx]
                r_ind = cis - fitted
                dev_r = float(np.abs(r_ind - np.asarray(rec["R_null"], float)).max())
                worst_rnull_dev = max(worst_rnull_dev, dev_r)
                if dev_r > 1e-9:
                    n_bad_rnull += 1
                # (c) independent per-null statistic: rho(R_null, feature)
                for f in NULL_FEATURES:
                    x = np.asarray(rec["features"][f], float)
                    per_null_rho[f].append(float(spearmanr(r_ind, x).statistic))

        # (d) pooled null statistics (1,200 records) vs artifact
        stat_bad = []
        for f in NULL_FEATURES:
            arr = np.asarray(per_null_rho[f], float)
            med_i = float(np.median(arr))
            iqr_i = float(np.subtract(*np.quantile(arr, [0.75, 0.25])))
            p95_i = float(np.quantile(np.abs(arr), 0.95))
            if (abs(med_i - float(summ[f]["median_rho_null"])) > 1e-9
                    or abs(iqr_i - float(summ[f]["iqr_rho_null"])) > 1e-9
                    or abs(p95_i - float(summ[f]["abs_rho_p95_null"])) > 1e-9):
                stat_bad.append(f)

        # (e) observed signed median rho recomputed from ALL 801 subjects
        obs_bad = []
        for f in NULL_FEATURES:
            vals = [float(spearmanr(d["residual_cis"].to_numpy(float),
                                    d[f].to_numpy(float)).statistic)
                    for _, d in merged.groupby("subject")]
            obs_med = float(np.median(vals))
            art = float(summ[f]["median_rho_observed"])
            if abs(obs_med - art) > 1e-6:
                obs_bad.append(f"{f}: obs {obs_med:.6f} vs artifact {art:.6f}")

        counts_ok = all(sum(1 for s2, _ in seeds_seen if s2 == s) == 100
                        for s in null_subjects)
        verdict_c = all(not summ[f].get("obs_exceeds_null_p95") for f in NULL_FEATURES)
        ok = (n_rec == 1200
              and len(seeds_seen) == 1200
              and counts_ok
              and n_bad_deg == 0
              and worst_deg_dev == 0.0
              and n_bad_rnull == 0
              and worst_rnull_dev <= 1e-9
              and not stat_bad
              and not obs_bad
              and verdict_c)
        surviving = [f for f in NULL_FEATURES if summ[f].get("obs_exceeds_null_p95")]
        check("V09", "null arbitration DEEP-verified from 1200 raw null records",
              ok,
              f"records = {n_rec}/1200, seeds unique: {len(seeds_seen)} == 1200, "
              f"per-subject counts == 100: {counts_ok}; degree preservation "
              f"violations: {n_bad_deg} (max dev {worst_deg_dev}); R_null "
              f"proxy re-derivation mismatches: {n_bad_rnull} (max dev "
              f"{worst_rnull_dev:.2e}); pooled null-stat mismatches: "
              f"{stat_bad if stat_bad else 'none'}; observed-stat mismatches: "
              f"{obs_bad if obs_bad else 'none'}; Outcome C reproduced: "
              f"{verdict_c} (exceed p95: {surviving if surviving else 'NONE'})")

    # ---- V10: robustness matrix (sign-consistency checked numerically) -------
    rb_path = TREE / "07_ROBUSTNESS" / "ROBUSTNESS_MATRIX.csv"
    if rb_path.exists():
        rb = pd.read_csv(rb_path)
        have = set(rb["analysis"].unique())
        sign_bad: list[str] = []
        if uni_bridge:
            for f in ("bridge", "participation"):
                ref = np.sign(uni_bridge[f])
                sub = rb[(rb["feature"] == f)
                         & (rb["statistic"].str.contains("median within-subject rho", na=False))]
                for _, row in sub.iterrows():
                    if np.sign(float(row["value"])) != ref:
                        sign_bad.append(f"{f}@{row['analysis']}/{row['parameter']}")
        grids_ok = (set(rb[rb["analysis"] == "R2_threshold"]["parameter"].unique()) == {"top1", "top5"}
                    and set(rb[rb["analysis"] == "R5_winsorized_R"]["parameter"].unique()) == {"0.999"}
                    and {"M2_linear", "P_df3", "Q_bin20"}
                    <= set(rb[rb["analysis"] == "R1_estimator"]["parameter"].unique()))
        check("V10", "robustness: R1/R2/R5 grids present + sign-consistent vs Stage 8",
              {"R1_estimator", "R2_threshold", "R5_winsorized_R"} <= have
              and not sign_bad and grids_ok,
              f"families: {sorted(have)}; sign violations: "
              f"{sign_bad if sign_bad else 'none'}")
    else:
        check("V10", "robustness matrix exists", False, "ROBUSTNESS_MATRIX.csv missing")

    # ---- V11: negative controls (bands rechecked numerically) -----------------
    nc_path = TREE / "07_ROBUSTNESS" / "NEGATIVE_CONTROLS.json"
    if nc_path.exists():
        nc = json.loads(nc_path.read_text())
        rows = nc["results"]
        bad: list[str] = []
        for r in rows:
            obs = abs(float(r["median_rho_observed"]))
            if not (obs > float(r["nc1_p95_abs"]) and obs > float(r["nc2_p95_abs"])):
                bad.append(f"{r['feature']}:obs-inside-band")
            if float(r["nc1_p95_abs"]) > 0.01 or float(r["nc2_p95_abs"]) > 0.01:
                bad.append(f"{r['feature']}:band-too-wide")
        min_margin = min(min(float(r["nc1_margin"]), float(r["nc2_margin"])) for r in rows)
        check("V11", "negative controls: observed exceeds NC1/NC2 p95 per feature",
              len(rows) == 8 and not bad,
              f"{len(rows)}/8 features rechecked; violations: "
              f"{bad if bad else 'none'}; min margin = {min_margin:.4f} "
              f"(weak features wmz/kcore expected small)")
    else:
        check("V11", "negative controls exist", False, "NEGATIVE_CONTROLS.json missing")

    # ---- V12: fly case study consistency ---------------------------------------
    me_path = TREE / "11_CASE_STUDIES" / "ME131_MECHANISTIC_PROFILE.csv"
    cat = pd.read_csv(CFG["paths"]["fly_e10b"].replace(
        "e10b_final.json", "../tables/e14_chokepoint_catalogue_v2.csv"))
    me_cat = cat[cat["name"] == "ME.131"].iloc[0]
    if me_path.exists():
        prof = pd.read_csv(me_path)
        cis_row = prof[prof["quantity"].str.startswith("CIS")]
        ok = (len(prof) >= 6
              and np.isclose(float(cis_row["ME131"].iloc[0]),
                             float(me_cat["cis"]), rtol=1e-6))
        check("V12", "ME.131 case profile consistent with frozen catalogue",
              ok, f"catalogue cis = {float(me_cat['cis']):.6f}, "
                  f"excess ratio = {float(me_cat['cis_excess_ratio']):.1f}x")
    else:
        check("V12", "ME.131 case study exists", False,
              "ME131_MECHANISTIC_PROFILE.csv missing")

    # ---- summary ----------------------------------------------------------------
    n_pass = sum(r["pass"] for r in results)
    print(f"\n{n_pass}/{len(results)} checks PASS")
    (TREE / "13_MANUSCRIPT" / "STAGE24_VERIFICATION.json").write_text(
        json.dumps({"n_pass": n_pass, "n_total": len(results),
                    "results": results}, indent=2))
    if n_pass != len(results):
        sys.exit(1)


if __name__ == "__main__":
    main()
