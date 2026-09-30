# RESOURCE INVENTORY — Paper 2 / Human Brain (measured 2026-09-29)

Classification: DATASET / ANNOTATION / ATLAS / CONNECTIVITY / CODE /
RESULT / DOCUMENT / CACHE. Sizes measured with `du`; not copied.

| Path (relative to repo root `D:\humanbrain\humanbrain`) | Class | Size | Contents | Source / Status |
|---|---|---|---|---|
| `12_HumanConnectome_AOMIC/zenodo_19796783_raw/` | DATASET (raw zips) | ~17 GB (incl. sibling fly 17G listed separately below) | `connectomes_part_1..10.zip` (900-subject AOMIC-ID1000 derivative, .mat per subject) | Zenodo 19796783, CC-BY-4.0; VERIFIED present; do not duplicate |
| `13_CROSS_SPECIES_CIS/02_PREPROCESSING/cache_parts/` | CACHE (pipeline input) | **4.0 GB** | 20 npz parts + per-part keys; 25,200 matrices (900 × 7 atlases × 4 variants) | E01 v2 cache; PROBED OK (subject 100 primary 456×456 loads) |
| `13_CROSS_SPECIES_CIS/02_PREPROCESSING/cache_keys.csv` | MANIFEST | 25,201 rows | (subject, atlas, variant) → part/member | frozen E01; PASS |
| `13_CROSS_SPECIES_CIS/00_MANIFEST/manifests/atlas_4S456_system_labels.csv` | ATLAS / ANNOTATION | 456 rows | node → parcel label + 7-network system (Vis/SomMot/DorsAttn/VentAttn/Limbic/FP/Default/Subcortical_Cerebellar) | extracted from Yeo-7-prefixed parcel names (provenance txt); DIRECT |
| `13_CROSS_SPECIES_CIS/03_BASELINE/qc_primary.csv` | RESULT (frozen flags) | 900 rows | subject → qc_pass (801 primary cohort) | Paper 1 frozen; flag-never-delete |
| `13_CROSS_SPECIES_CIS/04_CIS/` | RESULT (frozen) | 66 MB | per-subject CIS (456 nodes × 801), E03/E03b summaries | Paper 1 frozen; read-only |
| `02_PAPER2.../03_FEATURE_EXTRACTION/NODE_FEATURE_MATRIX.parquet` | RESULT (P2 Stage 6) | ~65 MB (dir incl. caches) | 365,256 rows × 12 features + degree/CIS | regenerated post-AMENDMENT-3; CURRENT |
| `02_PAPER2.../04_DEGREE_CONTROL/` | RESULT (P2 Stage 3-5) | ~40 MB | continuous_residuals, extremes, gates, crosschecks | Freeze-1 outputs; CURRENT |
| `D:\humanbrain\fruitfly\` | DATASET + RESULT (sibling, frozen) | 17 GB (incl. 12.9 GB SWC zip) | FAFB v783 raw + frozen v1.0.0 study | read-only reference; never modified |

Rules honored: no dataset duplication; the 4 GB cache is the single
pipeline input; raw zips retained as provenance; fly tree untouched.
