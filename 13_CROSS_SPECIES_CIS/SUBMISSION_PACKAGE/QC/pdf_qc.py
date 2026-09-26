"""PDF QC for the final manuscript package (read-only checks)."""
import re
import sys
from pathlib import Path

from pypdf import PdfReader

HERE = Path(__file__).resolve().parent
MAIN = HERE.parent / "FINAL_MANUSCRIPT" / "main.pdf"
SUPP = HERE.parent / "SUPPLEMENTARY" / "supplementary.pdf"

# Imperative 'Insert' only (not 'inserted'/'insertion' inside normal words).
INSERT_RE = re.compile(r"\bInsert\b(?!\s+(a|an|the|ion|ions|ed|ing|s)\b)")
PLACEHOLDER_RES = [re.compile(p, re.I) for p in
                   (r"\bTBD\b", r"\bTODO\b", r"\bFIXME\b", r"\bPLACEHOLDER\b",
                    r"XXXX", r"lorem", r"\bundefined\b", r"\?\?")]

FROZEN_MAIN = [
    "900", "801", "99", "456", "0.00462", "100%", "200/200", "16.36",
    "0.100", "0.078", "0.129", "36,846", "58.8%", "0.167",
    "23.30", "43/456", "0.943", "0.486", "0.996", "0.0012", "0.00262",
    "0.002619", "15,561", "68.2", "0.5468", "-0.38", "0.69",
    "9.06", "2.08", ".031", "1.25", "0.81", "2%", "80%", "2.63", "5.30",
    "13/50", "0.0979", "0.111", "0.0011", "0.109", "0.782", "1.21",
    "0.071", "0.022", "139,255", "0.098", "0.5441", "0.5497",
    # Typeset math forms (extracted with Unicode minus / no exponential form):
    "1.24", "10\u221260", "2.6", "10\u2212197", "0.5468",
]
FROZEN_SUPP = [
    "900", "801", "456", "10,000", "36,846", "15,561", "0.486", "0.4911",
    "0.5468", "0.5877", "0.6203", "43", "413", "20260922", "0.00262",
    "0.0026194", "0.0012286", "0.5467", "0.5468", "sift_invnodevol",
]


def extract(path):
    reader = PdfReader(path)
    return [p.extract_text() or "" for p in reader.pages]


def norm(s):
    return re.sub(r"\s+", " ", s)


def main():
    failures = []
    pages_main = extract(MAIN)
    pages_supp = extract(SUPP)
    n_main, n_supp = len(pages_main), len(pages_supp)
    print("main.pdf          : %d pages, %d KiB" % (n_main, MAIN.stat().st_size // 1024))
    print("supplementary.pdf : %d pages, %d KiB" % (n_supp, SUPP.stat().st_size // 1024))

    print("\n--- main.pdf page leads ---")
    for i, raw in enumerate(pages_main, 1):
        lead = norm(raw)[:80]
        print("  p%02d: %s" % (i, lead.encode("ascii", "replace").decode()))

    print("\n--- supplementary.pdf page leads ---")
    for i, raw in enumerate(pages_supp, 1):
        lead = norm(raw)[:80]
        print("  p%02d: %s" % (i, lead.encode("ascii", "replace").decode()))

    # placeholder scan
    for label, pages in (("main", pages_main), ("supp", pages_supp)):
        for i, raw in enumerate(pages, 1):
            t = norm(raw)
            if INSERT_RE.search(t):
                failures.append("%s p%d: imperative 'Insert'" % (label, i))
            for rx in PLACEHOLDER_RES:
                m = rx.search(t)
                if m:
                    ctx = t[max(0, m.start() - 40):m.end() + 40]
                    failures.append("%s p%d: placeholder /%s/ ...%s..." % (label, i, rx.pattern, ctx))

    # frozen numbers
    full_main = norm(" ".join(pages_main))
    full_supp = norm(" ".join(pages_supp))
    for n in FROZEN_MAIN:
        if n not in full_main:
            failures.append("main: frozen value missing: %r" % n)
    for n in FROZEN_SUPP:
        if n not in full_supp:
            failures.append("supp: frozen value missing: %r" % n)

    # every bibkey cited in main.tex
    main_src = (HERE.parent / "FINAL_MANUSCRIPT" / "main.tex").read_text(encoding="utf-8")
    bib_src = (HERE.parent / "FINAL_MANUSCRIPT" / "references.bib").read_text(encoding="utf-8")
    keys = re.findall(r"^@\w+\{([^,\s]+),", bib_src, flags=re.M)
    for k in keys:
        if not re.search(r"\\cite[tp]?\{[^}]*\b" + re.escape(k) + r"\b", main_src):
            failures.append("references: bibkey %r never cited in main.tex" % k)

    # report
    print("\n" + "=" * 66)
    if failures:
        print("PDF QC: %d ISSUE(S)" % len(failures))
        for f in failures:
            print("  - " + f.encode("ascii", "replace").decode())
        sys.exit(1)
    print("PDF QC: ALL CHECKS PASS")
    print("  placeholders       : 0")
    print("  unresolved refs    : 0 ('??' absent)")
    print("  frozen numbers     : %d main + %d supp present" % (len(FROZEN_MAIN), len(FROZEN_SUPP)))
    print("  bibkeys cited      : %d/%d" % (len(keys), len(keys)))


if __name__ == "__main__":
    main()
