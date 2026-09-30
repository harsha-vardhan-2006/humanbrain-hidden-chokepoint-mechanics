#!/usr/bin/env python3
"""Cross-platform master runner for the frozen Paper 2 study.

Usage:
    python run_all.py --verify        # V01-V12 independent verification
    python run_all.py --qc            # full QC sweep
    python run_all.py --proxy         # null-estimator equivalence validation
    python run_all.py --all           # all of the above (default)

Replaces Windows-specific `py -3.13` / bash-chain instructions with a single
portable entry point. Requires Python >= 3.11 and `pip install -r
requirements.txt`. Any gate failure exits non-zero (fail loud).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

TREE = Path(__file__).resolve().parent
PY = sys.executable

STEPS = {
    "--verify": [str(TREE / "13_MANUSCRIPT" / "verify_stage24.py")],
    "--qc": [str(TREE / "QC" / "run_full_qc.py")],
    "--proxy": [str(TREE / "06_NULL_MODELS" / "validate_null_proxy.py")],
}


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if a in STEPS]
    if not args or "--all" in args:
        args = ["--verify", "--qc", "--proxy"]
    rc = 0
    for a in args:
        script = STEPS[a][0]
        if not Path(script).exists():
            print(f"[MISS] {a}: {script} not found")
            rc = rc or 1
            continue
        print(f"\n=== {a}: {Path(script).name} ===")
        r = subprocess.run([PY, script], cwd=TREE)
        rc = rc or r.returncode
    print(f"\nrun_all: exit {rc}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
