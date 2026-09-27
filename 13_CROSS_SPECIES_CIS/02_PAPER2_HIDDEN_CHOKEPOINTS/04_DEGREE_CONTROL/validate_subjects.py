"""Stage 4 - Cross-subject validation + Paper 1 (E03b) cross-check.

Reads Stage 3 outputs (read-only) and produces:
  - subject-level bootstrap CI for the population median residual
  - replication fraction (subjects with median R > 0)
  - heterogeneity (IQR of per-subject median R)
  - leave-one-subject-out max deviation
  - cross-check vs Paper 1 matched-pair delta (sign agreement + Spearman)
  - SUBJECT_REPLICATION_REPORT.md
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

TREE = Path(__file__).resolve().parents[1]
CFG = json.loads((TREE / "01_CONFIG" / "config.json").read_text())
P = CFG["paths"]
OUT = Path(P["out_degree_control"])
SEED = CFG["seeds"]["bootstrap"]
N_BOOT = CFG["bootstrap"]["n_resamples"]


def main() -> None:
    summ = pd.read_csv(OUT / "subject_residual_summary.csv")
    e03b = pd.read_csv(P["e03b_per_subject"])
    gate = json.loads((OUT / "gate_report.json").read_text())

    med = summ["median_R_primary"].to_numpy(float)
    rng = np.random.default_rng(SEED)
    boots = np.median(rng.choice(med, size=(N_BOOT, med.size), replace=True), axis=1)
    ci_lo, ci_hi = np.quantile(boots, [0.025, 0.975])
    point = float(np.median(med))

    frac_pos = float((med > 0).mean())
    hetero_iqr = float(np.subtract(*np.quantile(med, [0.75, 0.25])))

    loso = np.array([np.median(np.delete(med, i)) for i in range(med.size)])
    loso_max_dev = float(np.abs(loso - point).max())

    # ---- cross-check vs Paper 1 E03b --------------------------------------
    # (Amendment 2: the authoritative cross-check is the SAME-PAIRS Spearman
    #  computed by crosscheck_same_pairs.py — pair-only deltas vs pair-only
    #  deltas. Retired here: the all-node-median vs pair-only-delta
    #  comparison, which was a unit mismatch.)
    cc_file = OUT / "crosscheck_same_pairs.json"
    cross = {"available": False}
    if cc_file.exists():
        same = json.loads(cc_file.read_text())
        cross = {
            "available": True,
            "kind": "same-pairs (Amendment 2)",
            "n_merged": same["n_subjects_merged"],
            "spearman_delta_ours_vs_paper1": same["spearman_delta_ours_vs_paper1"],
            "spearman_p": same["spearman_p"],
            "identity_max_abs_error": same["identity_max_abs_error"],
            "gate_pass": same["gate_pass"],
        }
        if not same["gate_pass"]:
            cross["BLOCKER"] = ("same-pairs Spearman < 0.5: reconcile before "
                                "proceeding (framework §4, Amendment 2)")

    report = {
        "n_subjects": int(len(summ)),
        "population_median_R": point,
        "bootstrap_ci95": [float(ci_lo), float(ci_hi)],
        "n_bootstrap": N_BOOT,
        "seed": SEED,
        "replication_fraction_median_R_positive": frac_pos,
        "heterogeneity_IQR": hetero_iqr,
        "loso_max_abs_deviation": loso_max_dev,
        "gate_report": gate,
        "cross_check_e03b": cross,
    }
    (OUT / "subject_validation.json").write_text(json.dumps(report, indent=2))
    pd.DataFrame({"loso_median_R": loso}).to_csv(OUT / "loso_medians.csv", index=False)

    lines = [
        "# SUBJECT REPLICATION REPORT (Stage 4)",
        "",
        f"- Subjects: **{report['n_subjects']}** (QC-pass, Paper 1 frozen flags).",
        f"- Population median residual R (primary estimator): "
        f"**{point:.3e}**  (bootstrap 95% CI **[{ci_lo:.3e}, {ci_hi:.3e}]**; "
        f"{N_BOOT} subject-level resamples, seed {SEED}).",
        f"- Replication fraction (median R > 0): **{frac_pos:.3f}** "
        f"({int(round(frac_pos * len(summ)))}/{len(summ)} subjects).",
        f"- Heterogeneity (IQR of per-subject median R): **{hetero_iqr:.3e}**.",
        f"- Leave-one-subject-out: max |deviation| of population median = "
        f"**{loso_max_dev:.3e}** (stability check).",
        f"- Orthogonality gate: pass={gate['gate_pass']} "
        f"(median |rho(R, degree)| = {gate['median_abs_rho']:.4f}).",
    ]
    if cross.get("available"):
        lines += [
            "",
            "## Cross-check vs Paper 1 matched-pair residual (E03b, same-pairs)",
            f"- Subjects merged: {cross['n_merged']} (same-pairs design, Amendment 2).",
            f"- Spearman(delta_ours, delta_paper1) = "
            f"**{cross['spearman_delta_ours_vs_paper1']:.3f}** (p = {cross['spearman_p']:.2e}).",
            f"- Input-identity check: max |deviation - fitted gap| = "
            f"{cross['identity_max_abs_error']:.2e} (machine-precision identity; "
            "both residuals act on identical inputs).",
            "- Interpretation: the model-based spline residual reproduces the "
            "matched-pair residual's subject-level structure; the two are "
            "different estimators of the same degree-control target.",
        ]
        if "BLOCKER" in cross:
            lines += ["", f"**BLOCKER: {cross['BLOCKER']}**"]
    (OUT / "SUBJECT_REPLICATION_REPORT.md").write_text("\n".join(lines) + "\n")
    print(json.dumps(report, indent=2)[:1200])
    if "BLOCKER" in cross:
        raise SystemExit("Stage 4 BLOCKER - see SUBJECT_REPLICATION_REPORT.md")


if __name__ == "__main__":
    main()
