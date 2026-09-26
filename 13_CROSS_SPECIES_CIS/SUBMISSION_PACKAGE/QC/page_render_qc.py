"""Page-by-page visual QC: renders every PDF page to PNG and runs
programmatic layout checks (blank pages, content clipped at page edges,
suspiciously dense/sparse pages). Renders are written to a temp directory
and removed afterwards; re-run to regenerate.
"""
import sys
import tempfile
from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image

HERE = Path(__file__).resolve().parent
PDFS = [
    ("main", HERE.parent / "FINAL_MANUSCRIPT" / "main.pdf"),
    ("supp", HERE.parent / "SUPPLEMENTARY" / "supplementary.pdf"),
]

SCALE = 2.0  # ~144 dpi
FAILS = []


def analyze(label, page_no, img, first, last):
    """Programmatic checks on one rendered page."""
    g = img.convert("L")
    w, h = g.size
    px = g.load()

    def region_ink(x0, y0, x1, y1):
        dark = 0
        total = 0
        for y in range(y0, y1):
            for x in range(x0, x1):
                total += 1
                if px[x, y] < 128:
                    dark += 1
        return dark / total if total else 0.0

    # edges: 8px band inside each border (at rendered scale)
    b = 8
    edges = {
        "top": region_ink(0, 0, w, b),
        "bottom": region_ink(0, h - b, w, h),
        "left": region_ink(0, 0, b, h),
        "right": region_ink(w - b, 0, w, h),
    }
    for side, ink in edges.items():
        if ink > 0.02:
            FAILS.append("%s p%d: content touching %s edge (ink %.3f)"
                         % (label, page_no, side, ink))

    # global ink coverage sanity
    small = g.resize((min(w, 400), min(h, 566)))
    sp = small.load()
    sw, sh = small.size
    dark = sum(1 for y in range(sh) for x in range(sw) if sp[x, y] < 128)
    ink = dark / (sw * sh)
    if ink < 0.002:
        FAILS.append("%s p%d: page nearly blank (ink %.4f)" % (label, page_no, ink))
    if ink > 0.55:
        FAILS.append("%s p%d: suspiciously dense (ink %.4f)" % (label, page_no, ink))
    return ink


def main():
    outdir = Path(tempfile.mkdtemp(prefix="hbqc_render_"))
    for label, path in PDFS:
        doc = pdfium.PdfDocument(str(path))
        n = len(doc)
        print("%s: %d pages -> %s%s_*.png" % (label, n, outdir, label))
        for i in range(n):
            page = doc[i]
            bmp = page.render(scale=SCALE)
            img = bmp.to_pil()
            png = outdir / ("%s_%02d.png" % (label, i + 1))
            img.save(png)
            ink = analyze(label, i + 1, img, i == 0, i == n - 1)
            print("  p%02d: %dx%d  ink=%.4f  %s" % (i + 1, img.width, img.height,
                                                    ink, png.name))
        doc.close()
    print("=" * 66)
    if FAILS:
        print("VISUAL QC: %d ISSUE(S)" % len(FAILS))
        for f in FAILS:
            print("  - " + f)
        print("(renders kept in %s)" % outdir)
        sys.exit(1)
    print("VISUAL QC: ALL PAGES PASS "
          "(no blank pages, no edge-clipping, no density anomalies)")
    print("(renders in %s)" % outdir)


if __name__ == "__main__":
    main()
