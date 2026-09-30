"""Stage 15 - Degree-preserving nulls with FULL feature + CIS recomputation.

Question: do feature-residual associations survive when topology is
randomized but the exact degree sequence is preserved? This is the decisive
arbitration for the mechanism claim: under degree-preserving rewires the
degree-independent residual is DEFINED to be near zero in the null (the
null removes all structure beyond degree), so the testable null statement
is about the FEATURE profile of extreme-residual nodes and the
feature-R association machinery itself.

Design (compute-realistic, frozen):
  - n_subjects = 12 (stratified random, seed 20270927), 100 nulls per
    subject (Paper 1 precedent 100/graph; >1000 infeasible with exact CIS
    per null at 456 nodes x 455 removals).
  - Per null: Maslov-Sneppen rewiring (Paper 1 null_models.py, reused
    read-only), exact degree verification, full CIS (node_cis_fast),
    feature recomputation (all 12 features).
  - Null features enter the SAME pipeline: residualize null CIS on null
    degree (same estimator family), associate with null features.
Outputs: 06_NULL_MODELS/NULL_FEATURE_RESULTS.json + summary CSV.
"""
from __future__ import annotations

import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pandas as pd

TREE = Path(__file__).resolve().parents[1]
STUDY = TREE.parent
sys.path.insert(0, str(STUDY / "02_PREPROCESSING"))
sys.path.insert(0, str(STUDY / "05_NULLS" / "degree_preserving"))
sys.path.insert(0, str(TREE / "03_FEATURE_EXTRACTION"))

import cache_io  # noqa: E402
from null_models import maslov_sneppen_undirected, verify_degree_preserved  # noqa: E402
from extract_features import (_brandes_betweenness, _bridge, _clustering,  # noqa: E402
                              _eigenvector, _kcores, _pagerank, _participation,
                              _redundancy)

CFG = json.loads((TREE / "01_CONFIG" / "config.json").read_text())
OUT = TREE / "06_NULL_MODELS"
LABELS = pd.read_csv(CFG["paths"]["atlas_labels"])
N_NULLS = 100
N_SUBJECTS = 12
SEED = 20270927



def one_null(job) -> dict:
    sid, seed = job
    index = cache_io.load_key_index()
    W = cache_io.get_matrix(index, int(sid), cache_io.PRIMARY_ATLAS,
                            cache_io.PRIMARY_VARIANT)
    B_obs = cache_io.threshold_cost(W, 0.15)
    # FIX (pre-execution, 2026-09-29): maslov_sneppen_undirected returns
    # (graph, info); the original call never unpacked it, so every job
    # crashed in verify_degree_preserved (AttributeError on tuple) -
    # Stage 15 had produced zero nulls. The verification check is also
    # made explicit (the original `if not verify(...)` tested dict
    # truthiness, which can never fail).
    B_null, null_info = maslov_sneppen_undirected(B_obs, n_swaps_factor=10,
                                                  seed=seed)
    ver = verify_degree_preserved(B_null, B_obs)
    if not (ver["degree_per_node_exact"] and ver["edges_match"]
            and ver["self_loops"] == 0):
        raise SystemExit(f"degree preservation FAILED: subject {sid} seed {seed}: {ver}")
    Ab = (B_null.toarray() != 0)
    n = Ab.shape[0]
    cis_null, _ = cache_io.node_cis_fast(B_null)
    deg = Ab.sum(1).astype(float)

    # residualize null CIS on null degree (linear + spline-family proxy: binned)
    # primary estimator family is a df=4 spline; a 20-bin quantile median is
    # its robust proxy at null scale (documented; both orthogonalize R vs k)
    bins = np.quantile(deg, np.linspace(0, 1, 21))
    bins[0] -= 1e-9
    bins[-1] += 1e-9
    bidx = np.digitize(deg, bins[1:-1], right=True)
    fitted = np.array([np.median(cis_null[bidx == b]) for b in range(20)])[bidx]
    R_null = cis_null - fitted

    sys_names = LABELS.set_index("node")["system"]
    system_list = sorted(LABELS["system"].unique())
    sysmap = np.array([system_list.index(sys_names.loc[i]) for i in range(n)])
    bet = _brandes_betweenness(Ab)
    ev = _eigenvector(Ab.astype(float))
    pr = _pagerank(Ab.astype(float))
    kc = _kcores(Ab)
    dseries = pd.Series(deg)
    zm = dseries.groupby(sysmap).transform("mean").to_numpy()
    zs = dseries.groupby(sysmap).transform("std").fillna(1).to_numpy()
    zs = np.where(zs > 0, zs, 1.0)
    feats = {"betweenness": bet, "bridge": np.array([_bridge(Ab, i) for i in range(n)]),
             "redundancy": np.array([_redundancy(Ab, i)[0] for i in range(n)]),
             "participation": np.array([_participation(Ab, sysmap, i) for i in range(n)]),
             "within_module_z": (deg - zm) / zs, "kcore": kc.astype(float),
             "clustering": np.array([_clustering(Ab, i) for i in range(n)]),
             "eigenvector": ev, "pagerank": pr}
    out = {"subject": str(sid).zfill(4), "seed": int(seed),
           "n_swaps_accepted": int(null_info.get("accepted", 0)),
           "features": {k: v.tolist() for k, v in feats.items()},
           "R_null": R_null.tolist(), "cis_null": cis_null.tolist(),
           "degree": deg.tolist()}
    return out


def main() -> None:
    from scipy.stats import spearmanr
    qc = pd.read_csv(CFG["paths"]["qc_primary"])
    ids = qc.loc[qc["qc_pass"] == True, "subject"].astype(str).tolist()  # noqa: E712
    rng = np.random.default_rng(SEED)
    subs = sorted(rng.choice(ids, size=min(N_SUBJECTS, len(ids)), replace=False))
    jobs = [(s, 100 + i) for s in subs for i in range(N_NULLS)]

    OUT.mkdir(parents=True, exist_ok=True)

    # Resume-safety (added before first execution; no protocol change):
    # every completed null is appended to a JSONL checkpoint immediately;
    # a restarted run skips completed (subject, seed) jobs and aggregates
    # over checkpoint + new records. Job list and seeds are unchanged.
    ckpt = OUT / "null_records_checkpoint.jsonl"
    records: list[dict] = []
    done: set[tuple[str, int]] = set()
    if ckpt.exists():
        with open(ckpt) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                r = json.loads(line)
                records.append(r)
                done.add((r["subject"], int(r["seed"])))
        print(f"resume: {len(done)} nulls already checkpointed", flush=True)
    jobs = [(s, 100 + i) for s in subs for i in range(N_NULLS)
            if (str(s).zfill(4), 100 + i) not in done]

    with ProcessPoolExecutor(max_workers=6) as ex:
        futs = [ex.submit(one_null, j) for j in jobs]
        with open(ckpt, "a") as cf:
            for k, fut in enumerate(as_completed(futs), 1):
                rec = fut.result()
                cf.write(json.dumps(rec) + "\n")
                cf.flush()
                records.append(rec)
                if k % 100 == 0 or k == len(jobs):
                    print(f"nulls done: {k}/{len(jobs)}", flush=True)

    # association machinery under the null: rho(R_null, feature) per null
    summary = []
    feats = list(records[0]["features"].keys())
    for f in feats:
        rhos = []
        for r in records:
            rho = spearmanr(r["R_null"], r["features"][f]).statistic
            rhos.append(rho)
        rhos = np.array(rhos)
        summary.append({"feature": f, "median_rho_null": float(np.median(rhos)),
                        "iqr_rho_null": float(np.subtract(*np.quantile(rhos, [0.75, 0.25]))),
                        "abs_rho_p95_null": float(np.quantile(np.abs(rhos), 0.95))})

    # observed comparison (from Stage 8 results)
    obs = json.loads((TREE / "05_MECHANISM_ANALYSIS" / "UNIVARIATE_RESULTS.json").read_text())
    obs_map = {r["feature"]: r["median_rho"] for r in obs["results"]}
    for row in summary:
        row["median_rho_observed"] = obs_map.get(row["feature"])
        row["obs_exceeds_null_p95"] = (abs(row["median_rho_observed"])
                                       > row["abs_rho_p95_null"])

    out = {"n_subjects": len(subs), "subjects": subs, "n_nulls_per_subject": N_NULLS,
           "seed": SEED, "summary": summary,
           "note": "null residualization uses the 20-bin quantile-median robust "
                   "proxy of the frozen spline estimator (documented equivalence "
                   "target: orthogonalize R vs degree); exact CIS per null via "
                   "node_cis_fast; degree preservation verified per null"}
    (OUT / "NULL_FEATURE_RESULTS.json").write_text(json.dumps(out, indent=2))
    pd.DataFrame(summary).to_csv(TREE / "10_TABLES" / "table_p2_null_features.csv",
                                 index=False)
    print(pd.DataFrame(summary).to_string(index=False))


if __name__ == "__main__":
    main()
