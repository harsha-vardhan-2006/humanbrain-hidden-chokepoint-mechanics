"""Stages 12-13 (fly side) - Fly connectome features + ME.131 case study.

Builds the directed FAFB v783 binary graph from the frozen fly edge table
(fruitfly/data/processed/graph_pairs.parquet, READ-ONLY), computes per-neuron
features for the 3,518 pre-registered CIS targets (e07_annotated.parquet),
and produces the ME.131 mechanistic profile vs degree-matched peers.

Fly CIS values are consumed FROZEN from Paper 1 artifacts (e07_annotated:
cis = k=8 panel). No fly CIS is recomputed (different estimator; documented
in MATHEMATICAL_FRAMEWORK section 7).

Outputs (11_CASE_STUDIES/):
  fly_target_features.parquet   (3,518 targets x features)
  ME131_MECHANISTIC_PROFILE.csv
  ME131_CASE_STUDY.md
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import shortest_path

TREE = Path(__file__).resolve().parents[1]
REPO = TREE.parents[1]                       # humanbrain repo root
FLY = REPO.parent / "fruitfly"CFG = json.loads((TREE / "01_CONFIG" / "config.json").read_text())
OUT = TREE / "11_CASE_STUDIES"
CASE = "ME.131"


def sampled_betweenness_directed(A, n_pivots=512, seed=20270927) -> np.ndarray:
    """Sampled DIRECTED betweenness (Brandes dependency accumulation on a
    fixed random pivot set).

    Full-exact Brandes is infeasible at 139,255 nodes / 3.7M edges in this
    environment (O(n*m) pure-Python; the exact per-source predecessor lists
    alone exceed available memory). The fly study itself pre-registered
    sampled betweenness with k=512 sources for target selection, so the
    same estimator (k=512, frozen seed) is used here; values are consumed
    descriptively in the Stage 13 case-study profile only.
    """
    n = A.shape[0]
    AT = A.T.tocsr()  # in-edges for predecessor lookups
    rng = np.random.default_rng(seed)
    pivots = rng.choice(n, size=min(n_pivots, n), replace=False)
    bc = np.zeros(n)
    indptr, indices = A.indptr, A.indices
    aiptr, aindices = AT.indptr, AT.indices
    for s in pivots:
        dist = np.full(n, -1.0)
        dist[s] = 0.0
        sigma = np.zeros(n)
        sigma[s] = 1.0
        levels = []
        frontier = np.array([s])
        d = 0
        while frontier.size:
            d += 1
            parts = [indices[indptr[v]:indptr[v + 1]] for v in frontier]
            neigh = np.unique(np.concatenate(parts)) if parts else np.array([], dtype=int)
            newly = neigh[dist[neigh] < 0]
            if newly.size == 0:
                break
            dist[newly] = float(d)
            for w in newly:
                ins = aindices[aiptr[w]:aiptr[w + 1]]
                ins = ins[dist[ins] == d - 1]
                sigma[w] = sigma[ins].sum()
            levels.append(newly)
            frontier = newly
        delta = np.zeros(n)
        for level in reversed(levels):
            for w in level:
                if w == s or sigma[w] == 0:
                    continue
                ins = aindices[aiptr[w]:aiptr[w + 1]]
                ins = ins[dist[ins] == dist[w] - 1]
                coef = (1.0 + delta[w]) / sigma[w]
                delta[ins] += sigma[ins] * coef
                bc[w] += delta[w]
    bc *= n / len(pivots)          # scale pivot sample to graph size
    return bc / ((n - 1) * (n - 2))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    pairs = pd.read_parquet(FLY / "data" / "processed" / "graph_pairs.parquet")
    # frozen convention (fly build): collapse to unique pairs, syn_count sum;
    # binary directed adjacency over all neurons
    pre = pairs["pre_root_id"].to_numpy()
    post = pairs["post_root_id"].to_numpy()
    ids = np.unique(np.concatenate([pre, post]))
    id2idx = {r: i for i, r in enumerate(ids)}
    rows = [id2idx[a] for a in pre]
    cols = [id2idx[b] for b in post]
    A = csr_matrix((np.ones(len(pre), dtype=np.int8), (rows, cols)), shape=(ids.size, ids.size))

    tg = pd.read_parquet(FLY / "results" / "tables" / "e07_annotated.parquet")
    tgt_idx = np.array([id2idx[r] for r in tg["root_id"]])
    deg_out = np.asarray(A.sum(1)).ravel()
    deg_in = np.asarray(A.sum(0)).ravel()
    total_degree = deg_out + deg_in

    print("computing sampled directed betweenness (k=512 pivots, frozen seed) "
          f"on FAFB binary graph ({A.shape[0]} nodes) ...", flush=True)
    bet = sampled_betweenness_directed(A)         # sampled estimator, frozen seed
    bet_tgt = bet[tgt_idx]

    # in/out clustering proxy: fraction of out-partners that connect back (reciprocity)
    A_t = A[tgt_idx]
    recip = np.asarray(A_t.multiply(A.T[tgt_idx]).sum(1)).ravel()
    recip = recip / np.maximum(deg_out[tgt_idx], 1)

    feat = pd.DataFrame({
        "root_id": tg["root_id"], "name": tg["name"], "nt_type": tg["nt_type"],
        "super_class": tg["super_class"], "cis_k8": tg["cis"],
        "in_degree": deg_in[tgt_idx], "out_degree": deg_out[tgt_idx],
        "total_degree": total_degree[tgt_idx],
        "betweenness_directed": bet_tgt,
        "out_clustering_recip": recip,
    })
    # local (undirected) clustering on the union graph for targets only
    Au = A + A.T
    Au.data = np.ones_like(Au.data)
    for k, i in enumerate(tgt_idx):
        nb = Au.indices[Au.indptr[i]:Au.indptr[i + 1]]
        kk = nb.size
        c = 0.0
        if kk >= 2:
            sub = Au[np.ix_(nb, nb)]
            c = sub.nnz / (kk * (kk - 1))
        feat.loc[k, "clustering_undirected"] = c

    feat.to_parquet(OUT / "fly_target_features.parquet", index=False)

    # ---------------- ME.131 case study ------------------------------------
    me = feat[feat["name"] == CASE]
    if me.empty:
        raise SystemExit(f"{CASE} not found in targets")
    me = me.iloc[0]
    cat = pd.read_csv(FLY / "results" / "tables" / "e14_chokepoint_catalogue_v2.csv")
    me_cat = cat[cat["name"] == CASE].iloc[0]

    # degree-matched peers among targets (±10% total degree, exclude self)
    lo, hi = 0.9 * me["total_degree"], 1.1 * me["total_degree"]
    peers = feat[(feat["total_degree"] >= lo) & (feat["total_degree"] <= hi)
                 & (feat["root_id"] != me["root_id"])]
    peers_cis = cat[cat["root_id"].isin(peers["root_id"])]["peer_median_cis"]

    def z(x, arr):
        arr = np.asarray(arr, float)
        return (x - arr.mean()) / (arr.std() or 1.0)

    profile_rows = []
    for col, label in (("cis_k8", "CIS (frozen k=8 panel)"),
                       ("betweenness_directed", "directed betweenness (sampled k=512)"),
                       ("clustering_undirected", "undirected clustering"),
                       ("out_clustering_recip", "reciprocal out-fraction"),
                       ("in_degree", "in-degree"), ("out_degree", "out-degree")):
        me_v = float(me[col])
        peer_v = peers[col].to_numpy(float)
        profile_rows.append({
            "quantity": label, "ME131": me_v,
            "peer_median": float(np.median(peer_v)) if len(peer_v) else np.nan,
            "peer_n": int(len(peer_v)),
            "z_vs_peers": float(z(me_v, peer_v)) if len(peer_v) > 2 else np.nan,
            "ratio_vs_peer_median": me_v / float(np.median(peer_v)) if len(peer_v) and np.median(peer_v) != 0 else np.nan,
        })
    prof = pd.DataFrame(profile_rows)
    prof.to_csv(OUT / "ME131_MECHANISTIC_PROFILE.csv", index=False)

    md = [
        f"# {CASE} CASE STUDY (Stage 13)",
        "",
        f"OCT visual-centrifugal neuron; frozen catalogue: rank {int(me_cat['rank'])},",
        f"CIS = {me_cat['cis']:.6f} at total degree {int(me_cat['total_degree'])}",
        f"(empirical p vs degree-matched peers = {me_cat['emp_p_degree_matched']};",
        f"peer median CIS = {me_cat['peer_median_cis']:.2e};",
        f"CIS excess ratio = {me_cat['cis_excess_ratio']:.1f}x).",
        "",
        "## Mechanistic profile vs degree-matched target peers",
        "",
        prof.to_string(index=False),
        "",
        "## Interpretation bounds (frozen)",
        "- Case study ONLY: no claim that ME.131's profile generalizes",
        "  (generalization is tested at Stage 22 cross-species, if at all).",
        "- Fly CIS is a different estimator (fixed-source panel, k=8):",
        "  comparisons stay within the fly study's own artifacts.",
        "- Peer pool = pre-registered CIS targets with +/-10% total degree",
        "  (small, documented pool).",
    ]
    (OUT / "ME131_CASE_STUDY.md").write_text("\n".join(md) + "\n")
    print(prof.to_string(index=False))


if __name__ == "__main__":
    main()
