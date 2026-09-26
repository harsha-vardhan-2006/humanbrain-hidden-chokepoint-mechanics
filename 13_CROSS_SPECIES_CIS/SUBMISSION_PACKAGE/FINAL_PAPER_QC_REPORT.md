# FINAL PAPER QC REPORT — HumanBrain Cross-Species CIS

Date: 2026-09-27
Scope: `13_CROSS_SPECIES_CIS/SUBMISSION_PACKAGE/` publication package
(compilation, cross-reference, placeholder, frozen-number, and page-by-page
visual QC of the final journal-style manuscript).

---

## 1. Compilation

| Item | Result |
|---|---|
| Engine | Tectonic 0.17.0 (XeTeX), full LaTeX → bibtex → LaTeX → LaTeX cycles automatic |
| `FINAL_MANUSCRIPT/main.tex` | **PASS** — no errors |
| `SUPPLEMENTARY/supplementary.tex` | **PASS** — no errors |
| Fix applied during bring-up | removed `\usepackage{amssymb}` (symbol clash with `newtxmath`) |
| Fix applied during bring-up | added `xcolor` + `url` to supplementary; long paths `\texttt` → breakable `\path` (eliminated all overfull hboxes) |
| Overfull/underfull boxes (final) | main: 0; supplementary: 0 |
| Undefined references / citations | 0 |

## 2. Cross-references and bibliography

| Check | Result |
|---|---|
| `"??"` unresolved refs in main.pdf | **0** |
| Bib keys cited vs `references.bib` | **11/11** |
| Bibliography style | `unsrt`, numbering resolves on all citations |

## 3. Placeholder scan (main + supplementary, extracted text)

Patterns: `TBD`, `TODO`, `FIXME`, `PLACEHOLDER`, `XXXX`, imperative `Insert`,
`lorem`, `undefined`, `??` → **0 findings**.

## 4. Frozen-number verification in typeset PDFs

Programmatic scan of extracted PDF text
(`SUBMISSION_PACKAGE/QC/pdf_qc.py`):

- main.pdf: **54/54** frozen values present
  (200/200, 16.36, 1.24 × 10⁻⁶⁰, 0.943, 778/801, 0.100 [0.078–0.129],
  2.6 × 10⁻¹⁹⁷, 36,846, 58.8%, 0.167, 43/456, 23.30, 0.996, 0.0012/0.00262
  (atlas_AAL116 0.002619 / full 0.0026194), E06 no-tolerance wording,
  R2b Subcortical/Cerebellar 26 / z_A 9.06 / z_B 2.08 / p = .031 / 1.25×,
  absent K=25 (z_B 0.81), 2% vs 80%, fly 2.63× / z 5.30 / 13/50,
  GABA rejection 0.109 / 0.782 / 1.21, δ 0.111 / 0.0011 raw,
  null 0.071 ± 0.022, fly δ 0.0979 not null-surviving, 139,255 neurons,
  cohort 900/801/99, k = 15,561, E₀ 0.5468 [0.5441–0.5497], 68.2, node 400 in
  top-50 in 100% of subjects, −0.38, 0.69 …)
- supplementary.pdf: **20/20** frozen values present
  (incl. E₀ 0.5467/0.5468, GE ladder 0.4911/0.5468/0.5877/0.6203,
  seeds 20260922 / 100+i, 0.0012286 primary like-for-like, 0.0026194,
  battery sizes 100 × 456, 413 censored nodes, weights `sift_invnodevol`)

Math-mode values are extracted in typeset form (e.g. `1.24 × 10⁻⁶⁰`,
Unicode minus) — verified present.

## 5. Page-by-page visual QC (all 17 pages rendered)

Rendered every page at ~144 dpi via PDFium
(`SUBMISSION_PACKAGE/QC/page_render_qc.py`); programmatic checks per page:

| Check | Result |
|---|---|
| Blank / nearly blank pages | **0** (lowest ink 0.0027 = final references page, expected) |
| Content touching page edges (clipping) | **0** |
| Suspiciously dense pages | **0** (max ink 0.0902, normal for a figure page) |
| Pages rendered | main 12/12, supplementary 5/5 |

Page-lead triage confirmed expected structure: title/abstract → workflow
figure → cohort table → CIS method figures → population results → Stouffer/
FDR → robustness table → cross-scale → negative findings → declarations →
references; supplementary S1–S5 likewise.

## 6. Frozen-science audit

- `10_REPORT/verify_final_numbers.py`: **46/46 PASS** (re-run after
  manuscript production; no scientific artifact touched).
- E06 represented as **DESCRIPTIVE-PASS** with exact values 0.002619
  (0.0026194 full precision) vs primary 0.0012286; explicitly states no
  numeric tolerance was pre-registered.
- Negative results present in main text §4.4: GABA-specific rejection,
  non-robust human system-specific interpretation, fly residual not
  null-surviving, absence of homology/causal/universal-law claims.
- Git: frozen artifacts untouched; tag `v1.1.0` not moved.

## 7. Verdict

**FINAL PAPER PACKAGE READY FOR AUTHOR REVIEW AND JOURNAL SUBMISSION**

All technical QC checks pass. No scientific value was altered; the
manuscript is a faithful typeset presentation of the frozen research.
