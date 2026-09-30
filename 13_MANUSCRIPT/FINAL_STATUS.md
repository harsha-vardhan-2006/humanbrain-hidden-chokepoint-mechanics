# FINAL STATUS — Paper 2: Hidden Chokepoints (v1.0.0, 2026-09-30)

| Component             | Status    | Evidence |
| --------------------- | --------- | -------- |
| Data audit            | PASS      | AUDIT/PROJECT_BASELINE.md; cache probe (20 parts, 25,200 keys) |
| Dataset verification  | PASS      | Paper 1 acquisition QC inherited; read-only consumption |
| Atlas mapping         | PASS      | data/node_atlas_mapping.csv (456/456, HIGH confidence) |
| Biological annotation | PASS      | results_annotation/human_node_biological_annotations.csv (456 rows; cell-type fields NOT_AVAILABLE by discipline) |
| CIS reproduction      | PASS      | V02 same-pairs rho = 0.785; V03 801/801 delta > 0 (Stage 4) |
| Null models           | PASS      | Stage 15: 1200/1200 degree-preserving nulls; Outcome C (all features inside null bands) |
| Mechanistic analysis  | PASS      | Stages 8-11: bridge rho = +0.4985; ridge cv-R2 = 0.574 vs degree-only ~ 0; CR1 q < 1e-7 (8 features) |
| Negative controls     | PASS      | Stage 21: NC1/NC2 bands <= 0.0044; observed margins >= 0.129 |
| Spatial controls      | NOT_ESTABLISHED | No MNI centroids in frozen manifests (documented; no invented coordinates) |
| Robustness            | PASS      | Stage 20 R1/R2/R5 sign-consistency; winsorization-invariant |
| Human/fly comparison  | PASS      | 12-property table; fly z = 1.21, p = 0.109 negative preserved verbatim |
| Chokepoint definition | PASS      | Operational, multi-criterion; 1/2/3/7 candidates at k = 1/2/5/10%; node-level null NOT_ESTABLISHED |
| Figures               | PASS      | 10 PNGs incl. 7 Stage-9 panels; every figure scripted |
| Manuscript            | PASS      | MANUSCRIPT.md + SUPPLEMENTARY + FIGURE_LEGENDS + REPRODUCIBILITY |
| Verification gates    | PASS      | V01-V12: 12/12 (13_MANUSCRIPT/verify_stage24.py, exit 0) |
| Full QC               | PASS      | QC/run_full_qc.py: 25 PASS / 0 FAIL / 1 WARNING |
| Secret scan           | PASS      | QC scan clean; no .env; no token patterns in tree || Git package             | PASS      | Tag v2.0.0 (commit 9e9cfd1) pushed to origin; dist/humanbrain_hidden_chokepoint_mechanics_v2.0.0.zip + SHA256SUMS_paper2.txt committed |

TOTAL PASS: 17   TOTAL FAIL: 0   TOTAL WARNING: 0   NOT_ESTABLISHED: 1 (spatial)   PENDING: 0

Percentages are NOT manufactured; counts are literal.

Verdict: **RELEASED** (v2.0.0, 2026-09-30). Scientific headline is bounded:
residual real + learnable; mechanism null-qualified (Outcome C);
chokepoint = operational label only.
