"""Stage 5 - Pre-registered extreme-residual node extraction.

Thresholds frozen in CONFIG before any identity inspection:
top 1% / 5% and bottom 1% / 5% of within-subject standardized residual ZR.
Writes positive_extreme_nodes.csv, negative_extreme_nodes.csv, and refreshes
continuous_residuals.csv (parquet already written by Stage 3).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

TREE = Path(__file__).resolve().parents[1]
CFG = json.loads((TREE / "01_CONFIG" / "config.json").read_text())
OUT = Path(CFG["paths"]["out_degree_control"])
PRIMARY = CFG["residualization"]["primary"]


def main() -> None:
    df = pd.read_parquet(OUT / "continuous_residuals.parquet")
    df = df[df["estimator"] == PRIMARY].copy()

    if not np.isfinite(df["standardized_residual"].to_numpy()).all():
        raise SystemExit("non-finite ZR in continuous residuals — refusing")

    pos = df[df["standardized_residual"] >= df.groupby("subject")["standardized_residual"]
             .transform(lambda s: s.quantile(0.99))]
    pos1 = pos.copy(); pos1["threshold"] = "top1"
    pos5 = df[df["standardized_residual"] >= df.groupby("subject")["standardized_residual"]
              .transform(lambda s: s.quantile(0.95))].copy(); pos5["threshold"] = "top5"

    neg = df[df["standardized_residual"] <= df.groupby("subject")["standardized_residual"]
             .transform(lambda s: s.quantile(0.01))]
    neg1 = neg.copy(); neg1["threshold"] = "bottom1"
    neg5 = df[df["standardized_residual"] <= df.groupby("subject")["standardized_residual"]
              .transform(lambda s: s.quantile(0.05))].copy(); neg5["threshold"] = "bottom5"

    cols = ["subject", "node", "degree", "strength", "cis", "expected_cis",
            "residual_cis", "standardized_residual", "residual_percentile",
            "threshold", "system"]
    pd.concat([pos1, pos5], ignore_index=True)[cols].to_csv(
        OUT / "positive_extreme_nodes.csv", index=False)
    pd.concat([neg1, neg5], ignore_index=True)[cols].to_csv(
        OUT / "negative_extreme_nodes.csv", index=False)

    meta = {
        "primary_estimator": PRIMARY,
        "thresholds": "within-subject ZR quantiles (frozen): top1/top5/bottom1/bottom5",
        "n_positive_top1": int(len(pos1)), "n_positive_top5": int(len(pos5)),
        "n_negative_bottom1": int(len(neg1)), "n_negative_bottom5": int(len(neg5)),
        "n_subject_node_rows": int(len(df)),
        "note": "identity columns (system label) included for QC; biological "
                "interpretation of extremes deferred to later stages",
    }
    (OUT / "extremes_manifest.json").write_text(json.dumps(meta, indent=2))
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
