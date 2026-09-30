"""Paper 2 full QC runner (master-prompt §29 checks, adapted to this study).

Checks (each PASS/FAIL/WARNING, fail-loud collection, exit 1 on any FAIL):
  dataset presence (AOMIC cache, fly artifacts), node counts, atlas mapping
  completeness, annotation completeness, no duplicate node IDs, no missing
  critical CIS/residual values, no invalid p/q values, null ensemble size,
  figure existence, report/manuscript existence, verification gates rerun,
  secret-leak scan (env/key patterns).

Output: QC/FINAL_QC_REPORT.md  (and stdout summary).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

TREE = Path(__file__).resolve().parents[1]
STUDY = TREE.parent
REPO = STUDY.parent
QC = TREE / "QC"
QC.mkdir(exist_ok=True)

results: list[tuple[str, str, str]] = []  # (status, check, detail)


def add(status: str, check: str, detail: str = "") -> None:
    results.append((status, check, detail))
    print(f"[{status}] {check} {('(%s)' % detail) if detail else ''}")


def main() -> None:
    # 1. dataset presence (layout-aware for the flattened standalone repo:
    # raw AOMIC cache parts live in the parent tree and are NOT redistributed;
    # fall back to verifying the frozen derived matrices this study consumed)
    cache_candidates = [
        TREE / ".." / "13_CROSS_SPECIES_CIS" / "02_PREPROCESSING" / "cache_parts",
        Path("D:/humanbrain/humanbrain/13_CROSS_SPECIES_CIS/02_PREPROCESSING/cache_parts"),
    ]
    n_cache = 0
    cache_seen = None
    for c in cache_candidates:
        if c.exists():
            n_cache = len(list(c.glob("*")))
            cache_seen = c
            if n_cache >= 20:
                break
    if n_cache >= 20:
        add("PASS", "AOMIC cache parts present", f"{n_cache} files in {cache_seen}")
    else:
        # fallback: frozen derived matrices with exact expected shapes
        try:
            fm = pd.read_parquet(TREE / "03_FEATURE_EXTRACTION" / "NODE_FEATURE_MATRIX.parquet")
            rd = pd.read_parquet(TREE / "04_DEGREE_CONTROL" / "continuous_residuals.parquet")
            ok = (fm["subject"].nunique() == 801 and len(fm) == 801 * 456
                  and len(rd) == 801 * 456)
            add("PASS" if ok else "FAIL",
                "Dataset lineage via frozen derived matrices (raw cache not "
                "redistributed; parent-tree cache absent)",
                f"feature matrix {fm.shape}, residuals {rd.shape}")
        except Exception as e:  # noqa: BLE001 - fail loud with reason
            add("FAIL", "Dataset lineage", f"no raw cache and derived check failed: {e}")
    fly_candidates = [
        TREE / ".." / "fruitfly" / "results" / "tables" / "e14_chokepoint_catalogue_v2.csv",
        Path("D:/humanbrain/fruitfly/results/tables/e14_chokepoint_catalogue_v2.csv"),
    ]
    fly_tab = next((p for p in fly_candidates if p.exists()), None)
    add("PASS" if fly_tab is not None else "FAIL", "Fly frozen artifacts reachable",
        str(fly_tab))

    # 2. atlas mapping / annotation completeness
    ann = pd.read_csv(TREE / "results_annotation" / "human_node_biological_annotations.csv")
    add("PASS" if len(ann) == 456 and ann["node_id"].is_unique else "FAIL",
        "Annotation table 456 unique nodes", f"rows={len(ann)}")
    critical = ["parcel_name", "hemisphere", "major_structure", "functional_network",
                "annotation_status"]
    ok = all(ann[c].notna().all() for c in critical)
    add("PASS" if ok else "FAIL", "Critical annotation fields complete")
    cell_cols = ["cell_class", "neuronal_class", "excitatory_inhibitory",
                 "neurotransmitter", "transcriptomic_class"]
    na_ok = all((ann[c] == "NOT_AVAILABLE").all() for c in cell_cols)
    add("PASS" if na_ok else "WARNING", "Cell-type fields uniformly NOT_AVAILABLE",
        "discipline: no invented biology" if na_ok else "check values")

    # 3. master table integrity
    m = pd.read_csv(TREE / "results_annotation" / "human_cis_biological_master.csv")
    add("PASS" if len(m) == 456 and m["node_id"].is_unique else "FAIL",
        "Master table 456 unique nodes")
    add("PASS" if m["CIS"].notna().all() and m["residual"].notna().all() else "FAIL",
        "No missing CIS/residual values")
    qok = (m["q_bh"].between(0, 1)).all() and (m["p_one_sided"].between(0, 1)).all()
    add("PASS" if qok else "FAIL", "p/q values in [0,1]")

    # 4. null ensemble size
    n_rec = sum(1 for line in open(TREE / "06_NULL_MODELS" / "null_records_checkpoint.jsonl")
                if line.strip())
    add("PASS" if n_rec == 1200 else "FAIL", "Null ensemble 1200 records",
        f"n={n_rec}")
    add("PASS" if (TREE / "06_NULL_MODELS" / "NULL_FEATURE_RESULTS.json").exists()
        else "FAIL", "Null arbitration JSON present")

    # 5. key results present
    for f in ("05_MECHANISM_ANALYSIS/UNIVARIATE_RESULTS.json",
              "08_STATISTICS/ML_BENCHMARK.json",
              "08_STATISTICS/SUBJECT_AWARE_MODEL.json",
              "07_ROBUSTNESS/ROBUSTNESS_MATRIX.csv",
              "07_ROBUSTNESS/NEGATIVE_CONTROLS.json",
              "12_SYNTHESIS/CHOKEPOINT_SENSITIVITY.csv",
              "12_SYNTHESIS/HUMAN_VS_FLY_COMPARISON.csv"):
        add("PASS" if (TREE / f).exists() else "FAIL", f"artifact: {f}")

    # 6. figures
    figs = list((TREE / "09_FIGURES").glob("*.png"))
    add("PASS" if len(figs) >= 10 else "WARNING", "Figure set size",
        f"{len(figs)} PNGs")

    # 7. manuscript package
    for f in ("MANUSCRIPT.md", "SUPPLEMENTARY.md", "FIGURE_LEGENDS.md",
              "REPRODUCIBILITY.md"):
        add("PASS" if (TREE / "13_MANUSCRIPT" / f).exists() else "FAIL",
            f"manuscript: {f}")

    # 8. verification gates (rerun V01-V12 quietly)
    import subprocess
    r = subprocess.run([sys.executable, str(TREE / "13_MANUSCRIPT" / "verify_stage24.py")],
                       capture_output=True, text=True)
    n_pass = r.stdout.count("[PASS]")
    add("PASS" if (r.returncode == 0 and n_pass == 12) else "FAIL",
        "Stage-24 gates V01-V12", f"{n_pass}/12 PASS")

    # 9. secret scan (study tree text files)
    pat = re.compile(r"(api[_-]?key|secret|password|token)\s*[=:]", re.I)
    hits: list[str] = []
    skip_dirs = {".git", "__pycache__", ".pytest_cache"}
    for p in TREE.rglob("*"):
        if p.is_file() and not (skip_dirs & set(p.parts)) and p.suffix in {
                ".py", ".md", ".json", ".csv", ".sh", ".txt", ".yml", ".yaml"}:
        # 20 MB JSONL null checkpoint is the only big file; scan a prefix
            try:
                with open(p, "r", errors="ignore") as fh:
                    head = fh.read(2_000_000)
                if pat.search(head):
                    hits.append(str(p.relative_to(TREE)))
            except OSError:
                pass
    add("PASS" if not hits else "FAIL", "Secret-pattern scan", str(hits[:5]))
    env_files = [str(p.relative_to(TREE)) for p in TREE.rglob(".env")]
    add("PASS" if not env_files else "FAIL", "No .env files in tree", str(env_files))

    # 10. git hygiene (informational at study level; handled at repo root)
    add("WARNING", "Git cleanliness checked at REPO ROOT before commit",
        "see repo-root QC + release step")

    n_pass = sum(1 for s, _, _ in results if s == "PASS")
    n_fail = sum(1 for s, _, _ in results if s == "FAIL")
    n_warn = sum(1 for s, _, _ in results if s == "WARNING")
    lines = ["# FINAL QC REPORT — Paper 2 (2026-09-30)", "",
             f"TOTAL PASS: {n_pass}   TOTAL FAIL: {n_fail}   TOTAL WARNING: {n_warn}",
             "", "| Status | Check | Detail |", "|---|---|---|"]
    lines += [f"| {s} | {c} | {d} |" for s, c, d in results]
    verdict = "PROJECT QC PASS" if n_fail == 0 else "PROJECT QC FAIL — DO NOT RELEASE"
    lines += ["", f"**Verdict: {verdict}**"]
    (QC / "FINAL_QC_REPORT.md").write_text("\n".join(lines) + "\n")
    print(f"\nQC summary: PASS={n_pass} FAIL={n_fail} WARNING={n_warn} -> {verdict}")
    if n_fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
