# FEATURE QC REPORT (Stage 7)

Rows: 365,256 (801 subjects x 456 nodes).

- Missing values: **0**; infinite values: **0** (must be 0; fail loud otherwise).
| feature | min | p50 | p99 | max | subject-SD (median) |
|---|---|---|---|---|---|
| degree | 1 | 63 | 187 | 309 | 32.37 |
| strength | 14.99 | 1.259e+04 | 8.363e+04 | 2.858e+05 | 1.474e+04 |
| betweenness | 0 | 0.0008181 | 0.0264 | 0.1026 | 0.005214 |
| closeness_d | 0.3034 | 0.5452 | 0.7052 | 0.8414 | 0.05191 |
| redundancy | 0 | 1 | 1 | 1 | 0.006207 |
| bridge | 0.4305 | 0.6804 | 0.8726 | 1 | 0.05806 |
| participation | 0 | 0.7846 | 0.861 | 0.8727 | 0.08374 |
| within_module_z | -2.817 | -0.1388 | 2.798 | 5.088 | 0.9923 |
| kcore | 1 | 41 | 44 | 47 | 5.429 |
| eigenvector | 5.242e-06 | 0.001991 | 0.006045 | 0.009041 | 0.001123 |
| pagerank | 0.0003543 | 0.002042 | 0.005432 | 0.008903 | 0.0008791 |
| clustering | 0 | 0.5568 | 0.9004 | 1 | 0.135 |

## Redundancy groups (median within-subject |rho| >= 0.9)
- betweenness ~ closeness_d
- betweenness ~ clustering
- betweenness ~ degree
- betweenness ~ pagerank
- betweenness ~ within_module_z
- closeness_d ~ degree
- closeness_d ~ eigenvector
- closeness_d ~ pagerank
- degree ~ eigenvector
- degree ~ pagerank
- degree ~ within_module_z
- eigenvector ~ pagerank
- pagerank ~ within_module_z

## Modeling rule
Highly redundant features are never placed in the same regression
without pre-registered justification; the Stage 9 feature set is
selected for low redundancy and each feature's coupling risk is
carried into interpretation.
