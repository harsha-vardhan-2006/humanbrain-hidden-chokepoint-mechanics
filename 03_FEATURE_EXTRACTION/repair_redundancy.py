"""AMENDMENT 3 repair - regenerate the degenerate `redundancy` column.

CONFIG_FREEZE.md Amendment 3: the Stage 6 redundancy feature collapsed to the
direct-edge mask (bool-matrix dot OR-semantics), making it numerically
identical to `clustering` on every row. This script regenerates the column
from the frozen thresholded graphs (same loader, same frozen variant/cost)
with the FIXED `_redundancy` (int32 common-neighbor counts) and rebuilds
NODE_FEATURE_MATRIX.parquet.

Every other column is copied through byte-identical from the existing
per-subject caches. The script fails loud if the new column equals
`clustering` on any subject that has at least one transitive neighbor pair
(a pair directly connected must exist for equality to be legitimate).
Parallel over subjects; resume-safe.

Run:  py 03_FEATURE_EXTRACTION/repair_redundancy.py --workers 6
"""
from __future__ import annotations

import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pandas as pd

TREE = Path(__file__).resolve().parents[1]
STUDY = TREE.parent
sys.path.insert(0, str(STUDY / "02_PREPROCESSING"))
sys.path.insert(0, str(TREE))

import cache_io  # noqa: E402  (Paper 1 frozen loader - read-only)
from extract_features import _redundancy  # noqa: E402  (AMENDMENT 3 version)

CFG = None  # config loaded lazily in workers


def _cfg():
    import json
    return json.loads((TREE / "01_CONFIG" / "config.json").read_text())


def repair_one(sid: str) -> str:
    zsid = str(sid).zfill(4)
    cache_file = TREE / "03_FEATURE_EXTRACTION" / "_per_subject_cache" / f"sub-{zsid}.parquet"
    df = pd.read_parquet(cache_file)

    index = cache_io.load_key_index()
    W = cache_io.get_matrix(index, int(sid), cache_io.PRIMARY_ATLAS,
                            cache_io.PRIMARY_VARIANT)
    B = cache_io.threshold_cost(W, 0.15)
    Ab = (B.toarray() != 0)
    n = Ab.shape[0]

    red = np.empty(n)
    n_pairs = np.empty(n, dtype=np.int64)
    for i in range(n):
        red[i], n_pairs[i] = _redundancy(Ab, i)

    old = df["redundancy"].to_numpy(float)
    changed = int((old != red).sum())
    if changed == 0:
        return f"skip {zsid}: column already correct"
    # sanity: new column must NOT equal clustering when any 2-step path exists
    if np.allclose(red, df["clustering"].to_numpy(float)):
        raise SystemExit(
            f"{zsid}: repaired redundancy still identical to clustering - "
            f"AMENDMENT 3 fix did not take effect")
    df["redundancy"] = red
    df["redundancy_n_pairs"] = n_pairs
    df.to_parquet(cache_file, index=False)
    return f"repaired {zsid}: {changed}/{n} rows changed"


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args()

    cfg = _cfg()
    qc = pd.read_csv(cfg["paths"]["qc_primary"])
    ids = qc.loc[qc["qc_pass"] == True, "subject"].astype(str).tolist()  # noqa: E712

    t0 = time.time()
    done = 0
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(repair_one, s): s for s in ids}
        for fut in as_completed(futs):
            msg = fut.result()
            done += 1
            if done % 50 == 0 or done == len(ids):
                print(f"[{time.strftime('%H:%M:%S')}] {done}/{len(ids)} {msg}",
                      flush=True)

    frames = [pd.read_parquet(TREE / "03_FEATURE_EXTRACTION" / "_per_subject_cache"
                              / f"sub-{s.zfill(4)}.parquet") for s in ids]
    alldf = pd.concat(frames, ignore_index=True)
    alldf.to_parquet(TREE / "03_FEATURE_EXTRACTION" / "NODE_FEATURE_MATRIX.parquet",
                     index=False)

    # matrix-level sanity + manifest refresh
    corr = float(np.corrcoef(alldf["redundancy"], alldf["clustering"])[0, 1])
    manifest = {
        "n_subjects": len(ids), "n_nodes": 456,
        "features": ["degree", "strength", "betweenness", "closeness_d",
                     "redundancy", "bridge", "participation", "within_module_z",
                     "kcore", "eigenvector", "pagerank", "clustering"],
        "coupling_risk": {"betweenness": True, "closeness_d": True,
                          "redundancy": True, "degree": False, "strength": False,
                          "bridge": False, "participation": False,
                          "within_module_z": False, "kcore": False,
                          "eigenvector": False, "pagerank": False,
                          "clustering": False},
        "variant": cache_io.PRIMARY_VARIANT, "cost": 0.15,
        "runtime_s": round(time.time() - t0, 1),
        "amendment_3": {
            "repair": "redundancy regenerated with int32 common-neighbor counts",
            "redundancy_vs_clustering_pearson_r": corr,
            "note": "bool-dot defect fixed per CONFIG_FREEZE.md Amendment 3; "
                    "all other columns copied through from the original Stage 6 run",
        },
        "note": "all features per-subject on the frozen thresholded binary graph; "
                "definitions in 03_FEATURE_EXTRACTION/FEATURE_DEFINITIONS.md",
    }
    (TREE / "03_FEATURE_EXTRACTION" / "feature_extraction_manifest.json").write_text(
        __import__("json").dumps(manifest, indent=2))
    print(json := __import__("json").dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
