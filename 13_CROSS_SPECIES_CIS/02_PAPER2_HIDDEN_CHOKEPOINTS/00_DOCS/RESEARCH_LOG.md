# RESEARCH LOG — Paper 2: Hidden Chokepoints (02_PAPER2_HIDDEN_CHOKEPOINTS)

Append-only. Style inherited from the parent study log. Superseded entries
stay with a superseded marker.

---

## P2-00 — Stages 0–5 + FREEZE 1 (2026-09-27)

```
Date:       2026-09-27
Scope:      Paper 2 master prompt, Stages 0-5, checkpoint discipline
            (session stops at Freeze 1; no Stage 6+ work started).
Stage 0:    Repository audit executed (REPOSITORY_AUDIT.md). Paths verified
            by listing, not assumed. Key finding: repo root is
            D:\humanbrain\humanbrain\; the fruitfly dataset is a SIBLING
            (D:\humanbrain\fruitfly), NOT a child - the first config run
            failed loud on this and the path was corrected. Study tree
            created with 00_DOCS..15_TESTS layout.
Stage 1:    RESEARCH_QUESTION.md frozen (H1 primary; H2-H4 secondary;
            H5 multivariate; H6/H7 exploratory-never-promoted; falsification
            rules; Outcome A/B/C rule). CONFIG_FREEZE.md frozen (cohort 801
            QC-pass x 456; thresholds; seeds 20270927; MCBH-FDR plan).
Stage 2:    MATHEMATICAL_FRAMEWORK.md frozen (exact CIS consumed read-only;
            residual R_i = CIS_i - m_s(k_i); estimator ladder; orthogonality
            gate |median rho| < 0.05; same-pairs cross-check gate rho >= 0.5;
            coupling-risk flag for path metrics).
Stage 3:    compute_residuals.py run on 801 subjects x 456 nodes:
            ORTHOGONALITY GATE PASS - median |rho(R, degree)| = 0.0327
            (mean 0.0382; p95 0.0954); linear-estimator contrast 0.396;
            Paper 1 CIS-degree rho 0.943. Outputs: continuous residuals
            (365,256 rows), subject summaries, orthogonality table, gate
            report, 3 figures.
Stage 3b:   crosscheck_same_pairs.py: SAME-PAIRS comparison vs Paper 1 E03b:
            Spearman(delta_ours, delta_paper1) = 0.785 (p = 1.7e-168,
            n = 801); median delta_ours = 0.1040 vs frozen 0.100.
            Input identity proven exactly: [R(n)-R(c)] - frozen pair
            residual = fitted(n) - fitted(c) to 8.7e-19 over all 36,846
            pair rows (both residuals act on identical inputs; only the
            baseline differs: spline fit vs matched control). 888 pairs
            with deviation > 1e-3 are predominantly nearest-50 fallback
            matches with large degree gaps - expected, documented.
Stage 4:    validate_subjects.py: replication on the proper statistic
            (delta_ours > 0): 801/801 = 100% (Paper 1: 778/801 with
            delta = 0.100); median 0.1040, subject-bootstrap 95% CI
            [0.1007, 0.1073] (10k resamples, seed 20270927); LOSO max
            deviation 5.4e-8. Retired (documented, not deleted): all-node
            median-R sign fraction (0.489) - the effect lives in the CIS
            upper tail; the matched-pair design samples it by construction.
Stage 5:    extract_extremes.py (pre-registered thresholds, BEFORE any
            identity inspection): top1 4,005 / top5 18,429 / bottom1 4,007 /
            bottom5 18,427 rows; system labels joined for QC only.
Tests:      15_TESTS/test_stage3_residuals.py: 7/7 PASS
            (py -3.13 -m pytest).
Amendments (all PRE-unblinding, append-only in CONFIG_FREEZE.md):
            (1) log10(cis+1e-6) transform RETIRED - invalid for signed CIS
                (6.1% negative rows -> NaN); caught by fail-loud execution.
                Interim asinh transform also retired (retransformation
                bias; rho = -0.063 > gate). Final primary: raw-CIS cubic
                spline df=4 (the literal E[CIS|degree]).
            (2) Cross-check redefined same-pairs: E03b per-subject deltas
                are computed on ~46 matched nodes only; the all-node-median
                vs pair-only-delta comparison was a unit mismatch producing
                a spurious blocker (rho = -0.144) - replaced by the
                same-pairs design above.
            NO gate or threshold was changed after seeing a result that
            passed it; both amendments replaced BROKEN machinery before
            any downstream statistic was consumed.
Data protection: raw datasets untouched; Paper 1 artifacts consumed
            read-only; Paper 1 outputs never modified.
Next step:  FREEZE 1 REVIEW, then Stage 6 (feature extraction) with
            coupling-risk flags; Stages 7-8 next session.
Verdict:    FREEZE 1 ACHIEVED - residualization validated and locked.
```
