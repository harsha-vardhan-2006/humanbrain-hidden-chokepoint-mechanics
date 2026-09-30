"""Stage 6 - Graph-geometric feature extraction (human, 4S456 @ 15% cost).

For each QC-pass subject, load the frozen thresholded binary graph via
Paper 1's cache_io (read-only) and compute per-node features:

  core      : degree, strength (raw |w| sum)
  path      : betweenness (exact unweighted Brandes), distance-weighted closeness
  redundancy: mean over neighbors j of (1 - 1/|P(i,j)|), |P(i,j)| = number of
              distinct shortest paths i->j (exact path-counting BFS)
  bridge    : 1 - mean_j |N(i) & N(j)| / |N(i) u N(j)| (edge-embeddedness gap)
  community : participation coefficient P_i = 1 - sum_s (k_is/k_i)^2
              (Guimera-Amaral; modules = frozen atlas system labels),
              within-module degree z-score
  core/pos  : k-core number (peeling), eigenvector centrality (power iteration),
              PageRank (damping 0.85, 100 iterations)
  local     : binary Watts-Strogatz clustering coefficient

Coupling-risk flags (MATHEMATICAL_FRAMEWORK section 8): betweenness,
closeness_d, redundancy are shortest-path based (share the efficiency
functional with CIS).

Outputs (03_FEATURE_EXTRACTION/): NODE_FEATURE_MATRIX.parquet,
feature_extraction_manifest.json; per-subject caches in _per_subject_cache/
(resume-safe). Parallel over subjects with ProcessPoolExecutor.
"""
from __future__ import annotations

import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pandas as pd

TREE = Path(__file__).resolve().parents[1]
STUDY = TREE.parent
sys.path.insert(0, str(STUDY / "02_PREPROCESSING"))

import cache_io  # noqa: E402  (Paper 1 frozen loader - read-only use)

CFG = json.loads((TREE / "01_CONFIG" / "config.json").read_text())
OUT = TREE / "03_FEATURE_EXTRACTION"
CACHE = OUT / "_per_subject_cache"
LABELS = pd.read_csv(CFG["paths"]["atlas_labels"])
FEATURE_COLS = ["degree", "strength", "betweenness", "closeness_d", "redundancy",
                "bridge", "participation", "within_module_z", "kcore",
                "eigenvector", "pagerank", "clustering"]
COUPLING_RISK = {"betweenness": True, "closeness_d": True, "redundancy": True,
                 "degree": False, "strength": False, "bridge": False,
                 "participation": False, "within_module_z": False, "kcore": False,
                 "eigenvector": False, "pagerank": False, "clustering": False}


def _bfs_paths(adj, src):
    """Single-source BFS: distances + exact #shortest paths (sigma)."""
    n = adj.shape[0]
    dist = np.full(n, np.inf)
    sigma = np.zeros(n)
    dist[src] = 0.0
    sigma[src] = 1.0
    frontier = np.array([src])
    d = 0
    while frontier.size:
        d += 1
        neigh = np.unique(np.where(adj[frontier])[1])
        newly = neigh[np.isinf(dist[neigh])]
        if newly.size == 0:
            break
        # predecessors of `newly` at distance d-1: neighbors of each j on frontier
        sub = adj[np.ix_(newly, frontier)] & (dist[frontier] == d - 1)[None, :]
        for idx, j in enumerate(newly):
            pre = frontier[sub[idx]]
            sigma[j] = sigma[pre].sum()
            dist[j] = d
        frontier = newly
    return dist, sigma


def _brandes_betweenness(adj) -> np.ndarray:
    """Exact unweighted betweenness (Brandes 2001) via BFS + dependencyaccum."""
    n = adj.shape[0]
    nb = [np.where(adj[i])[0] for i in range(n)]
    bc = np.zeros(n)
    for s in range(n):
        stack = []
        pred = [[] for _ in range(n)]
        sigma = np.zeros(n); sigma[s] = 1.0
        dist = np.full(n, -1.0); dist[s] = 0.0
        queue = [s]
        qi = 0
        while qi < len(queue):
            v = queue[qi]; qi += 1
            stack.append(v)
            dv1 = dist[v] + 1
            for w in nb[v]:
                if dist[w] < 0:
                    dist[w] = dv1
                    queue.append(w)
                if dist[w] == dv1:
                    sigma[w] += sigma[v]
                    pred[w].append(v)
        delta = np.zeros(n)
        for w in reversed(stack):
            coef = (1.0 + delta[w]) / sigma[w]
            for v in pred[w]:
                delta[v] += sigma[v] * coef
            if w != s:
                bc[w] += delta[w]
    return bc / ((n - 1) * (n - 2))


def _redundancy(adj, i) -> tuple[float, int]:
    """Local alternative-path redundancy of node i.

    Fraction of unordered neighbor pairs {j,k} of N(i) that remain connected
    within 2 steps WITHOUT using i: direct edge j-k, or a common neighbor
    m != i. Low values = i's neighborhood depends on i to stay locally
    connected (chokepoint-like); high = fully redundant. Pairs = C(k,2).
    (Fixes the degenerate per-neighbor sigma definition: a direct neighbor
    always has exactly one shortest path from i, so that version was
    identically 0.)

    AMENDMENT 3 (2026-09-28, pre-analysis): the common-neighbor matrix must
    be computed in INTEGER arithmetic. On a boolean adjacency, numpy's
    bool-matrix dot performs OR-semantics (no counts), so C collapsed to
    {0, -1}, `C > 0` was never true, and the feature degenerated to the
    direct-edge mask - numerically identical to `clustering` on all rows
    (verified: corr = 1.0 over 365,256 rows). Cast to int32 before the
    product; no other line changes.
    """
    nb = np.where(adj[i])[0]
    k = nb.size
    if k < 2:
        return 0.0, 0
    A = adj[np.ix_(nb, nb)]                      # direct edges among neighbors
    Ai = adj.astype(np.int32)                    # AMENDMENT 3: integer counts
    C = Ai[nb, :].dot(Ai[:, nb]) - 1             # common neighbors anywhere, minus i
    ok = A | (C > 0)
    np.fill_diagonal(ok, False)
    pairs = k * (k - 1) // 2
    return float(np.triu(ok, 1).sum() / pairs), int(pairs)


def _bridge(adj, i) -> float:
    nb = np.where(adj[i])[0]
    if nb.size == 0:
        return 0.0
    Ni = set(int(x) for x in nb)
    vals = []
    for j in nb:
        Nj = set(int(x) for x in np.where(adj[j])[0])
        union = Ni | Nj
        vals.append(len(Ni & Nj) / len(union) if union else 0.0)
    return float(1.0 - np.mean(vals))


def _clustering(adj, i) -> float:
    nb = np.where(adj[i])[0]
    k = nb.size
    if k < 2:
        return 0.0
    sub = adj[np.ix_(nb, nb)]
    # symmetric adjacency counts each edge twice: C = sub.sum()/2,
    # so C / C(k,2) = sub.sum() / (k*(k-1)).
    return float(sub.sum() / (k * (k - 1)))


def _participation(adj, sysmap, i) -> float:
    """Guimera-Amaral participation: P_i = 1 - sum_s (k_is/k_i)^2."""
    nb = np.where(adj[i])[0]
    k = nb.size
    if k == 0:
        return 0.0
    frac = np.bincount(sysmap[nb]) / k
    return float(1.0 - np.sum(frac ** 2))


def _pagerank(adj, damping=0.85, iters=100) -> np.ndarray:
    out = adj.sum(1)
    M = np.where(out > 0, adj / np.maximum(out, 1)[:, None], 1.0 / adj.shape[0])
    r = np.full(adj.shape[0], 1.0 / adj.shape[0])
    for _ in range(iters):
        r = damping * (M.T @ r) + (1 - damping) / adj.shape[0]
    return r / r.sum()


def _kcores(adj) -> np.ndarray:
    """Standard k-core peeling; returns core number per node."""
    n = adj.shape[0]
    alive = np.ones(n, dtype=bool)
    core = np.zeros(n, dtype=int)
    rem = adj.astype(np.int32).copy()
    while alive.any():
        d = rem.sum(1) * alive
        k = int(d[alive].min())
        while True:
            d = rem.sum(1) * alive
            cand = np.where(alive & (d <= k))[0]
            if cand.size == 0:
                break
            core[cand] = k
            alive[cand] = False
            rem[cand, :] = 0
            rem[:, cand] = 0
    return core


def _eigenvector(adj, iters=200, tol=1e-10) -> np.ndarray:
    n = adj.shape[0]
    ev = np.full(n, 1.0 / n)
    for _ in range(iters):
        ev_new = adj @ ev
        s = ev_new.sum()
        ev_new = np.full(n, 1.0 / n) if s == 0 else ev_new / s
        if np.abs(ev_new - ev).max() < tol:
            return ev_new
        ev = ev_new
    return ev


def features_one_subject(job: tuple) -> str:
    sid, variant = job
    t0 = time.time()
    zsid = str(sid).zfill(4)
    cache_file = CACHE / f"sub-{zsid}.parquet"
    if cache_file.exists():
        return f"skip {sid} (cached)"

    index = cache_io.load_key_index()
    W = cache_io.get_matrix(index, int(sid), cache_io.PRIMARY_ATLAS, variant)
    B = cache_io.threshold_cost(W, 0.15)
    Ab = (B.toarray() != 0)
    n = Ab.shape[0]

    Wraw = np.asarray(W, dtype=np.float64)
    np.fill_diagonal(Wraw, 0.0)
    strength = Wraw.sum(1)
    deg = Ab.sum(1).astype(float)

    sys_names = LABELS.set_index("node")["system"]
    system_list = sorted(LABELS["system"].unique())
    sysmap = np.array([system_list.index(sys_names.loc[i]) for i in range(n)])

    bet = _brandes_betweenness(Ab)
    dist_all = cache_io.allpairs_dist_fast(Ab.astype(np.float32))
    finite = dist_all > 0
    closeness = np.where(finite, 1.0 / np.maximum(dist_all, 1e-12), 0.0).sum(1)
    denom = np.maximum(finite.sum(1) - 1, 1)
    closeness = closeness / denom

    ev = _eigenvector(Ab.astype(float))
    pr = _pagerank(Ab.astype(float))
    kc = _kcores(Ab)

    deg_series = pd.Series(deg)
    mod_deg_mean = deg_series.groupby(sysmap).transform("mean").to_numpy()
    mod_deg_std = deg_series.groupby(sysmap).transform("std").fillna(1.0).to_numpy()
    mod_deg_std = np.where(mod_deg_std > 0, mod_deg_std, 1.0)

    rows = []
    for i in range(n):
        red, n_pairs = _redundancy(Ab, i)
        rows.append({
            "subject": zsid, "node": i, "degree": int(deg[i]),
            "strength": float(strength[i]),
            "betweenness": float(bet[i]), "closeness_d": float(closeness[i]),
            "redundancy": red, "redundancy_n_pairs": n_pairs,
            "bridge": _bridge(Ab, i), "participation": _participation(Ab, sysmap, i),
            "within_module_z": float((deg[i] - mod_deg_mean[i]) / mod_deg_std[i]),
            "kcore": int(kc[i]), "eigenvector": float(ev[i]),
            "pagerank": float(pr[i]), "clustering": _clustering(Ab, i),
            "n_neighbors": int(np.where(Ab[i])[0].size), "system": sys_names.loc[i],
        })
    df = pd.DataFrame(rows)
    CACHE.mkdir(parents=True, exist_ok=True)
    df.to_parquet(cache_file, index=False)
    return f"done {sid} in {time.time()-t0:.0f}s"


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--limit", type=int, default=0, help="debug: limit subjects")
    ap.add_argument("--subject", type=str, default="", help="debug: one subject")
    args = ap.parse_args()

    qc = pd.read_csv(CFG["paths"]["qc_primary"])
    ids = qc.loc[qc["qc_pass"] == True, "subject"].astype(str).tolist()  # noqa: E712
    if args.subject:
        ids = [args.subject]
    elif args.limit:
        ids = ids[: args.limit]
    jobs = [(s, cache_io.PRIMARY_VARIANT) for s in ids]
    OUT.mkdir(parents=True, exist_ok=True)
    CACHE.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    done = 0
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(features_one_subject, j): j[0] for j in jobs}
        for fut in as_completed(futs):
            msg = fut.result()
            done += 1
            if done % 25 == 0 or done == len(jobs):
                print(f"[{time.strftime('%H:%M:%S')}] {done}/{len(jobs)} {msg}", flush=True)

    frames = [pd.read_parquet(CACHE / f"sub-{s.zfill(4)}.parquet") for s in ids]
    alldf = pd.concat(frames, ignore_index=True)
    alldf.to_parquet(OUT / "NODE_FEATURE_MATRIX.parquet", index=False)
    manifest = {
        "n_subjects": len(ids), "n_nodes": 456, "features": FEATURE_COLS,
        "coupling_risk": COUPLING_RISK,
        "variant": cache_io.PRIMARY_VARIANT, "cost": 0.15,
        "runtime_s": round(time.time() - t0, 1),
        "note": "all features per-subject on the frozen thresholded binary graph; "
                "definitions in 03_FEATURE_EXTRACTION/FEATURE_DEFINITIONS.md",
    }
    (OUT / "feature_extraction_manifest.json").write_text(json.dumps(manifest, indent=2))
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
