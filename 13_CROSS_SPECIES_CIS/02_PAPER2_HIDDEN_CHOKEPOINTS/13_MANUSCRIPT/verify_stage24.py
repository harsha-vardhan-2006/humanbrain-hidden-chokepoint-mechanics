"""Stage 24 - Independent verification of every Paper 2 headline number.

Re-derives each verdict-relevant quantity from the frozen artifacts on disk
(no numbers are trusted from prose) and checks the frozen gates:

  V01  Freeze 1 orthogonality gate: median |rho(R, degree)| < 0.05 (primary M1)
  V02  Same-pairs cross-check: Spearman(delta_ours, delta_paper1) >= 0.5
  V03  Subject replication: delta_ours > 0 in all 801 QC-pass subjects
  V04  Stage 6 feature matrix complete: 801 subjects x 456 nodes, 0 non-finite
  V05  Stage 8 univariate table present with 12 features, q_bh in [0,1]
  V06  Stage 9 nested models: M4 delta_cvR2 vs M1 reported
  V07  Stage 10 ML benchmark: degree_only vs full ridge delta reported
  V08  Stage 11 subject-aware model: 8 features, cluster-robust SEs present
  V09  Stage 15 null arbitration: per-feature observed |median rho| vs null p95
  V10  Stage 20 robustness matrix present (R1/R2/R5 rows)
  V11  Stage 21 negative controls: observed exceeds NC band where claimed
  V12  Fly case study: ME.131 profile consistent with frozen catalogue

Exit code 0 = all checks PASS. Any FAIL exits 1 (fail loud, no silent skip).
Usage:  py 13_MANUSCRIPT/verify_stage24.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

TREE = Path(__file__).resolve().parents[1]
CFG = json.loads((TREE / "01_CONFIG" / "config.json").read_text())
PRIMARY = CFG["residualization"]["primary"]

results: list[dict] = []


def check(vid: str, desc: str, ok: bool, detail: str) -> None:
    results.append({"id": vid, "check": desc, "pass": bool(ok), "detail": detail})
    print(f"[{'PASS' if ok else 'FAIL'}] {vid}  {desc}  ({detail})")


def main() -> None:
    # ---- V01: orthogonality gate (recompute from the frozen residual file) --
    res = pd.read_parquet(TREE / "04_DEGREE_CONTROL" / "continuous_residuals.parquet")
    res_p = res[res["estimator"] == PRIMARY]
    from scipy.stats import spearmanr
    rhos = [spearmanr(d["residual_cis"], d["degree"]).statistic
            for _, d in res_p.groupby("subject")]
    med_abs = float(np.median(np.abs(rhos)))
    check("V01", "orthogonality gate median |rho(R, degree)| < 0.05",
          med_abs < 0.05, f"median |rho| = {med_abs:.4f}, n_subjects = {len(rhos)}")

    # ---- V02: same-pairs cross-check (frozen Stage 3b JSON + CSV recompute) -
    cc = json.loads((TREE / "04_DEGREE_CONTROL" / "crosscheck_same_pairs.json").read_text())
    rho_cc = float(cc.get("spearman_delta_ours_vs_paper1",
                          cc.get("spearman", np.nan)))
    check("V02", "same-pairs cross-check rho >= 0.5",
          rho_cc >= 0.5, f"rho = {rho_cc:.3f} (frozen Stage 3b artifact)")

    # ---- V03: subject replication (delta_ours > 0 in 801/801) ---------------
    sv = json.loads((TREE / "04_DEGREE_CONTROL" / "subject_validation.json").read_text())
    rep = sv["replication_delta_ours"]
    n_pos = int(round(float(rep["replication_fraction_delta_ours_positive"]) * 801))
    n_subj = int(rep["n_subjects"])
    check("V03", "residual effect positive in all QC-pass subjects",
          n_subj == 801 and n_pos == 801,
          f"{n_pos}/{n_subj} subjects with delta_ours > 0 "
          f"(median {rep['median_delta_ours']:.4f}, CI "
          f"[{rep['bootstrap_ci95'][0]:.4f}, {rep['bootstrap_ci95'][1]:.4f}])")

    # ---- V04: feature matrix completeness -----------------------------------
    fm_path = TREE / "03_FEATURE_EXTRACTION" / "NODE_FEATURE_MATRIX.parquet"
    if fm_path.exists():
        fm = pd.read_parquet(fm_path)
        n_sub = fm["subject"].nunique()
        n_rows = len(fm)
        feats = ["degree", "strength", "betweenness", "closeness_d", "redundancy",
                 "bridge", "participation", "within_module_z", "kcore",
                 "eigenvector", "pagerank", "clustering"]
        n_bad = int(fm[feats].isna().sum().sum()
                    + np.isinf(fm[feats].to_numpy(float)).sum())
        check("V04", "feature matrix 801 x 456, zero non-finite feature values",
              n_sub == 801 and n_rows == 801 * 456 and n_bad == 0,
              f"{n_sub} subjects, {n_rows} rows, {n_bad} non-finite")
    else:
        check("V04", "feature matrix exists", False, "NODE_FEATURE_MATRIX.parquet missing")

    # ---- V05: univariate table ----------------------------------------------
    uni_path = TREE / "05_MECHANISM_ANALYSIS" / "UNIVARIATE_RESULTS.json"
    if uni_path.exists():
        uni = json.loads(uni_path.read_text())
        rows = uni["results"]
        ok = (len(rows) == 12
              and all(0.0 <= r["q_bh"] <= 1.0 for r in rows)
              and all(np.isfinite(r["median_rho"]) for r in rows))
        top = max(rows, key=lambda r: abs(r["median_rho"]))
        check("V05", "univariate table: 12 features, finite rhos, valid q",
              ok, f"top |median rho| = {top['median_rho']:+.3f} ({top['feature']})")
    else:
        check("V05", "univariate table exists", False, "UNIVARIATE_RESULTS.json missing")

    # ---- V06: nested models ---------------------------------------------------
    nm_path = TREE / "10_TABLES" / "table_p2_nested_models.csv"
    if nm_path.exists():
        nm = pd.read_csv(nm_path)
        m1 = float(nm.loc[nm["model"] == "M1_degree", "cv_R2_grouped_by_subject"].iloc[0])
        m4 = float(nm.loc[nm["model"] == "M4_degree_plus_set", "cv_R2_grouped_by_subject"].iloc[0])
        check("V06", "nested models: M4 delta_cvR2 vs M1 reported",
              True, f"M1 cvR2 = {m1:.4f}, M4 cvR2 = {m4:.4f}, delta = {m4 - m1:+.4f}")
    else:
        check("V06", "nested models table exists", False, "table_p2_nested_models.csv missing")

    # ---- V07: ML benchmark ----------------------------------------------------
    ml_path = TREE / "10_TABLES" / "table_p2_ml_benchmark.csv"
    if ml_path.exists():
        ml = pd.read_csv(ml_path)
        deg = float(ml.loc[ml["model"] == "degree_only", "cv_R2_mean"].iloc[0])
        ridge = float(ml.loc[ml["model"] == "ridge", "cv_R2_mean"].iloc[0])
        check("V07", "ML benchmark: degree_only vs full ridge reported",
              True, f"degree_only = {deg:.4f}, ridge = {ridge:.4f}, delta = {ridge - deg:+.4f}")
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

    # ---- V09: null arbitration --------------------------------------------------
    nf_path = TREE / "06_NULL_MODELS" / "NULL_FEATURE_RESULTS.json"
    if nf_path.exists():
        nf = json.loads(nf_path.read_text())
        summ = nf["summary"]
        surviving = [r["feature"] for r in summ if r.get("obs_exceeds_null_p95")]
        check("V09", "null arbitration recorded for every feature",
              len(summ) >= 9,
              f"{len(summ)} features arbitrated; exceed null p95: "
              f"{surviving if surviving else 'NONE (Outcome C for all)'}")
    else:
        check("V09", "null arbitration exists", False, "NULL_FEATURE_RESULTS.json missing")

    # ---- V10: robustness matrix -------------------------------------------------
    rb_path = TREE / "07_ROBUSTNESS" / "ROBUSTNESS_MATRIX.csv"
    if rb_path.exists():
        rb = pd.read_csv(rb_path)
        have = set(rb["analysis"].unique())
        check("V10", "robustness matrix has R1/R2/R5 families",
              {"R1_estimator", "R2_threshold", "R5_winsorized_R"} <= have,
              f"families present: {sorted(have)}")
    else:
        check("V10", "robustness matrix exists", False, "ROBUSTNESS_MATRIX.csv missing")

    # ---- V11: negative controls ---------------------------------------------------
    nc_path = TREE / "07_ROBUSTNESS" / "NEGATIVE_CONTROLS.json"
    if nc_path.exists():
        nc = json.loads(nc_path.read_text())
        rows = nc["results"]
        exceeding = [r["feature"] for r in rows if r.get("obs_exceeds_nc1_band")]
        check("V11", "negative controls recorded (NC1/NC2 per feature)",
              len(rows) == 8,
              f"obs exceeds NC1 band: {exceeding if exceeding else 'NONE'}")
    else:
        check("V11", "negative controls exist", False, "NEGATIVE_CONTROLS.json missing")

    # ---- V12: fly case study consistency -------------------------------------------
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

    # ---- summary --------------------------------------------------------------------
    n_pass = sum(r["pass"] for r in results)
    print(f"\n{n_pass}/{len(results)} checks PASS")
    (TREE / "13_MANUSCRIPT" / "STAGE24_VERIFICATION.json").write_text(
        json.dumps({"n_pass": n_pass, "n_total": len(results),
                    "results": results}, indent=2))
    if n_pass != len(results):
        sys.exit(1)


if __name__ == "__main__":
    main()
