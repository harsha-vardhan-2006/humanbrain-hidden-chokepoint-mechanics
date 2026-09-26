# SUBMISSION PACKAGE — README (index and build instructions)

Assembled 2026-09-26; human-author fields completed and PDF/DOCX rendered
the same day. All statements reference frozen artifacts; nothing is
fabricated. **Status: placeholders resolved (CRediT confirmed, COI, ethics,
affiliation); rendering DONE; package is submission-ready pending the
author's final read-through and the human release/signing decision.**

## FINAL RESEARCH PAPER (typeset, 2026-09-27)

The package now contains the **final journal-style research paper**, fully
typeset from LaTeX and QC-checked — this is the citable artifact to submit:

| Artifact | Path |
|---|---|
| Paper (PDF, 12 pp) | [`FINAL_MANUSCRIPT/main.pdf`](FINAL_MANUSCRIPT/main.pdf) |
| Paper (LaTeX source) | `FINAL_MANUSCRIPT/main.tex` + `references.bib` + `tables/` + `figures/` |
| Supplementary (PDF, 5 pp) | [`SUPPLEMENTARY/supplementary.pdf`](SUPPLEMENTARY/supplementary.pdf) (+ `supplementary.tex`) |
| Table generator (fail-loud) | [`TABLE_SOURCES/generate_tables.py`](TABLE_SOURCES/generate_tables.py) |
| New figure source | [`FIGURE_SOURCES/make_fig_cis_method.py`](FIGURE_SOURCES/make_fig_cis_method.py) |
| QC report | [`FINAL_PAPER_QC_REPORT.md`](FINAL_PAPER_QC_REPORT.md) |
| QC scripts | `QC/pdf_qc.py`, `QC/page_render_qc.py` |

**Rebuild the paper** (Tectonic 0.17+, any OS; resolves packages and runs
BibTeX automatically):
```bash
cd FINAL_MANUSCRIPT && tectonic main.tex
cd ../SUPPLEMENTARY && tectonic supplementary.tex
```
Regenerate tables (requires the frozen CSV/RESOLUTION artifacts; exits
non-zero on any mismatch): `python TABLE_SOURCES/generate_tables.py`
from `13_CROSS_SPECIES_CIS/`. Regenerate the schematic figure:
`python FIGURE_SOURCES/make_fig_cis_method.py`.
QC re-run: `python QC/pdf_qc.py` and `python QC/page_render_qc.py`
(needs `pypdf`, `pypdfium2`).

The paper is a faithful typeset presentation of the frozen results: no
number, hypothesis, threshold, seed, or interpretation was altered;
negative results are reported as first-class outcomes; E06 is described as
a DESCRIPTIVE-PASS with no pre-registered tolerance. The Markdown renders
in `rendered/` below remain as provenance snapshots of the pre-typeset
draft.

## Contents
| File | Purpose | Status |
|---|---|---|
| `cover_letter.md` | venue-agnostic factual cover letter | READY (author review) |
| `highlights.md` | 6 highlight bullets | READY |
| `graphical_abstract_description.md` | designer brief for the graphical abstract | READY |
| `author_contributions.md` | CRediT statement | **COMPLETED (author-confirmed 2026-09-26)** |
| `data_availability.md` | data provenance + licenses | READY |
| `code_availability.md` | code paths + environment + MIT license | READY (license added 2026-09-26) |
| `reproducibility_statement.md` | audit summary + disclosed gaps | READY |
| `conflict_of_interest.md` | COI declaration | **COMPLETED (no competing interests)** |
| `ethics_statement_if_applicable.md` | secondary-data use note | **COMPLETED (secondary use of public data; no IRB required — author determination)** |
| `novelty_statement.md` | bounded novelty claim | READY (Kudriavtsev full-text gate CLOSED 2026-09-26) |
| `JOURNAL_OPTIONS.md` | venue scope/policy table (no ranking) | READY (verify APCs at submission) |
| `manuscript.md` | final manuscript (author block + references added 2026-09-26) | READY |
| `rendered/` | PDF/DOCX/HTML renderings + print stylesheet | **RENDERED 2026-09-26** |

## Renderings (2026-09-26)
`rendered/manuscript.pdf` (5 pp), `rendered/manuscript.docx`,
`rendered/supplementary_material.pdf|.docx` (3 pp),
`rendered/figure_captions.pdf` (2 pp; captions for all 6 main + 3
supplementary figures, resolving the items FIGURE_PROVENANCE deferred to
typesetting). The typeset PDF/DOCX are rendered from the manuscript body
(## Title onward); the full provenance header remains in `manuscript.md`
and `10_REPORT/MANUSCRIPT_FINAL.md`. Toolchain: pandoc 3.11 → HTML (print
stylesheet `rendered/style_header.html`) → headless Chrome print-to-PDF;
DOCX direct via pandoc. Visual/content inspection passed: zero
[PLACEHOLDER]/TBD tokens; title page, CRediT/COI/ethics, references (11
entries), Unicode notation, and page flow verified programmatically from
the PDF text layer.

## Building from source (reproducible rendering)
```bash
pandoc manuscript.md -f markdown -t html5 -s -c rendered/style_header.html \
  --metadata pagetitle="Manuscript" -o rendered/manuscript.html
# PDF via headless Chrome (or: pandoc --pdf-engine=xelatex on TeX machines)
chrome --headless --print-to-pdf=rendered/manuscript.pdf \
  --no-pdf-header-footer rendered/manuscript.html
pandoc manuscript.md -f markdown -t docx -o rendered/manuscript.docx
```
Supplementary renders the same way from `10_REPORT/SUPPLEMENTARY_MATERIAL.md`.
Figures: `../08_FIGURES/*.png|pdf` (provenance:
`../10_REPORT/FIGURE_PROVENANCE.md`; captions: `../08_FIGURES/FIGURE_CAPTIONS.md`).
Figure 5 (`fig05_fdr_anatomical.*`) was rendered 2026-09-26 from frozen
artifacts by `../08_FIGURES/make_fig05_anatomical.py`; no statistics were
recomputed.

## Pre-submission checklist (human)
1. ~~Kudriavtsev 2026 full-text read; co-sign the gate record.~~ CLOSED
   2026-09-26 (full text verified via proxy; optional co-signature only).
2. ~~Fill [PLACEHOLDER]s: contributions, COI, ethics/IRB note, affiliation.~~
   DONE 2026-09-26 (author-confirmed).
3. ~~Render PDF/DOCX; attach figures per FIGURE_PROVENANCE.~~ DONE
   2026-09-26 (+ captions PDF).
4. Verify current APC/policies of the chosen venue (JOURNAL_OPTIONS notes).
5. Post bioRxiv preprint (optional).
6. ~~Add a code license.~~ DONE 2026-09-26 (MIT, `LICENSE` at repo root).
7. Correspondence email/ORCID: withheld from this public repo by author
   decision; enter in the journal submission system.
