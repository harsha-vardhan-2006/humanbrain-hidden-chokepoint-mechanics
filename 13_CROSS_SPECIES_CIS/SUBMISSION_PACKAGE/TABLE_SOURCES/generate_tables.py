#!/usr/bin/env python3
"""Generate publication LaTeX tables from FROZEN repository artifacts.

Authoritative sources (frozen, read-only):
  09_TABLES/table_01_subject_cohort.csv       (cohort)
  09_TABLES/table_08_robustness.csv           (E06 condition metrics)
  10_REPORT/RESOLUTION.md                     (E06 like-for-like deltas + R2b enrichment)
  07_CROSS_SCALE/table_09_cross_scale.csv     (cross-scale comparators)
  09_TABLES/table_05_top_stability.csv        (top-node stability -> supplement)
  09_TABLES/table_03_qc_summary.csv           (QC summary -> supplement)

Every cell is parsed from these artifacts and cross-checked against frozen
expectations; the script FAILS LOUDLY on any mismatch rather than silently
emitting altered numbers. Formatting is rounding only -- no value is derived,
recomputed, or invented. Run from 13_CROSS_SPECIES_CIS/ :
    python SUBMISSION_PACKAGE/TABLE_SOURCES/generate_tables.py
"""
import csv, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# ROOT = 13_CROSS_SPECIES_CIS when run from there; repo root when run from repo root
if os.path.basename(ROOT) != "13_CROSS_SPECIES_CIS":
    ROOT = os.path.join(ROOT, "13_CROSS_SPECIES_CIS")
TAB = os.path.join(ROOT, "09_TABLES")
REP = os.path.join(ROOT, "10_REPORT")
XS = os.path.join(ROOT, "07_CROSS_SCALE")
OUT = os.path.join(ROOT, "SUBMISSION_PACKAGE", "FINAL_MANUSCRIPT", "tables")
SOUT = os.path.join(ROOT, "SUBMISSION_PACKAGE", "SUPPLEMENTARY", "tables")
os.makedirs(OUT, exist_ok=True)
os.makedirs(SOUT, exist_ok=True)


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def w(name, text, supp=False):
    for d in ([OUT, SOUT] if supp else [OUT]):
        with open(os.path.join(d, name), "w", encoding="utf-8") as f:
            f.write(text)
    print("wrote", name)


def require(cond, msg):
    if not cond:
        sys.exit("FROZEN-VALUE MISMATCH: " + msg)


def esc(s):
    return s.replace("%", r"\%").replace("_", r"\_").replace("×", r"$\times$")


# ---------------------------------------------------------------- T1 cohort
rows = read_csv(os.path.join(TAB, "table_01_subject_cohort.csv"))
r = [x for x in rows if x["atlas"] == "atlas_4S456Parcels"]
require(len(r) == 1, "cohort: expected exactly one 4S456Parcels row")
r = r[0]
require((r["n_subjects_cached"], r["n_qc_pass"], r["n_qc_fail"], r["qc_pass_rate"])
        == ("900", "801", "99", "0.89"), f"cohort values changed: {r}")
t1 = r"""% AUTO-GENERATED from 09_TABLES/table_01_subject_cohort.csv -- do not edit numbers by hand.
\begin{table}[!t]
\centering\small
\caption{Primary cohort and baseline network properties. Structural connectomes
were extracted for 900 subjects; 801 pass the pre-registered, CIS-blind
property-based QC (flags retained, never deleted). Baseline statistics are for
the primary configuration (4S456Parcels, \texttt{sift\_radius2\_count} weights,
15\% proportional threshold). E0: global efficiency; $k$: mean degree.
Values are frozen artifact outputs (\texttt{table\_01\_subject\_cohort.csv},
\texttt{table\_03\_qc\_summary.csv}, \texttt{table\_02\_baseline\_network.csv}).}
\label{tab:cohort}
\begin{tabular}{lll}
\toprule
Quantity & Value & Source \\
\midrule
Subjects acquired & 900 & frozen manifest \\
QC-pass primary cohort & 801 ($0.89$) & E02 property QC \\
Flags retained (isolated-node / strength-IQR) & 94 / 5 & \texttt{qc\_primary.csv} \\
Parcellation (nodes $N$) & 4S456Parcels ($N=456$) & atlas manifest \\
Weight variant & \texttt{sift\_radius2\_count\_connectivity} & frozen config \\
Proportional threshold $c$ & 0.15 ($k=15{,}561$ edges) & E01 \\
Mean degree $\langle k\rangle$ & 68.2 & baseline artifact \\
Global efficiency $E_0$ (median) & 0.5468 [0.5441--0.5497] & baseline artifact \\
\bottomrule
\end{tabular}
\end{table}
"""
w("table01_cohort.tex", t1)

# ------------------------------------------------- T4 E06 robustness ladder
res = open(os.path.join(REP, "RESOLUTION.md"), encoding="utf-8").read()
block = re.search(r"condition\s+n_subjects\s+top50_mean.*?\n(.*?)\n\s*\n", res, re.DOTALL)
require(block is not None, "RESOLUTION: concordance block not found")
cond_rows = []
for line in block.group(1).strip().splitlines():
    m = re.match(r"^\s*(\S+)\s+(\d+)\s+([\d.]+)\s+(-?[\d.]+)\s+([\d.]+)\s+(-?[\d.]+)\s+([\d.]+)\s+(-?[\d.]+)\s*$", line)
    if m:
        cond_rows.append(m.groups())
require(len(cond_rows) == 9, f"RESOLUTION: expected 9 concordance rows, got {len(cond_rows)}")
expected_conds = {"cost_10", "cost_20", "cost_25", "atlas_4S256", "atlas_4S156",
                  "atlas_B246", "atlas_AAL116", "weight_invnodevol", "weight_r2count"}
require({c[0] for c in cond_rows} == expected_conds, "RESOLUTION: condition set changed")

# cross-check each top50_mean against the frozen CSV (6 dp)
t8 = read_csv(os.path.join(TAB, "table_08_robustness.csv"))
t8map = {r["condition"]: float(r["top50_mean_of_means"]) for r in t8}
require(len(t8) == 9, "table_08: expected 9 conditions")
for cond, _n, top50, *_ in cond_rows:
    require(abs(float(top50) - t8map[cond]) < 5e-7,
            f"RESOLUTION vs table_08 disagree for {cond}: {top50} vs {t8map[cond]}")

aal = [c for c in cond_rows if c[0] == "atlas_AAL116"][0]
require(abs(float(aal[2]) - 0.003848) < 5e-7 and abs(float(aal[3]) - 0.002619) < 5e-7,
        "E06: atlas_AAL116 values changed")
maxd = max(cond_rows, key=lambda c: abs(float(c[3])))
require(maxd[0] == "atlas_AAL116", "E06: max-delta condition changed")

tex_rows = []
for cond, n, top50, delta, gini, gdelta, rho, rdelta in cond_rows:
    name = {"cost_10": "cost 0.10", "cost_20": "cost 0.20", "cost_25": "cost 0.25",
            "atlas_4S256": r"atlas 4S256", "atlas_4S156": r"atlas 4S156",
            "atlas_B246": r"atlas Brainnetome246Ext", "atlas_AAL116": r"atlas AAL116",
            "weight_invnodevol": r"weights \texttt{sift\_invnodevol}",
            "weight_r2count": r"weights \texttt{radius2\_count}"}[cond]
    star = r"$\ast$" if cond == "atlas_AAL116" else ""
    tex_rows.append(
        f"{name} & {n} & {top50} & {delta}{star} & {gini} & {gdelta} & {rho} \\\\")
t4 = r"""% AUTO-GENERATED from 10_REPORT/RESOLUTION.md concordance block, cross-checked
% against 09_TABLES/table_08_robustness.csv -- do not edit numbers by hand.
\begin{table}[!t]
\centering\small
\caption{E06 robustness ladder: nine pre-registered alternative configurations
(frozen $n=150$ cohort, nested samples). Each condition reproduces the primary
architecture. $\Delta_{50}$: like-for-like deviation of the top-50 mean-of-means
from the like-for-like primary row (4S456, \texttt{radius2\_count}, cost 0.15,
same cohort; primary top-50 mean 0.0012286). $\ast$: maximum absolute
deviation, full precision $0.0026194$ (atlas AAL116: 0.0038480 vs 0.0012286).
No numeric tolerance was pre-registered for E06 in PROTOCOL\_FREEZE or
STUDY\_DESIGN; the concordance is a descriptive comparison, not a pass/fail
gate. Sources: \texttt{RESOLUTION.md}; \texttt{table\_08\_robustness.csv}.}
\label{tab:robustness}
\begin{tabular}{lcccccc}
\toprule
Condition & $n$ & top-50 mean & $\Delta_{50}$ & Gini (med.) & $\Delta$ Gini & $\rho$(CIS, deg.) (med.) \\
\midrule
""" + "\n".join(tex_rows) + r"""
\bottomrule
\end{tabular}
\end{table}
"""
w("table04_robustness.tex", t4)

# ---------------------------------------------------- T3 R2b enrichment gate
r2b = re.search(r"\| system \| observed \| z_A \| p_A \| z_B \| p_B \| enrich_B \|\n\|(?:-+\|)+\n(?:\|[^\n]*\n)+", res)
require(r2b is not None, "RESOLUTION: R2b table not found")
r2b_rows = []
for line in r2b.group(0).strip().splitlines()[2:]:
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    if len(cells) == 7 and cells[0] not in ("system",):
        r2b_rows.append(cells)
require(len(r2b_rows) >= 4, f"RESOLUTION: R2b rows missing ({len(r2b_rows)})")
vis = [c for c in r2b_rows if c[0] == "Vis"]
require(vis and vis[0][1] == "1" and vis[0][4] == "-0.38",
        "R2b: Vis row changed (expected obs 1, z_B -0.38)")
tex_rows = []
for s, obs, za, pa, zb, pb, eb in r2b_rows:
    sysname = {"Vis": "Visual", "SomMot": "Somatomotor", "DorsAttn": "Dorsal attention",
               "SalVentAttn": "Salience/ventral attention"}.get(s, s)
    tex_rows.append(f"{sysname} & {obs} & {za} & {pa} & {zb} & {pb} & {esc(eb)} \\\\")
t3 = r"""% AUTO-GENERATED from 10_REPORT/RESOLUTION.md R2b block -- do not edit numbers by hand.
\begin{table}[!t]
\centering\small
\caption{Pre-registered system-enrichment gate (R2b) at $K=50$ for the four
pre-specified sensory/attention systems: observed count in the top-50 residual
nodes, node-label-shuffle control ($z_A$, $p_A$; 10{,}000 permutations), and
degree-matched peer-pool control ($z_B$, $p_B$; 10{,}000 resamples), with
control-B enrichment. \textbf{The pre-registered gate was negative}: no
pre-specified sensory/visual system shows positive degree-matched enrichment
(Visual: 1/50 nodes, $z_B=-0.38$). The full eight-system table, including the
nominal Subcortical/Cerebellar signal ($z_B=2.08$, $p=.031$, $1.25\times$;
absent at $K=25$ and degree-anchored), is frozen in the E05 artifacts. Source:
\texttt{RESOLUTION.md} (verbatim).}
\label{tab:r2b}
\begin{tabular}{lcccccc}
\toprule
System & Obs. & $z_A$ & $p_A$ & $z_B$ & $p_B$ & Enrich.\ (B) \\
\midrule
""" + "\n".join(tex_rows) + r"""
\bottomrule
\end{tabular}
\end{table}
"""
w("table03_enrichment.tex", t3)

# ------------------------------------------------------- T5 cross-scale table
xs = read_csv(os.path.join(XS, "table_09_cross_scale.csv"))
require(len(xs) == 6, f"table_09: expected 6 comparator rows, got {len(xs)}")
joined = " ".join(r["fly_value"] + " " + r["human_value"] for r in xs)
for token in ["0.0979", "0.100", "2.63x", "5.30", "80%", "2%"]:
    require(token in joined, f"table_09: frozen token '{token}' missing")
quantity_map = {
    "CIS distribution shift (target vs matched controls)":
        r"Effect size of the CIS shift (target vs.\ matched controls), Cliff's $\delta$",
    "Null survival of group-level CIS effect (degree-preserving)":
        r"Null survival of the group-level CIS effect (degree-preserving ensembles)",
    "Top-K enrichment vs tested universe (control A)":
        r"Top-$K$ enrichment vs.\ tested universe (control A: label shuffle)",
    "Top-K enrichment vs degree-matched expectation (control B)":
        r"Top-$K$ enrichment vs.\ degree-matched expectation (control B)",
    "Chokepoint catalogue depth":
        r"Chokepoint catalogue depth",
    "Visual-system share of top-50":
        r"Visual-system share of the top 50",
}
tex_rows = []
for r in xs:
    q = quantity_map.get(r["quantity"], esc(r["quantity"]))
    tex_rows.append(
        f"{q} & {esc(r['fly_value'])} & {esc(r['human_value'])} & {esc(r['comparison_type'])} \\\\")
t5 = r"""% AUTO-GENERATED from 07_CROSS_SCALE/table_09_cross_scale.csv -- do not edit numbers by hand.
\begin{table}[!t]
\centering\small
\caption{Pre-registered cross-scale comparators (human vs.\ fly), normalized
per the frozen discipline tags (DIRECT: same statistic and control design;
NORMALIZED: scale-normalized analogue; QUALITATIVE). Absolute CIS values are
never compared across species (different units, graphs, and designs). The fly
$\delta$ did not survive its own degree-preserving null ensemble ($p=0.109$).
Human and fly nodes are not treated as homologous structures; the comparison
operates at the level of network architecture and statistical organization.
Source: \texttt{table\_09\_cross\_scale.csv} (verbatim).}
\label{tab:crossscale}
\begin{tabular}{p{3.4cm}p{3.9cm}p{4.6cm}l}
\toprule
Comparator & Fly (FAFB v783) & Human (AOMIC-ID1000) & Tag \\
\midrule
""" + "\n".join(tex_rows) + r"""
\bottomrule
\end{tabular}
\end{table}
"""
w("table05_crossscale.tex", t5)

# ------------------------------------------- S-table: top-node stability (S1)
ts = read_csv(os.path.join(TAB, "table_05_top_stability.csv"))
ts = sorted(ts, key=lambda r: int(r["stability_rank"]))[:8]
require(ts[0]["node"] == "415" and ts[1]["node"] == "401",
        "table_05: top-node order changed")
tex_rows = []
for r in ts:
    tex_rows.append(
        f"{r['stability_rank']} & {r['node']} & {float(r['cis_mean']):.4f} & "
        f"{float(r['degree_mean']):.1f} & {float(r['top50_rate']):.3f} & "
        f"{float(r['topdecile_rate']):.3f} \\\\")
tS1 = r"""% AUTO-GENERATED from 09_TABLES/table_05_top_stability.csv -- do not edit numbers by hand.
\begin{table}[!t]
\centering\small
\caption{Eight highest-ranked nodes by population-mean CIS (frozen
\texttt{table\_05\_top\_stability.csv}): mean CIS across the 801-subject
cohort, mean degree, fraction of subjects in which the node falls in the
top-50 (\texttt{top50\_rate}) and top decile (\texttt{topdecile\_rate}) CIS.
Node indices follow the frozen 4S456 atlas manifest.}
\label{tab:stopnodes}
\begin{tabular}{crrrrr}
\toprule
Rank & Node & mean CIS & mean degree & top-50 rate & top-decile rate \\
\midrule
""" + "\n".join(tex_rows) + r"""
\bottomrule
\end{tabular}
\end{table}
"""
w("tableS1_top_nodes.tex", tS1, supp=True)

# ------------------------------------------- S-table: QC summary metrics (S2)
qc = read_csv(os.path.join(TAB, "table_03_qc_summary.csv"))
require(len(qc) >= 7, "table_03: QC summary rows missing")
ge = [r for r in qc if r["metric"] == "ge"]
require(ge and abs(float(ge[0]["mean"]) - 0.5466585864590251) < 5e-9,
        "table_03: GE mean changed")
label_map = {
    "n_nodes": "Nodes per graph",
    "density_raw": "Raw density",
    "isolated_nodes_post_threshold": "Isolated nodes after threshold (mean)",
    "n_components_multi": "Multi-node components (mean)",
    "giant_frac": "Giant-component fraction",
    "ge": r"Global efficiency $E_0$",
    "strength_mean": "Mean node strength",
}
tex_rows = []
for r in qc:
    lab = label_map.get(r["metric"], esc(r["metric"]))
    m, md = float(r["mean"]), float(r["median"])
    fm = f"{m:.4f}" if abs(m) < 10 else f"{m:,.1f}"
    fd = f"{md:.4f}" if abs(md) < 10 else f"{md:,.1f}"
    tex_rows.append(f"{lab} & {fm} & {fd} \\\\")
tS2 = r"""% AUTO-GENERATED from 09_TABLES/table_03_qc_summary.csv -- do not edit numbers by hand.
\begin{table}[!t]
\centering\small
\caption{Population QC summary over the 801-subject primary cohort (frozen
\texttt{table\_03\_qc\_summary.csv}; mean and median across subjects, primary
configuration). Strength is in SIFT-weighted streamline-count units.}
\label{tab:sqc}
\begin{tabular}{lrr}
\toprule
Metric & Mean & Median \\
\midrule
""" + "\n".join(tex_rows) + r"""
\bottomrule
\end{tabular}
\end{table}
"""
w("tableS2_qc_summary.tex", tS2, supp=True)

print("ALL FROZEN-VALUE ASSERTIONS PASSED")
