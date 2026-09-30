# Release v2.0.1 — external-audit response (2026-09-30)

Paper 2: *Degree-Independent Control Impact in the Human Structural
Connectome: Graph-Geometric Associations and Degree-Preserving Null
Arbitration.*

This release responds to a full external research-submission audit. The
scientific results are **unchanged** — every frozen number is identical.
What changed is the strength of the evidence layer and the completeness of
the publication package.

## Scientific verdict (unchanged)

A degree-independent CIS residual replicates across all 801 QC-pass
subjects (δ = 0.104, CI [0.1007, 0.1073]) and is predictable from measured
network features (ridge cv-R² = 0.574; degree-only ≈ 0), but **none** of
the observed feature–residual associations survives exact degree-preserving
null arbitration (pre-registered **Outcome C**). The "hidden chokepoint"
is an operational construct, not a validated node class.

## Phase 1 — auditability repairs

1. **`13_MANUSCRIPT/verify_stage24.py` rewritten as a genuine independent
   verifier** (was: several existence-only gates):
   - V06: M1/M4 subject-grouped CV **recomputed from the merged
     residual+feature matrix**, incl. the a-priori M4 selection rule;
     must match frozen table to 1e-6 (actual: exact to 6 decimals).
   - V07: degree-only/ridge cv-R² **recomputed** (3 seeds × 5 folds,
     train-fold scaling, λ=1 closed-form ridge) + permuted-R control
     (matches to <1e-6).
   - V09 **deep verification over all 1,200 raw null records**: 12
     subjects × 100 unique seeds; per-null **exact degree preservation**
     vs the observed degree sequence (max deviation 0.0); stored
     R_null **re-derived bit-exactly** from (cis_null, degree) via the
     documented 20-bin proxy; pooled null median/IQR/p95 reproduced to
     1e-9; observed 801-subject statistics reproduced; **Outcome C
     reproduced from raw data**.
   - V10/V11: sign-consistency and NC1/NC2 band-exceedance now checked
     numerically per feature.
   - Result: **12/12 PASS**, exit 0.
2. **Null-estimator equivalence validation** (new
   `06_NULL_MODELS/validate_null_proxy.py` →
   `NULL_PROXY_VALIDATION.json`): on observed data, the arbitrated
   statistic ρ(R, feature) differs between the 20-bin null proxy and the
   frozen spline by a median of 0.050 (null bands 0.10–0.73); the proxy
   yields *stronger* observed associations, so it cannot manufacture
   Outcome C.
3. **`MATHEMATICAL_FRAMEWORK.md`** stale sentence removed (+1e-6 log
   offset no longer exists anywhere); historical note added (Amendments
   1–2); null-proxy role documented.
4. **Correction found by the new V11:** the earlier "margins ≥ 0.13 for
   all features" claim was wrong — within-module z (0.014) and k-core
   (0.052) have small margins. Manuscript §4.4 corrected; all 8 features
   still exceed both bands.

## Phase 2 — publication package

- Manuscript **retitled** (no "determinants"); "universal" → "replicated
  across all 801"; "learnable" → "predictable from measured network
  features"; spatial caveat moved **next to the enrichment result**.
- New **§3.9 Null ensemble calibration and Monte Carlo precision**.
- **25-reference bibliography** (network control, connectomics, AOMIC,
  FAFB/FlyWire, SIFT2, graph-metric primary sources) with matching inline
  citations.
- **Author metadata block** (affiliation, corresponding author, funding,
  competing interests, ethics, contributions; ORCID flagged for the
  author).
- **`SUBMISSION/`**: `PAPER2_MAIN.tex` + `PAPER2_MAIN.pdf`,
  `SUPPLEMENTARY.tex` + `SUPPLEMENTARY.pdf` (Tectonic-compiled).
- **`SUPPLEMENTARY_TABLES.md`** (S0–S10) auto-generated from artifacts by
  `make_supplementary.py` — no hand-typed numbers.
- **`CITATION.cff`** added.

## Phase 3 — reproducibility

- `requirements.txt` (exact versions) + `run_all.py` cross-platform
  runner (`python run_all.py --verify --qc --proxy`).
- Raw 1,200-null ensemble (117 MB, gitignored) **checksummed for archival**:
  SHA256 `e01852cdf4a2f00f63531dc108b35c3a5b005714713cc443a1760d07ecde7864`
  — ships in the release archive; recommended for Zenodo deposit.
- Zenodo/DOI deposit: recommended follow-up (button requires a GitHub
  account connection; not executable from the CLI session).

## Verification status at this tag

`python run_all.py --verify` → **12/12 PASS** (deep V09).
