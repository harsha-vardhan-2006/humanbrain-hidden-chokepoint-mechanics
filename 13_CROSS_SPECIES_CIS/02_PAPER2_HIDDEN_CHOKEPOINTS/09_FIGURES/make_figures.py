"""Paper 2 figure set - all panels from frozen artifacts (no recomputation).

Outputs to 09_FIGURES/ (PNG, 150 dpi):
  fig_p2_null_arbitration.png    observed |rho| vs null band per feature
  fig_p2_ml_benchmark.png        cv-R2 by model incl. permuted controls
  fig_p2_subject_aware.png       within-subject standardized beta with CR1 CI
  fig_p2_chokepoint_sensitivity.png  joint-criterion counts vs k
  fig_p2_bio_enrichment.png      cortex under-representation in top-CIS
  fig_p2_fly_case.png            ME.131 z-profile vs degree-matched peers
Existing (Stage 3/8, kept): degree_vs_CIS, degree_vs_residual,
residual_distribution, fig_p2_feature_associations.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

TREE = Path(__file__).resolve().parents[1]
FIG = TREE / "09_FIGURES"
FIG.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"figure.dpi": 150, "font.size": 9,
                     "axes.titlesize": 10, "axes.labelsize": 9})

# 1 ---- null arbitration
nulls = json.loads((TREE / "06_NULL_MODELS" / "NULL_FEATURE_RESULTS.json").read_text())
s = pd.DataFrame(nulls["summary"]).sort_values("abs_rho_p95_null")
fig, ax = plt.subplots(figsize=(6.3, 3.6))
y = np.arange(len(s))
ax.barh(y, s["abs_rho_p95_null"], color="#cfd8ec", label="null |rho| p95 (degree-preserving)")
ax.scatter(s["median_rho_observed"].abs(), y, color="#1a3a6b", zorder=3, s=28,
           label="observed |median rho|")
ax.set_yticks(y, s["feature"])
ax.set_xlabel("|Spearman rho(R, feature)| (within-graph pooled)")
ax.set_title("Stage 15 null arbitration: observed associations sit inside\n"
             "degree-preserving null bands (Outcome C, all features)")
ax.legend(loc="lower right", frameon=False)
fig.tight_layout()
fig.savefig(FIG / "fig_p2_null_arbitration.png")
plt.close(fig)

# 2 ---- ML benchmark
ml = json.loads((TREE / "08_STATISTICS" / "ML_BENCHMARK.json").read_text())
m = pd.DataFrame(ml["results"])
fig, ax = plt.subplots(figsize=(5.4, 3.4))
x = np.arange(len(m))
ax.bar(x - 0.2, m["cv_R2_mean"], 0.38, yerr=m["cv_R2_sd"], label="observed R",
       color="#2a5db0", capsize=2)
ax.bar(x + 0.2, m["cv_R2_permuted_mean"], 0.38, yerr=m["cv_R2_permuted_sd"],
       label="permuted-R control", color="#b0b8c9", capsize=2)
ax.axhline(0, color="k", lw=0.8)
ax.set_xticks(x, m["model"])
ax.set_ylabel("out-of-sample cv-R2\n(5-fold grouped by subject x 3 seeds)")
ax.set_ylim(-1.2, 0.8)
ax.set_title("Residual is learnable from network position\n(ridge +0.574 vs degree-only ~ 0)")
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(FIG / "fig_p2_ml_benchmark.png")
plt.close(fig)

# 3 ---- subject-aware betas
sa = pd.read_csv(TREE / "10_TABLES" / "table_p2_subject_aware_model.csv")
sa = sa.sort_values("beta_standardized")
fig, ax = plt.subplots(figsize=(5.8, 3.4))
y = np.arange(len(sa))
ax.errorbar(sa["beta_standardized"] * 1e3, y,
            xerr=1.96 * sa["cluster_robust_se"] * 1e3, fmt="o", ms=4,
            color="#1a3a6b", capsize=2, lw=1)
ax.axvline(0, color="k", lw=0.8)
ax.set_yticks(y, sa["feature"])
ax.set_xlabel("within-subject standardized beta (x1e-3), CR1 95% CI")
ax.set_title("Subject-aware model: all 8 features q < 1e-7\n(clustered by subject, N = 801)")
fig.tight_layout()
fig.savefig(FIG / "fig_p2_subject_aware.png")
plt.close(fig)

# 4 ---- chokepoint sensitivity
sens = pd.read_csv(TREE / "12_SYNTHESIS" / "CHOKEPOINT_SENSITIVITY.csv")
fig, ax = plt.subplots(figsize=(5.0, 3.2))
ax.plot(sens["top_frac"] * 100, sens["n_cis_top"], "o--", color="#9aa7bd",
        label="CIS top-k nodes")
ax.plot(sens["top_frac"] * 100, sens["n_both"], "s-", color="#1a3a6b",
        label="CIS top-k AND residual top-k")
ax.plot(sens["top_frac"] * 100, sens["n_candidates_with_position"], "^-",
        color="#8a1c1c", label="+ bridge upper half (candidates)")
for _, r in sens.iterrows():
    ax.annotate(str(int(r["n_candidates_with_position"])),
                (r["top_frac"] * 100, r["n_candidates_with_position"]),
                textcoords="offset points", xytext=(0, 6), ha="center", fontsize=8)
ax.set_xlabel("k (% of 456 nodes)")
ax.set_ylabel("node count")
ax.set_title("Operational chokepoint candidates vs threshold k\n(1 / 2 / 3 / 7 nodes at 1/2/5/10%)")
ax.legend(frameon=False, fontsize=8)
fig.tight_layout()
fig.savefig(FIG / "fig_p2_chokepoint_sensitivity.png")
plt.close(fig)

# 5 ---- biological enrichment (major_structure, top10_CIS rows)
enr = json.loads((TREE / "results_annotation" / "BIOLOGICAL_ENRICHMENT.json").read_text())
rows = [r for r in enr["enrichment"]
        if r["set"] == "top10_CIS" and r["category_col"] == "major_structure"
        and r["n_total"] > 0]
rows = sorted(rows, key=lambda r: r["enrichment_pp"])
fig, ax = plt.subplots(figsize=(6.0, 3.4))
y = np.arange(len(rows))
vals = [r["enrichment_pp"] for r in rows]
cols = ["#8a1c1c" if v < 0 else "#2a5db0" for v in vals]
sig = [r["q_bh"] < 0.05 for r in rows]
ax.barh(y, vals, color=cols)
for i, (r, sv) in enumerate(zip(rows, sig)):
    if sv:
        ax.text(r["enrichment_pp"], i, " *", va="center",
                color="k" if r["enrichment_pp"] > 0 else "w", fontsize=10)
ax.set_yticks(y, [f"{r['category']} (n={r['n_total']})" for r in rows])
ax.axvline(0, color="k", lw=0.8)
ax.set_xlabel("share difference vs expected (top-10% CIS set)")
ax.set_title("Top-CIS nodes under-represent CORTEX\n(* q < 0.05, 10k permutations; cell-type rows NOT_ESTABLISHED)")
fig.tight_layout()
fig.savefig(FIG / "fig_p2_bio_enrichment.png")
plt.close(fig)

# 6 ---- fly case study
prof = pd.read_csv(TREE / "11_CASE_STUDIES" / "ME131_MECHANISTIC_PROFILE.csv")
prof = prof[prof["quantity"] != "CIS (frozen k=8 panel)"]  # log-scale outlier; shown in text
prof = prof.sort_values("z_vs_peers")
fig, ax = plt.subplots(figsize=(6.0, 3.2))
y = np.arange(len(prof))
cols = ["#8a1c1c" if v > 0 else "#2a5db0" for v in prof["z_vs_peers"]]
ax.barh(y, prof["z_vs_peers"], color=cols)
ax.axvline(0, color="k", lw=0.8)
ax.set_yticks(y, [q.replace(" (sampled k=512)", "") for q in prof["quantity"]])
ax.set_xlabel("ME.131 z-score vs 86 degree-matched target peers")
ax.set_title("Fly case study (ME.131): elevated directed betweenness\n(CIS z = +23.4, not shown; case study only)")
fig.tight_layout()
fig.savefig(FIG / "fig_p2_fly_case.png")
plt.close(fig)

print("figures written:", sorted(p.name for p in FIG.glob("fig_p2_*.png")))
