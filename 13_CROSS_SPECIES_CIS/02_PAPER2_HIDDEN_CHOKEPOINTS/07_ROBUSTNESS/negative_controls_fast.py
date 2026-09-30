"""Stage 21 - Negative controls (vectorized execution, identical statistic).

Scientific design is UNCHANGED from the original negative_controls.py
(preserved in git history):

  NC1 permuted-R:   R permuted within subject (destroys R-feature pairing,
                    keeps R and feature marginals)
  NC2 permuted-f:   each feature permuted within subject (same, symmetric)

Acceptance: observed |median rho| must exceed the control 95% band edge
(|rho| p95 over 100 control draws), one-sided.

Execution-only rewrite (no protocol change):
  - Statistic: median over 801 subjects of Spearman(R, f). Computed as
    per-subject Pearson of ranks (Spearman identity), exact-equivalence
    ASSERTED against scipy spearmanr per feature (max |drho| < 1e-12).
  - Permutations: permuting values then ranking == permuting ranks
    (exact), so all NC work is on rank vectors.
  - Seed: the frozen CFG seed (seeds.bootstrap) seeds every control
    stream. NOTE (honest deviation): the serial reference consumed the
    RNG in draw-major order; this implementation consumes it subject-major
    with vectorized draws. Draw streams are exchangeable, so the 95% band
    is identical up to Monte-Carlo wobble at n_draws=100; margins
    (observed vs band edge) are reported so any near-threshold decision
    is visible. No acceptance threshold was changed.
Outputs: 10_TABLES/table_p2_negative_controls.csv (same schema + margins),
         07_ROBUSTNESS/NEGATIVE_CONTROLS.json (same schema + note).
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr

TREE = Path(__file__).resolve().parents[1]
CFG = json.loads((TREE / "01_CONFIG" / "config.json").read_text())
OUT = TREE / "07_ROBUSTNESS"
TBL = TREE / "10_TABLES"
SEED = CFG["seeds"]["bootstrap"]
N_DRAWS = 100
FEATURES = ["betweenness", "closeness_d", "redundancy", "bridge",
            "participation", "within_module_z", "kcore", "clustering"]


def pearson_by_group(x: np.ndarray, y: np.ndarray, idx: np.ndarray,
                     counts: np.ndarray) -> np.ndarray:
    """Pearson correlation of x,y within each group (vectorized)."""
    n = counts.astype(float)
    mx = np.bincount(idx, x) / n
    my = np.bincount(idx, y) / n
    xs = x - mx[idx]
    ys = y - my[idx]
    cov = np.bincount(idx, xs * ys) / n
    vx = np.bincount(idx, xs * xs) / n
    vy = np.bincount(idx, ys * ys) / n
    return cov / np.sqrt(np.maximum(vx * vy, 1e-300))


def perm_matrix(n: int, n_draws: int, rng: np.random.Generator) -> np.ndarray:
    """(n_draws, n) row-independent permutations (argsort of uniforms)."""
    return np.argsort(rng.random((n_draws, n)), axis=1)


def main() -> None:
    t0 = time.perf_counter()
    res = pd.read_parquet(TREE / "04_DEGREE_CONTROL" / "continuous_residuals.parquet")
    res = res[res["estimator"] == "M1_spline4_raw"][
        ["subject", "node", "residual_cis"]].copy()
    res["subject"] = res["subject"].astype(str).str.zfill(4)
    feat = pd.read_parquet(TREE / "03_FEATURE_EXTRACTION" /
                           "NODE_FEATURE_MATRIX.parquet")
    df = feat.merge(res, on=["subject", "node"], validate="1:1")
    assert len(df) == len(feat), "merge lost rows - subject key misalignment"
    df = df.sort_values(["subject", "node"]).reset_index(drop=True)

    codes, subj_unique = pd.factorize(df["subject"].to_numpy())
    n_sub = len(subj_unique)
    counts = np.bincount(codes, minlength=n_sub).astype(float)
    R = df["residual_cis"].to_numpy(float)
    draw_idx = np.repeat(np.arange(N_DRAWS), int(counts[0]))
    print(f"rows={len(df)} subjects={n_sub} nodes/subject={int(counts[0])}",
          flush=True)

    # per-subject slices (contiguous after the sort above)
    slices = [np.where(codes == i)[0] for i in range(n_sub)]

    rows = []
    for f in FEATURES:
        tf0 = time.perf_counter()
        x = df[f].to_numpy(float)

        # ---- equivalence gate vs scipy (per-subject reference)
        rho_ref = np.array([spearmanr(R[sl], x[sl]).statistic for sl in slices])
        rkR = np.empty(len(df))
        rkX = np.empty(len(df))
        for sl in slices:
            rkR[sl] = rankdata(R[sl])
            rkX[sl] = rankdata(x[sl])
        pr_vec = pearson_by_group(rkR, rkX, codes, counts)
        max_dev = float(np.max(np.abs(pr_vec - rho_ref)))
        assert max_dev < 1e-12, f"equivalence FAILED for {f}: {max_dev}"
        obs = float(np.median(pr_vec))

        # ---- NC1: permute R within subject -> PR1 (n_sub, N_DRAWS)
        rng = np.random.default_rng(SEED)
        PR1 = np.empty((n_sub, N_DRAWS))
        for i, sl in enumerate(slices):
            n_s = len(sl)
            P = perm_matrix(n_s, N_DRAWS, rng)
            rkr = np.broadcast_to(rkR[sl], (N_DRAWS, n_s))
            rkx = np.broadcast_to(rkX[sl], (N_DRAWS, n_s))
            pr = pearson_by_group(
                np.take_along_axis(rkr, P, axis=1).ravel(), rkx.ravel(),
                draw_idx, np.full(N_DRAWS, n_s, dtype=float))
            PR1[i] = pr
        nc1 = np.median(PR1, axis=0)

        # ---- NC2: permute feature within subject
        rng2 = np.random.default_rng(SEED)
        PR2 = np.empty((n_sub, N_DRAWS))
        for i, sl in enumerate(slices):
            n_s = len(sl)
            P = perm_matrix(n_s, N_DRAWS, rng2)
            rkr = np.broadcast_to(rkR[sl], (N_DRAWS, n_s))
            rkx = np.broadcast_to(rkX[sl], (N_DRAWS, n_s))
            pr = pearson_by_group(
                rkr.ravel(), np.take_along_axis(rkx, P, axis=1).ravel(),
                draw_idx, np.full(N_DRAWS, n_s, dtype=float))
            PR2[i] = pr
        nc2 = np.median(PR2, axis=0)

        c1_p95 = float(np.quantile(np.abs(nc1), 0.95))
        c2_p95 = float(np.quantile(np.abs(nc2), 0.95))
        rows.append({
            "feature": f,
            "median_rho_observed": obs,
            "nc1_permuted_R_median": float(np.median(nc1)),
            "nc1_p95_abs": c1_p95,
            "nc2_permuted_f_median": float(np.median(nc2)),
            "nc2_p95_abs": c2_p95,
            "obs_exceeds_nc1_band": bool(abs(obs) > c1_p95),
            "obs_exceeds_nc2_band": bool(abs(obs) > c2_p95),
            "nc1_margin": float(abs(obs) - c1_p95),
            "nc2_margin": float(abs(obs) - c2_p95),
            "equivalence_max_dev": max_dev,
        })
        print(f"{f:18s} obs={obs:+.3f} nc1_p95={c1_p95:.3f} "
              f"nc2_p95={c2_p95:.3f} exceeds={rows[-1]['obs_exceeds_nc1_band']}"
              f"/{rows[-1]['obs_exceeds_nc2_band']} "
              f"({time.perf_counter() - tf0:.0f}s)", flush=True)

    out = pd.DataFrame(rows)
    TBL.mkdir(parents=True, exist_ok=True)
    out.to_csv(TBL / "table_p2_negative_controls.csv", index=False)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "NEGATIVE_CONTROLS.json").write_text(json.dumps(
        {"n_draws": N_DRAWS, "seed": SEED,
         "implementation": "vectorized rank-permutation (exact Spearman "
                           "equivalence asserted per feature); frozen seed; "
                           "draw stream subject-major (exchangeable vs the "
                           "serial reference - band identical up to "
                           "Monte-Carlo wobble at n_draws=100; margins "
                           "reported)",
         "nc3_nc4_note": "NC3/NC4 covered by ml_benchmark negative control "
                         "and feature_nulls Stage 15",
         "results": out.to_dict(orient="records")}, indent=2))
    print("saved:", OUT / "NEGATIVE_CONTROLS.json")
    print(f"total {time.perf_counter() - t0:.0f}s")


if __name__ == "__main__":
    main()
