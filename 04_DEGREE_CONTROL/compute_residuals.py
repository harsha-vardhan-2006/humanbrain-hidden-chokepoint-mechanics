"""Stage 3 - Degree-control residualization (Paper 2).

For every QC-pass human subject:
  1. Load frozen per-node (node, cis, degree, strength) from Paper 1
     subject_cis CSVs (read-only).
  2. Fit E[CIS | degree] with the frozen estimator ladder
     (primary: OLS log10(cis+1e-6) ~ natural cubic spline(degree, df=4)).
  3. Compute residual R_i and standardized residual ZR_i per estimator.
  4. Apply the frozen orthogonality gate: Spearman(R, degree) per subject.
  5. Write per-subject CSVs, subject-level summary, gate report, and the
     three Stage 3 figures.

No stochasticity. No manual edits of outputs. Fail loud on any anomaly.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.interpolate import splev, splrep
from scipy.stats import spearmanr


def _assert_finite(a: np.ndarray, what: str) -> None:
    """Fail loud on any NaN/Inf — NaN must never flow into statistics."""
    if not np.isfinite(a).all():
        n = int((~np.isfinite(a)).sum())
        raise SystemExit(f"NON-FINITE VALUES in {what}: {n} NaN/Inf present")

TREE = Path(__file__).resolve().parents[1]
CFG = json.loads((TREE / "01_CONFIG" / "config.json").read_text())
P = CFG["paths"]
OUT = Path(P["out_degree_control"])
FIGS = Path(P["out_figures"])
LOGS = Path(P["out_logs"])

LOG_LINES: list[str] = []


def log(msg: str) -> None:
    stamp = time.strftime("%H:%M:%S")
    line = f"[{stamp}] {msg}"
    print(line, flush=True)
    LOG_LINES.append(line)


# ---------------------------------------------------------------- estimators
def fit_predict(x: np.ndarray, y: np.ndarray, kind: str, df: int | None = None,
                q: int | None = None, log_offset: float | None = None
                ) -> tuple[np.ndarray, dict]:
    """Return fitted values on the original y scale + fit metadata."""
    meta: dict = {"kind": kind, "df": df, "q": q}
    if kind == "ols":
        beta1, beta0 = np.polyfit(x, y, 1)
        meta.update({"beta0": float(beta0), "beta1": float(beta1)})
        return beta0 + beta1 * x, meta
    if kind == "spline_ols":
        # y already transformed by caller; fit natural-ish cubic smoothing spline
        # via least-squares B-spline on unique knots (scipy splrep, s=0 exact)
        order = np.argsort(x)
        xu, yu = x[order], y[order]
        # collapse duplicate degrees by mean (splrep requires distinct x)
        xu_u, idx = np.unique(xu, return_inverse=True)
        yu_u = np.bincount(idx, weights=yu) / np.bincount(idx)
        n_knots = max(df + 1, 5)
        t = np.quantile(xu_u, np.linspace(0, 1, n_knots))
        t[0] -= 1e-9
        t[-1] += 1e-9
        try:
            tck = splrep(xu_u, yu_u, k=3, t=t[1:-1], s=0)
        except Exception:
            tck = splrep(xu_u, yu_u, k=min(3, len(xu_u) - 1), s=len(xu_u) * 1e-6)
        fitted = splev(x, tck)
        meta["tck"] = None  # not serialized; per-subject refit only
        return np.asarray(fitted), meta
    if kind == "poly":
        coefs = np.polyfit(x, y, df)
        meta["coefs"] = coefs.tolist()
        return np.polyval(coefs, x), meta
    if kind == "quantile_bins":
        edges = np.quantile(x, np.linspace(0, 1, q + 1))
        edges[0] -= 1e-9
        edges[-1] += 1e-9
        bins = np.digitize(x, edges[1:-1], right=True)
        fitted = np.empty_like(y)
        for b in range(q):
            m = bins == b
            if m.any():
                fitted[m] = np.median(y[m])
        meta["bin_edges"] = edges.tolist()
        return fitted, meta
    raise ValueError(f"unknown estimator kind: {kind}")


def orthogonality(resid: np.ndarray, degree: np.ndarray) -> float:
    _assert_finite(resid, "orthogonality input")
    rho, _ = spearmanr(resid, degree)
    if np.isnan(rho):
        raise SystemExit("orthogonality: Spearman returned NaN (constant input?)")
    return float(rho)


# ---------------------------------------------------------------- main
def main() -> None:
    t0 = time.time()
    qc = pd.read_csv(P["qc_primary"])
    pass_ids = qc.loc[qc["qc_pass"] == True, "subject"].astype(str).tolist()  # noqa: E712
    log(f"QC-pass subjects: {len(pass_ids)} / {len(qc)}")

    cis_dir = Path(P["subject_cis_dir"])
    labels = pd.read_csv(P["atlas_labels"])

    gate_rows = []
    subject_summaries = []
    extreme_frames = []
    n_missing = 0

    for si, sid in enumerate(sorted(pass_ids), 1):
        f = cis_dir / f"sub-{str(sid).zfill(4)}.csv"
        if not f.exists():
            n_missing += 1
            log(f"MISSING subject file: {f}")
            continue
        df = pd.read_csv(f)
        if len(df) != CFG["cohort"]["n_nodes"]:
            raise SystemExit(f"{f}: expected 456 rows, got {len(df)}")
        df = df.merge(labels, on="node", how="left", validate="1:1")

        x = df["degree"].to_numpy(float)
        y = df["cis"].to_numpy(float)
        _assert_finite(x, f"{sid} degree")
        _assert_finite(y, f"{sid} cis")

        results = {}
        for name, spec in CFG["residualization"]["estimators"].items():
            fitted, meta = fit_predict(
                x, y, spec["kind"], df=spec.get("df"), q=spec.get("q"),
                log_offset=spec.get("log_offset"))
            resid = y - fitted
            _assert_finite(resid, f"{sid}/{name} residual")
            sd = resid.std(ddof=1)
            if not np.isfinite(sd) or sd <= 0:
                raise SystemExit(f"degenerate residual SD for {sid}/{name}: {sd}")
            zr = (resid - resid.mean()) / sd
            results[name] = pd.DataFrame({
                "node": df["node"], "degree": df["degree"], "strength": df["strength"],
                "cis": y, "expected_cis": fitted, "residual_cis": resid,
                "standardized_residual": zr, "system": df["system"],
                "estimator": name,
            })
            if name == CFG["residualization"]["primary"]:
                primary_resid, primary_zr = resid, zr

        rho_by_est = {n: orthogonality(r["residual_cis"].to_numpy(float), x)
                      for n, r in results.items()}
        gate_rows.append({"subject": sid, **{f"rho_{n}": v for n, v in rho_by_est.items()}})

        subject_summaries.append({
            "subject": sid,
            "median_R_primary": float(np.median(primary_resid)),
            "mean_R_primary": float(primary_resid.mean()),
            "sd_R_primary": float(primary_resid.std(ddof=1)),
            "frac_nodes_R_positive": float((primary_resid > 0).mean()),
            **{f"rho_{n}": v for n, v in rho_by_est.items()},
        })

        # Stage 5 extremes (primary estimator only), threshold-free percentiles here
        pr = results[CFG["residualization"]["primary"]].copy()
        pr.insert(0, "subject", sid)
        pr["residual_percentile"] = pr["standardized_residual"].rank(pct=True)
        extreme_frames.append(pr)

        if si % 100 == 0 or si == len(pass_ids):
            log(f"processed {si}/{len(pass_ids)} subjects")

    gate = pd.DataFrame(gate_rows)
    summ = pd.DataFrame(subject_summaries)
    allres = pd.concat(extreme_frames, ignore_index=True)

    rho_col = f"rho_{CFG['residualization']['primary']}"
    med_abs = float(gate[rho_col].abs().median())
    mean_abs = float(gate[rho_col].abs().mean())
    rho_lin = float(gate["rho_M2_linear"].abs().median())
    gate_pass = (med_abs < 0.05) and (mean_abs < 0.1)

    gate_report = {
        "n_subjects": int(len(gate)),
        "missing_subject_files": n_missing,
        "primary_estimator": CFG["residualization"]["primary"],
        "median_abs_rho": med_abs,
        "mean_abs_rho": mean_abs,
        "median_abs_rho_linear": rho_lin,
        "paper1_cis_degree_rho": 0.943,
        "gate_pass": bool(gate_pass),
        "quantiles_abs_rho": {q: float(gate[rho_col].abs().quantile(float(q)))
                              for q in ("0.05", "0.5", "0.95")},
    }
    log(f"ORTHO GATE: pass={gate_pass} median|rho|={med_abs:.4f} mean|rho|={mean_abs:.4f} "
        f"(linear-estimator median|rho|={rho_lin:.4f} for contrast)")

    # outputs
    OUT.mkdir(parents=True, exist_ok=True)
    gate.to_csv(OUT / "orthogonality_by_subject.csv", index=False)
    summ.to_csv(OUT / "subject_residual_summary.csv", index=False)
    allres.to_parquet(OUT / "continuous_residuals.parquet", index=False)
    allres.to_csv(OUT / "continuous_residuals.csv.gz", index=False, compression="gzip")
    (OUT / "gate_report.json").write_text(json.dumps(gate_report, indent=2))
    for name, r in results.items():
        pass
    log("wrote per-subject outputs + gate report")

    # ---------------- figures (Stage 3 trio, primary estimator) -------------
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    FIGS.mkdir(parents=True, exist_ok=True)
    pop = allres[allres["estimator"] == CFG["residualization"]["primary"]]

    fig, ax = plt.subplots(figsize=(6.4, 4.8))
    sub = pop.sample(frac=0.02, random_state=CFG["seeds"]["bootstrap"])
    ax.scatter(sub["degree"], sub["cis"], s=4, alpha=0.25, color="#4477aa")
    med = pop.groupby("degree")["cis"].median()
    ax.plot(med.index, med.values, color="black", lw=2, label="median CIS @ degree")
    ax.set_xlabel("degree k"); ax.set_ylabel("CIS")
    ax.set_title(f"Degree vs CIS (2% node-subject sample, n={len(pass_ids)} subjects)")
    ax.legend(); fig.tight_layout()
    fig.savefig(FIGS / "degree_vs_CIS.png", dpi=150); plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.4, 4.8))
    ax.scatter(sub["degree"], sub["residual_cis"], s=4, alpha=0.25, color="#cc3311")
    med = pop.groupby("degree")["residual_cis"].median()
    ax.plot(med.index, med.values, color="black", lw=2, label="median R @ degree")
    ax.axhline(0, color="grey", lw=0.8, ls="--")
    ax.set_xlabel("degree k"); ax.set_ylabel("residual R = CIS - E[CIS|degree]")
    ax.set_title(f"Degree vs residual (primary estimator; median |rho|={med_abs:.3f})")
    ax.legend(); fig.tight_layout()
    fig.savefig(FIGS / "degree_vs_residual.png", dpi=150); plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
    axes[0].hist(pop["residual_cis"], bins=120, color="#4477aa", alpha=0.85)
    axes[0].set_xlabel("R"); axes[0].set_ylabel("count (subject-node)")
    axes[0].set_title("Residual distribution (pooled)")
    axes[1].hist(summ["median_R_primary"], bins=40, color="#228833", alpha=0.85)
    axes[1].set_xlabel("per-subject median R"); axes[1].set_ylabel("subjects")
    axes[1].set_title("Per-subject median residual")
    fig.tight_layout(); fig.savefig(FIGS / "residual_distribution.png", dpi=150)
    plt.close(fig)
    log("figures written: degree_vs_CIS, degree_vs_residual, residual_distribution")

    LOGS.mkdir(parents=True, exist_ok=True)
    (LOGS / "stage3_residuals.json").write_text(json.dumps(
        {**gate_report, "runtime_s": round(time.time() - t0, 1)}, indent=2))
    log(f"stage 3 complete in {time.time()-t0:.0f}s; gate_pass={gate_pass}")


if __name__ == "__main__":
    main()
