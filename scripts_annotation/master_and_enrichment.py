"""Build the master CIS + biology table (Paper 2 node level) and run the
biological enrichment + degree-controlled association analyses.

Inputs (all frozen or Freeze-1 outputs; consumed read-only):
  00_MANIFEST/manifests/atlas_4S456_system_labels.csv        (atlas labels)
  results_annotation/human_node_biological_annotations.csv   (evidence-leveled)
  04_CIS/population_cis.csv                                  (per-subject CIS)
  04_DEGREE_CONTROL/continuous_residuals.parquet (M1 residuals per subject-node)
  09_TABLES/table_07_null_results.csv                        (per-node null z/p/q)

Outputs:
  results_annotation/human_cis_biological_master.csv
  results_annotation/BIOLOGICAL_ENRICHMENT.json
  10_TABLES/table_p2_bio_enrichment.csv
  10_TABLES/table_p2_degree_controlled.csv

Evidence discipline: nodes are PARCELS, not neurons. Enrichment categories
come from the annotation table only (structure / hemisphere / functional
network). Cell-type fields are NOT_AVAILABLE everywhere and are therefore
reported as NOT_ESTABLISHED, never tested.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata

TREE = Path(__file__).resolve().parents[1]
STUDY = TREE.parent
ANN = TREE / "results_annotation"
TBL = TREE / "10_TABLES"
SEED = 20270927
N_PERM = 10_000
TOP_FRAC = 0.10  # high-CIS / high-residual sets (node level)


def build_master() -> pd.DataFrame:
    ann = pd.read_csv(ANN / "human_node_biological_annotations.csv")
    pop = pd.read_csv(STUDY / "04_CIS" / "population_cis.csv")
    nul = pd.read_csv(STUDY / "09_TABLES" / "table_07_null_results.csv")
    res = pd.read_parquet(TREE / "04_DEGREE_CONTROL" / "continuous_residuals.parquet")
    res = res[res["estimator"] == "M1_spline4_raw"]

    # node-level aggregates over the 801 QC subjects
    g = pop.groupby("node").agg(
        CIS=("cis", "median"), degree=("degree", "median"),
        weighted_degree=("strength", "median"))
    # expected CIS per node: fitted = cis - residual, median across subjects
    res["fitted"] = res["cis"] - res["residual_cis"]
    exp = res.groupby("node")["fitted"].median().rename("expected_CIS")
    resid = res.groupby("node")["residual_cis"].median().rename("residual")

    m = (ann.set_index("node_id")
         .join(g).join(exp).join(resid)
         .join(nul.set_index("node")))
    m["CIS_rank"] = m["CIS"].rank(ascending=False)
    m["residual_rank"] = m["residual"].rank(ascending=False)
    m["significant"] = m["q_bh"] < 0.05
    # graph is undirected: in/out degree are each half the recorded degree
    m["in_degree"] = m["degree"] / 2
    m["out_degree"] = m["degree"] / 2
    m = m.reset_index().rename(columns={"index": "node_id", "node": "node_id"})
    return m


def perm_enrichment(labels: pd.Series, values: np.ndarray, top_mask: np.ndarray,
                    rng: np.random.Generator, n_perm: int = N_PERM) -> dict:
    """Enrichment of `labels` categories among top-`values` nodes.

    observed  = share of category c among the top set
    expected  = share of category c overall (population)
    stat      = observed - expected (percentage points)
    perm p    = two-sided label-permutation p for |stat|
    """
    cats = labels.to_numpy()
    out = {}
    uniq, inv = np.unique(cats, return_inverse=True)
    n_top = int(top_mask.sum())
    base_share = np.array([(inv == c).mean() for c in range(len(uniq))])
    obs_share = np.array([(inv[top_mask] == c).sum() / max(n_top, 1)
                          for c in range(len(uniq))])
    stat_obs = obs_share - base_share
    stats = np.empty((n_perm, len(uniq)))
    for p in range(n_perm):
        pm = rng.permutation(len(cats))[:n_top]
        s = np.array([(inv[pm] == c).sum() / max(n_top, 1)
                      for c in range(len(uniq))])
        stats[p] = s - base_share
    for c, name in enumerate(uniq):
        extreme = np.abs(stats[:, c] - stat_obs[c] + stat_obs[c])
        # two-sided: null |stat| >= |observed stat|
        p_val = float((1 + (np.abs(stats[:, c]) >= abs(stat_obs[c]) - 1e-12).sum())
                      / (n_perm + 1))
        boot = stats[:, c]
        out[str(name)] = {
            "n_top": int((top_mask & (inv == c)).sum()),
            "n_total": int((inv == c).sum()),
            "observed_share": float(obs_share[c]),
            "expected_share": float(base_share[c]),
            "enrichment_pp": float(stat_obs[c]),
            "perm_p_two_sided": p_val,
            "ci95_null_stat": [float(np.quantile(boot, 0.025)),
                               float(np.quantile(boot, 0.975))],
        }
    return out


def fdr_bh(pvals: np.ndarray) -> np.ndarray:
    p = np.asarray(pvals, float)
    order = np.argsort(p)
    ranked = p[order] * len(p) / np.arange(1, len(p) + 1)
    ranked = np.minimum.accumulate(ranked[::-1])[::-1]
    out = np.empty_like(ranked)
    out[order] = np.minimum(ranked, 1.0)
    return out


def main() -> None:
    m = build_master()
    m.to_csv(ANN / "human_cis_biological_master.csv", index=False)
    print(f"master table: {len(m)} nodes -> "
          f"results_annotation/human_cis_biological_master.csv")

    rng = np.random.default_rng(SEED)
    top_cis = (rankdata(-m["CIS"]) <= int(TOP_FRAC * len(m)))
    top_res = (rankdata(-m["residual"]) <= int(TOP_FRAC * len(m)))

    results = {"n_perm": N_PERM, "seed": SEED, "top_frac": TOP_FRAC,
               "note": "node-level; labels from evidence-leveled annotation "
                       "table; cell-type fields are NOT_AVAILABLE (parcels "
                       "are not cell types) hence NOT_ESTABLISHED"}
    rows = []
    for set_name, mask in (("top10_CIS", top_cis), ("top10_residual", top_res)):
        for col in ("major_structure", "hemisphere", "functional_network",
                    "cortical_status"):
            enr = perm_enrichment(m[col], m["CIS"].to_numpy(), mask, rng)
            for cat, d in enr.items():
                rows.append({"set": set_name, "category_col": col,
                             "category": cat, **d})
    enr_df = pd.DataFrame(rows)
    # FDR within (set, category_col) family
    enr_df["q_bh"] = enr_df.groupby(["set", "category_col"])["perm_p_two_sided"] \
        .transform(lambda p: fdr_bh(p.to_numpy()))
    TBL.mkdir(exist_ok=True)
    enr_df.to_csv(TBL / "table_p2_bio_enrichment.csv", index=False)
    results["enrichment"] = enr_df.to_dict(orient="records")
    (ANN / "BIOLOGICAL_ENRICHMENT.json").write_text(json.dumps(results, indent=2))

    # degree-controlled association: residual ~ category + log_degree
    # (categorical -> ANOVA-style: compare within-category Spearman(R,k) and
    #  the category coefficient in OLS on ranks; permutation p, 5,000 draws)
    from scipy.stats import spearmanr
    lr = np.log10(m["degree"].to_numpy(float))
    R = m["residual"].to_numpy(float)
    dctrl = []
    for col in ("major_structure", "functional_network", "hemisphere"):
        cats = m[col].astype("category").cat.codes.to_numpy()
        uniq = np.unique(cats)
        # partial Spearman: rank-residualize R and category on log_degree
        rr = R - np.polyval(np.polyfit(lr, rankdata(R), 1), lr)
        cc = cats - np.polyval(np.polyfit(lr, cats, 1), lr)
        rho_part = spearmanr(rr, cc).statistic
        rng2 = np.random.default_rng(SEED + 1)
        null = [spearmanr(rng2.permutation(rr), cc).statistic
                for _ in range(5_000)]
        p_perm = float((1 + np.sum(np.abs(null) >= abs(rho_part))) / 5_001)
        dctrl.append({"category_col": col, "n_categories": int(len(uniq)),
                      "partial_spearman_residual_vs_category_given_log_degree":
                          float(rho_part), "perm_p": p_perm})
    dc = pd.DataFrame(dctrl)
    dc["q_bh"] = fdr_bh(dc["perm_p"].to_numpy())
    dc.to_csv(TBL / "table_p2_degree_controlled.csv", index=False)
    results["degree_controlled"] = dc.to_dict(orient="records")
    (ANN / "BIOLOGICAL_ENRICHMENT.json").write_text(json.dumps(results, indent=2))

    print("\nTop enrichment rows (|enrichment_pp| largest, q<0.05):")
    sig = enr_df[enr_df.q_bh < 0.05].reindex(
        enr_df.q_bh.where(enr_df.q_bh < 0.05).abs().sub(1).abs().sort_values().index)
    show = enr_df[enr_df.q_bh < 0.05].copy()
    show["abspp"] = show.enrichment_pp.abs()
    print(show.nlargest(10, "abspp")[
        ["set", "category_col", "category", "enrichment_pp",
         "perm_p_two_sided", "q_bh"]].to_string(index=False))
    print("\nDegree-controlled (partial Spearman):")
    print(dc.to_string(index=False))
    print("\nNOT_ESTABLISHED: cell_class/neuronal_class/E-I/neurotransmitter/"
          "transcriptomic enrichment (fields NOT_AVAILABLE for parcels).")


if __name__ == "__main__":
    main()
