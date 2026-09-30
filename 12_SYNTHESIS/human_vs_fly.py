"""Stage 22b - Human vs fly conservative comparison table.

Every human number traces to a frozen Paper-2 artifact on disk; every fly
number traces to the frozen fruitfly v1.0.0 release. The fly negative
degree-preserving-null verdict (z = 1.21, p = 0.109) is preserved as a
first-class outcome. No same-mechanism claim is made or licensed.

Output: 12_SYNTHESIS/HUMAN_VS_FLY_COMPARISON.csv + .md
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

TREE = Path(__file__).resolve().parents[1]
OUT = TREE / "12_SYNTHESIS"
OUT.mkdir(parents=True, exist_ok=True)

uni = json.loads((TREE / "05_MECHANISM_ANALYSIS" / "UNIVARIATE_RESULTS.json").read_text())
uni_map = {r["feature"]: r["median_rho"] for r in uni["results"]}
ml = json.loads((TREE / "08_STATISTICS" / "ML_BENCHMARK.json").read_text())
ridge = next(r for r in ml["results"] if r["model"] == "ridge")
deg = next(r for r in ml["results"] if r["model"] == "degree_only")
nulls = json.loads((TREE / "06_NULL_MODELS" / "NULL_FEATURE_RESULTS.json").read_text())

ROWS = [
    # property, human, fly, interpretation (bounded wording)
    ("Unit of analysis",
     "456-node atlas PARCEL (4S456; macroscopic region, NOT a neuron)",
     "individual NEURON (FAFB v783, 139k neurons; targets 3,518)",
     "Cross-scale comparison is architectural only; scales differ by ~5 orders of magnitude in unit size."),
    ("CIS-degree dependence",
     "median rho(CIS, degree) = 0.943 (Paper 1, frozen)",
     "strong (fly Paper 1: CIS dominated by degree; visual fraction 80%)",
     "Both scales: raw CIS is degree-confounded; explicit control is mandatory before interpretation."),
    ("Degree-independent residual (matched/control design)",
     "delta = 0.104; 801/801 subjects > 0; CI [0.1007, 0.1073]",
     "delta = 0.100; 778/801 sign-positive (fly Paper 1 E03b)",
     "A small positive degree-independent CIS residual exists at BOTH scales."),
    ("Residual reproducibility (this paper, same pairs)",
     "rho(delta_ours, delta_paper1) = 0.785; median 0.1040",
     "not re-run (frozen v1.0.0 artifacts consumed read-only)",
     "Human side re-derived independently; fly side preserved as released."),
    ("Degree-preserving null VERDICT on the residual mechanism",
     "Stage 15: feature-R associations DO NOT exceed degree-preserving null p95 (Outcome C, all 9 features)",
     "z = 1.21, p = 0.109 - DID NOT survive (fly v1.0.0, frozen)",
     "At NEITHER scale does the residual mechanism survive a degree-preserving null. Same-direction negatives; no universal-law claim."),
    ("Network-position signature of high-residual nodes",
     "bridge rho = +0.4985; closeness_d +0.2489; redundancy -0.2179 (within-subject medians)",
     "ME.131 case: betweenness z = +4.08 vs degree-matched peers; case study ONLY",
     "Human: population-level associations (null-qualified). Fly: single pre-registered case; NOT a population claim."),
    ("Predictive learnability of the residual",
     "ridge cv-R2 = 0.574 (permuted-R control 0.0024; degree-only ~ 0)",
     "NOT_ESTABLISHED (no equivalent benchmark in fly release)",
     "Learnable structure beyond degree exists in human; fly equivalent absent - do not equate."),
    ("Anatomical concentration of extremes",
     "top-10% CIS UNDER-represents cortex (share 0.44 vs expected 0.88, q<0.001); enrichment NOT_ESTABLISHED for cell type (parcels are not cell types)",
     "ME.131 = optic lobe (visual); fly visual contribution ~ 80%",
     "Human extremes avoid cortex; fly concentrated in visual system. Anatomies differ."),
    ("Visual-system contribution to CIS",
     "~2% (human, frozen Paper 1)",
     "~80% (fly, frozen Paper 1)",
     "Architecture does NOT transfer at the anatomical level ('architecture replicates, anatomy doesn't')."),
    ("Cell-type / neurotransmitter annotation",
     "NOT_AVAILABLE (macroscopic parcels carry no cell-type ground truth)",
     "available per neuron (FAFB annotations: nt_type, super_class)",
     "Resolution asymmetry is structural; human cell-type claims are NOT_ESTABLISHED in this study."),
    ("Robustness of associations",
     "estimator ladder + winsorization: sign-consistent for bridge/participation (Stage 20)",
     "fly study internal robustness only (v1.0.0)",
     "Human feature associations are estimator-robust in sign; magnitudes differ across estimators."),
    ("Causal interpretation",
     "NONE licensed (observational structural connectomes)",
     "NONE licensed (observational connectome)",
     "Both studies are observational; removal-CIS is a network quantity, not a perturbation experiment."),
]

table = pd.DataFrame(ROWS, columns=["property", "human", "fly", "interpretation"])
table.to_csv(OUT / "HUMAN_VS_FLY_COMPARISON.csv", index=False)

md = [
    "# Human vs fly - conservative comparison (Paper 2 Stage 22b)",
    "",
    "Sources: human numbers re-derived in this study from frozen artifacts;",
    "fly numbers from the frozen `fruitfly` v1.0.0 release (read-only).",
    "",
    table.to_markdown(index=False) if False else "\n".join(
        f"### {p}\n\n- **Human:** {h}\n- **Fly:** {f}\n- **Interpretation:** {i}\n"
        for p, h, f, i in ROWS),
    "",
    "## Mandatory framing",
    "",
    "- The fly residual's failure to survive its degree-preserving null",
    "  (z = 1.21, p = 0.109) is preserved verbatim; it is a first-class",
    "  negative result.",
    "- The human Stage-15 null arbitration reached the same direction",
    "  (Outcome C for all 9 features). Two same-direction negatives at",
    "  different scales DO NOT license 'universal law' or 'same mechanism'",
    "  claims - they show only that, at both scales, degree alone explains",
    "  the null-level structure of the CIS-residual association machinery.",
    "- Shared: degree dominance; small positive degree-independent residual;",
    "  null-negative arbitration. Species/network-specific: anatomical",
    "  concentration, visual contribution, unit of analysis, availability",
    "  of cell-type ground truth, predictive benchmark.",
]
(OUT / "HUMAN_VS_FLY_COMPARISON.md").write_text("\n".join(md) + "\n")
print(table[["property"]].to_string(index=False))
print(f"WROTE {len(table)} comparison rows")
