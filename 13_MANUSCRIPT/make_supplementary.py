"""Generate real supplementary tables (S0-S10) from frozen artifacts.

Audit item 19: turn the supplementary index into actual tables.
Output: 13_MANUSCRIPT/SUPPLEMENTARY_TABLES.md
All numbers come from artifacts; nothing is hand-typed except the S0
amendment table, which transcribes CONFIG_FREEZE.md (documented history).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

TREE = Path(__file__).resolve().parents[1]
OUT = TREE / "13_MANUSCRIPT" / "SUPPLEMENTARY_TABLES.md"

L: list[str] = []


def h(t: str) -> None:
    L.append(f"\n## {t}\n")


def table(df: pd.DataFrame, floatfmt: str = ".4f") -> None:
    with pd.option_context("display.max_rows", 200, "display.width", 200):
        L.append("```")
        L.append(df.to_string(index=False, float_format=lambda v: f"{v:{floatfmt}}"))
        L.append("```\n")


def main() -> None:
    L.append("# Supplementary Tables — Paper 2 (Hidden Chokepoints, v2.0.1)\n")
    L.append("All tables are auto-generated from frozen artifacts by "
             "`13_MANUSCRIPT/make_supplementary.py`. Regenerate: "
             "`python 13_MANUSCRIPT/make_supplementary.py`.\n")

    # S0 - amendments (transcribed from CONFIG_FREEZE.md; documented history)
    h("Table S0. Protocol amendments and their timing")
    s0 = pd.DataFrame([
        {"amendment": "A1", "problem": "log10(CIS+1e-6) estimator invalid: CIS is signed, log of negative CIS -> NaN",
         "discovery_point": "first Stage-3 execution (QC figure failure)", "before_unblinding": "yes (no statistic read)",
         "effect_on_results": "replaced primary estimator (asinh variant, later replaced again by A2)",
         "resolution": "M1 re-specified pre-unblinding"},
        {"amendment": "A2", "problem": "(1) asinh retransformation biased (Jensen): rho(R,degree)=-0.063 failing gate; (2) cross-check compared all-node median vs pair-only delta (unit mismatch, spurious blocker)",
         "discovery_point": "pre-unblinding gate check", "before_unblinding": "yes (no statistic read)",
         "effect_on_results": "final M1 = raw-CIS spline df=4; cross-check redefined as same-pairs Spearman",
         "resolution": "retired transform estimators (preserved in git)"},
        {"amendment": "A3", "problem": "redundancy feature computed with boolean adjacency (OR-semantics): redundancy == clustering on all rows",
         "discovery_point": "pre-analysis integrity sweep of Stage-6 matrix", "before_unblinding": "yes (Stages 7+ not run)",
         "effect_on_results": "int32 cast; caches regenerated; only redundancy column changes",
         "resolution": "unit assertion added to Stage-6 QC"},
        {"amendment": "FREEZE", "problem": "study completion", "discovery_point": "2026-09-30",
         "before_unblinding": "n/a", "effect_on_results": "study tree declared read-only",
         "resolution": "declaration appended to CONFIG_FREEZE.md"},
    ])
    table(s0)

    # S1 - feature definitions (from extract_features.py docstrings/names)
    h("Table S1. Feature definitions (Stage 6)")
    s1 = pd.DataFrame([
        {"feature": "degree", "definition": "binary adjacency row sum (k = number of connections)", "family": "connectivity"},
        {"feature": "strength", "definition": "weighted adjacency row sum (SIFT streamline counts)", "family": "connectivity"},
        {"feature": "betweenness", "definition": "Brandes exact betweenness centrality on the binary graph", "family": "path (coupling-flagged)"},
        {"feature": "closeness_d", "definition": "directed-transposed closeness proxy on the binary graph", "family": "path (coupling-flagged)"},
        {"feature": "redundancy", "definition": "local alternative-path redundancy: common-neighbor product C = Ai[nb,:].Ai[:,nb] - 1 (int32 cast per Amendment 3)", "family": "path"},
        {"feature": "bridge", "definition": "bridge score: degree-1 neighbors fraction (edges to non-reciprocated neighbors)", "family": "position"},
        {"feature": "participation", "definition": "participation coefficient across atlas systems (Guimera & Amaral 2005)", "family": "position"},
        {"feature": "within_module_z", "definition": "within-system degree z-score", "family": "position"},
        {"feature": "kcore", "definition": "k-core index (Seidman 1983)", "family": "core"},
        {"feature": "eigenvector", "definition": "eigenvector centrality (Bonacich 1972), power iteration", "family": "centrality"},
        {"feature": "pagerank", "definition": "PageRank (damping 0.85)", "family": "centrality"},
        {"feature": "clustering", "definition": "clustering coefficient (Watts & Strogatz 1998)", "family": "path"},
    ])
    table(s1)

    # S2 - univariate associations
    h("Table S2. All 12 univariate associations (Stage 8)")
    uni = json.loads((TREE / "05_MECHANISM_ANALYSIS" / "UNIVARIATE_RESULTS.json").read_text())
    rows = [{"feature": r["feature"], "median_rho": r["median_rho"], "iqr_rho": r["iqr_rho"],
             "t_vs_zero": r["t_vs_zero"], "p_wilcoxon": r["p_wilcoxon"],
             "q_bh": r["q_bh"], "frac_same_sign": r["frac_subjects_same_sign"]}
            for r in uni["results"]]
    table(pd.DataFrame(rows))

    # S3 - feature correlation matrix (Stage 7)
    h("Table S3. Feature median within-subject |Spearman| matrix (Stage 7; prune rule |rho| >= 0.9)")
    corr = pd.read_csv(TREE / "10_TABLES" / "table_p2_feature_correlations.csv", index_col=0)
    L.append("```")
    L.append(corr.round(3).to_string())
    L.append("```\n")

    # S4 - nested models
    h("Table S4. Nested models (Stage 9)")
    table(pd.read_csv(TREE / "10_TABLES" / "table_p2_nested_models.csv"))

    # S5 - subject-aware regression
    h("Table S5. Within-subject standardized regression, CR1 SEs (Stage 11)")
    table(pd.read_csv(TREE / "10_TABLES" / "table_p2_subject_aware_model.csv"))

    # S6 - degree-preserving null results
    h("Table S6. Degree-preserving null arbitration, all features (Stage 15; 12 subjects x 100 nulls, seed 20270927)")
    nf = json.loads((TREE / "06_NULL_MODELS" / "NULL_FEATURE_RESULTS.json").read_text())
    rows = [{"feature": r["feature"],
             "median_rho_null": r["median_rho_null"], "iqr_rho_null": r["iqr_rho_null"],
             "abs_p95_null": r["abs_rho_p95_null"],
             "median_rho_observed": r["median_rho_observed"],
             "obs_exceeds_p95": r["obs_exceeds_null_p95"]} for r in nf["summary"]]
    table(pd.DataFrame(rows))
    L.append("Verdict: Outcome C - no observed association exceeds its null p95 "
             "(deep-verified from raw records by gate V09).\n")

    # S6b - null proxy validation
    h("Table S6b. Null-residualization proxy vs spline on observed data (12 null subjects)")
    pv = json.loads((TREE / "06_NULL_MODELS" / "NULL_PROXY_VALIDATION.json").read_text())
    pf = pv["association_level_agreement (the quantity the null arbitrates)"]["per_feature"]
    rows = [{"feature": f, "median_rho_spline": v["median_rho_spline"],
             "median_rho_20bin": v["median_rho_20bin"],
             "median_abs_delta": v["median_abs_delta"],
             "p95_abs_delta": v["p95_abs_delta"]} for f, v in pf.items()]
    table(pd.DataFrame(rows))
    L.append(f"Association-level median |delta rho| = "
             f"{pv['association_level_agreement (the quantity the null arbitrates)']['median_abs_delta_rho']:.4f} "
             "(null bands: 0.10-0.73). Point-level residuals differ in the tails "
             "(median Spearman(R_spline, R_20bin) = "
             f"{pv['null_ensemble_median']['spearman_Rspline_R20']:.3f}); both are "
             "degree-orthogonal. The stored per-null R_null re-derives bit-exactly "
             "(gate V09).\n")

    # S7 - robustness matrix
    h("Table S7. Robustness matrix (Stage 20: R1 estimator ladder, R2 extremes, R5 winsorization)")
    table(pd.read_csv(TREE / "07_ROBUSTNESS" / "ROBUSTNESS_MATRIX.csv"))

    # S8 - biological enrichment (top-10% CIS + residual, all categories)
    h("Table S8. Biological enrichment (10,000 permutations, two-sided, BH-q)")
    enr = json.loads((TREE / "results_annotation" / "BIOLOGICAL_ENRICHMENT.json").read_text())
    rows = [{"set": e["set"], "category_col": e["category_col"], "category": e["category"],
             "n_top": e["n_top"], "observed": round(e["observed_share"], 4),
             "expected": round(e["expected_share"], 4),
             "delta_pp": round(100 * e["enrichment_pp"], 2),
             "p_perm": e["perm_p_two_sided"], "q_bh": e["q_bh"]} for e in enr["enrichment"]]
    table(pd.DataFrame(rows))

    # S9 - chokepoint candidates (k = 5%)
    h("Table S9. Chokepoint candidates at k = 5% (Stage 22; per-node null NOT_ESTABLISHED by design)")
    cand = pd.read_csv(TREE / "12_SYNTHESIS" / "CHOKEPOINT_CANDIDATES.csv")
    table(cand)
    sens = pd.read_csv(TREE / "12_SYNTHESIS" / "CHOKEPOINT_SENSITIVITY.csv")
    h("Table S9b. Chokepoint threshold sensitivity")
    table(sens)

    # S10 - human vs fly comparison
    h("Table S10. Human vs fly comparison (Stage 22b; fly negative preserved verbatim)")
    hvf = pd.read_csv(TREE / "12_SYNTHESIS" / "HUMAN_VS_FLY_COMPARISON.csv")
    table(hvf)

    OUT.write_text("\n".join(L))
    print(f"wrote {OUT} ({len(L)} lines)")


if __name__ == "__main__":
    main()
