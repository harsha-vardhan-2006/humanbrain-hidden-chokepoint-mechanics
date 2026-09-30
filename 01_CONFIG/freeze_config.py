"""Freeze Paper 2 machine configuration into config.json.

Writes 01_CONFIG/config.json with verified paths, frozen seeds, estimator
settings, and provenance (git SHA, timestamps). Run once; re-runs are
idempotent (same inputs -> same file except timestamp).

Frozen discipline: config.json is the single source consumed by all Paper 2
scripts; editing it after freeze = amendment (append note to CONFIG_FREEZE.md).
"""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

TREE = Path(__file__).resolve().parents[1]          # 02_PAPER2_HIDDEN_CHOKEPOINTS
STUDY = TREE.parent                                  # 13_CROSS_SPECIES_CIS
REPO = STUDY.parent                                  # humanbrain/

CONFIG = {
    "identity": {
        "paper": 2,
        "working_title": "Hidden Chokepoints: Graph-Geometric Determinants of "
                         "Degree-Independent Control Impact in Connectome Networks",
        "frozen_utc": None,  # filled at runtime
    },
    "paths": {
        "subject_cis_dir": str(STUDY / "04_CIS" / "subject_cis"),
        "qc_primary": str(STUDY / "03_BASELINE" / "qc_primary.csv"),
        "e03_summary": str(STUDY / "04_CIS" / "e03_summary.json"),
        "e03b_per_subject": str(STUDY / "04_CIS" / "degree_strength_control_per_subject.csv"),
        "e03b_pairs": str(STUDY / "04_CIS" / "degree_strength_control_results.csv"),
        "atlas_labels": str(STUDY / "00_MANIFEST" / "manifests" / "atlas_4S456_system_labels.csv"),
        "out_degree_control": str(TREE / "04_DEGREE_CONTROL"),
        "out_figures": str(TREE / "09_FIGURES"),
        "out_tables": str(TREE / "10_TABLES"),
        "out_logs": str(TREE / "14_LOGS"),
        "fly_e10b": str(REPO.parent / "fruitfly" / "results" / "final" / "e10b_final.json"),
    },
    "cohort": {
        "n_nodes": 456,
        "qc_source": "qc_primary.csv:qc_pass == True (Paper 1 frozen flags)",
        "secondary_full900": "descriptive only, never headline",
    },
    "residualization": {    "primary": "M1_spline4_raw",
    "estimators": {
        "M1_spline4_raw": {"kind": "spline_ols", "y": "cis",
                           "x": "degree", "df": 4, "amendment": 2},
        "M2_linear": {"kind": "ols", "y": "cis", "x": "degree"},
            "P_df2": {"kind": "poly", "df": 2}, "P_df3": {"kind": "poly", "df": 3},
            "P_df5": {"kind": "poly", "df": 5}, "P_df6": {"kind": "poly", "df": 6},
            "Q_bin20": {"kind": "quantile_bins", "q": 20, "agg": "median"},
        },
        "orthogonality_gate": {
            "statistic": "Spearman(R_i, k_i) per subject",
            "pass": "median |rho_s| < 0.05 AND mean |rho_s| < 0.1 (primary estimator)",
        },
        "cross_check": {
            "source": "e03b_per_subject (matched-pair delta, Paper 1)",
            "expectation": "sign agreement >= 90% on per-subject median-R sign vs delta sign; "
                           "subject-level Spearman(median_R, delta) reported; |rho| < 0.5 blocks",
        },
    },
    "extremes": {
        "thresholds_zr": {"top": [0.01, 0.05], "bottom": [0.01, 0.05]},
        "note": "within-subject percentiles of ZR; pre-registered before any identity inspection",
    },
    "seeds": {"bootstrap": 20270927, "nulls_cis": "100+i (Stage 15)", "nulls_feature": 20270927},
    "bootstrap": {"n_resamples": 10000, "unit": "subject"},
}


def git_sha() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO,
                              capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return "unavailable"


def main() -> None:
    CONFIG["identity"]["frozen_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    CONFIG["identity"]["amendments"] = [1]
    CONFIG["provenance"] = {"git_sha": git_sha(), "writer": str(Path(__file__).name)}
    out = Path(__file__).resolve().parent / "config.json"
    out.write_text(json.dumps(CONFIG, indent=2))
    print(f"wrote {out}")
    # fail loud on missing inputs
    for key, p in CONFIG["paths"].items():
        if not Path(p).exists():
            raise SystemExit(f"MISSING INPUT PATH ({key}): {p}")
    print("all input paths verified")


if __name__ == "__main__":
    main()
