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

---

## P2-01 � Stages 6�24 completion (2026-09-30)

```
Date:       2026-09-30
Scope:      downstream chain completion (Stages 6-24) + synthesis + docs.
Stage 6:    feature matrix 801x456 x 12 features (Amendment-3 redundancy
            repair verified in-chain: max|diff| vs clustering > 0).
Stages 7-9: feature QC, univariate (12 features, all q < 1e-27; bridge
            strongest rho = +0.4985), nested models (M4 cvR2 = 0.294 vs
            M1 ~ 0; closeness_d/redundancy/bridge best M3 adds).
Stage 10:   ML benchmark - ridge cvR2 = 0.5740 vs degree_only ~ 0;
            permuted-R control 0.0024. MLP arm unstable (cvR2 -4.09 +- 4.57,
            documented benchmark artifact; numpy-native SGD, not a
            mechanism claim). FIX during run: mlp_fit backward pass
            err @ W2 -> np.outer(err, W2) (shape bug; pre-result, no
            numbers consumed before the fix).
Stage 11:   subject-aware within-subject model, CR1 SEs: all 8 features
            q < 1e-7 (bridge t = 109.2; clustering t = 56.3).
Stage 15:   degree-preserving nulls COMPLETE 1200/1200 (12 subjects x 100,
            seed 20270927, exact degree verification per null, full CIS +
            9-feature recomputation per null). VERDICT: Outcome C - all 9
            observed |median rho| INSIDE null p95 bands
            (bridge obs +0.4985 vs null p95 0.6538; clustering obs
            -0.1658 vs null p95 0.7314; etc.). Null machinery is WIDE:
            degree-preserving rewiring alone generates rho magnitudes
            comparable to the observed ones.
Stage 20:   robustness matrix (R1/R2/R5) - sign-consistent bridge/
            participation; winsorization-invariant headline associations.
Stage 21:   negative controls NC1/NC2 - observed exceeds bands, margins
            >= 0.13 for all features.
Stage 12-13: fly case study - ME.131 vs 86 degree-matched peers:
            CIS z = +23.4 (154x peer median), directed betweenness
            (sampled k=512, frozen seed) z = +4.08; case-study bounds
            preserved. FIX during run: to_markdown -> to_string
            (missing optional dep 'tabulate'; formatting only).
Stage 22:   chokepoint operationalization + sensitivity (1/2/3/7 joint-
            criterion candidates at 1/2/5/10%) + human-vs-fly comparison
            table (12 properties; fly z=1.21 p=0.109 negative preserved).
Stage 24:   independent verification V01-V12: 12/12 PASS.
Spatial:    Moran's I / distance nulls NOT_ESTABLISHED (no parcel
            centroids in frozen manifests) - recorded, not approximated.
Data protection: Paper 1 + fly artifacts read-only; frozen outputs
            untouched; nulls checkpointed JSONL (resume-safe).
Next step:  figures + manuscript package + QC + release (P2-02).
Verdict:    residual real and learnable; mechanism claim NULL-QUALIFIED
            (Outcome C); chokepoint = operational label only.
```

---

## P2-02 — 2026-09-30 — Formal research paper + v2.0.0 release

```
Entry:      P2-02
Date:       2026-09-30
Scope:      Paper 2 master prompt Stage 25 (final report) + formal paper

Release:    tag v2.0.0 on parent repo (commit 9e9cfd1); ZIP
            dist/humanbrain_hidden_chokepoint_mechanics_v2.0.0.zip
            (SHA256 45c758b8...bfd1e0e, manifest dist/SHA256SUMS_paper2.txt).
            Frozen Paper 1 + fly lineage (v1.1.0) untouched.
QC:         run_full_qc.py 25 PASS / 0 FAIL / 1 WARNING (git-cleanliness
            check, resolved at release); V01-V12 12/12 PASS.
Paper:      13_MANUSCRIPT/RESEARCH_PAPER.md — formal manuscript compiled
            FROM FROZEN ARTIFACTS ONLY; no numbers re-derived, no claims
            extended. Tables: ML benchmark, null arbitration (Outcome C,
            9 features), enrichment (major structure), chokepoint
            sensitivity, human-vs-fly comparison. Fly negative
            (z=1.21, p=0.109) preserved verbatim.
Framing:    residual real + learnable (ridge cv-R2 = 0.574); mechanism
            NULL-QUALIFIED (Outcome C); chokepoint = operational label
            only; spatial NOT_ESTABLISHED; no causal claims.
Fixes:      FINAL_STATUS.md Git-package row PENDING -> PASS (release
            completed this session); release vehicle deviation
            (parent-repo tag instead of standalone repo) documented
            in paper section 8.
Verdict:    paper complete; study v2.0.0 released.
```

---

## P2-03 — 2026-09-30 — STUDY FREEZE + standalone release repo

```
Entry:      P2-03
Date:       2026-09-30
Scope:      Freeze of the completed Paper 2 study; standalone mirror repo

FREEZE:     Study tree declared FROZEN (read-only) at v2.0.0 lineage
            (9e9cfd1 + manuscript commit 80fe5ba). Declaration appended
            to 01_CONFIG/CONFIG_FREEZE.md (append-only, below Amendment 3).
            No result, figure, table, or manuscript number modified.
Release:    Standalone mirror repo
            github.com/harsha-vardhan-2006/humanbrain-hidden-chokepoint-mechanics
            created per master prompt; parent study tree flattened to repo
            root; parent history imported for lineage; tag v2.0.0 re-created
            on the standalone release head; PROVENANCE.md records parent
            SHAs + ZIP SHA256 (45c758b8...bfd1e0e).
Verdict:    Paper 2 analysis CLOSED; further work = new labeled studies only.
```
