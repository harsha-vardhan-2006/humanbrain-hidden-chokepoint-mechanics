# Supplementary Tables — Paper 2 (Hidden Chokepoints, v2.0.1)

All tables are auto-generated from frozen artifacts by `13_MANUSCRIPT/make_supplementary.py`. Regenerate: `python 13_MANUSCRIPT/make_supplementary.py`.


## Table S0. Protocol amendments and their timing

```
amendment                                                                                                                                                                      problem                                discovery_point       before_unblinding                                                            effect_on_results                                      resolution
       A1                                                                                                 log10(CIS+1e-6) estimator invalid: CIS is signed, log of negative CIS -> NaN    first Stage-3 execution (QC figure failure) yes (no statistic read)       replaced primary estimator (asinh variant, later replaced again by A2)                  M1 re-specified pre-unblinding
       A2 (1) asinh retransformation biased (Jensen): rho(R,degree)=-0.063 failing gate; (2) cross-check compared all-node median vs pair-only delta (unit mismatch, spurious blocker)                      pre-unblinding gate check yes (no statistic read) final M1 = raw-CIS spline df=4; cross-check redefined as same-pairs Spearman retired transform estimators (preserved in git)
       A3                                                                      redundancy feature computed with boolean adjacency (OR-semantics): redundancy == clustering on all rows pre-analysis integrity sweep of Stage-6 matrix yes (Stages 7+ not run)               int32 cast; caches regenerated; only redundancy column changes              unit assertion added to Stage-6 QC
   FREEZE                                                                                                                                                             study completion                                     2026-09-30                     n/a                                                study tree declared read-only        declaration appended to CONFIG_FREEZE.md
```


## Table S1. Feature definitions (Stage 6)

```
        feature                                                                                                        definition                  family
         degree                                                              binary adjacency row sum (k = number of connections)            connectivity
       strength                                                               weighted adjacency row sum (SIFT streamline counts)            connectivity
    betweenness                                                          Brandes exact betweenness centrality on the binary graph path (coupling-flagged)
    closeness_d                                                           directed-transposed closeness proxy on the binary graph path (coupling-flagged)
     redundancy local alternative-path redundancy: common-neighbor product C = Ai[nb,:].Ai[:,nb] - 1 (int32 cast per Amendment 3)                    path
         bridge                                   bridge score: degree-1 neighbors fraction (edges to non-reciprocated neighbors)                position
  participation                                            participation coefficient across atlas systems (Guimera & Amaral 2005)                position
within_module_z                                                                                      within-system degree z-score                position
          kcore                                                                                       k-core index (Seidman 1983)                    core
    eigenvector                                                           eigenvector centrality (Bonacich 1972), power iteration              centrality
       pagerank                                                                                           PageRank (damping 0.85)              centrality
     clustering                                                                    clustering coefficient (Watts & Strogatz 1998)                    path
```


## Table S2. All 12 univariate associations (Stage 8)

```
        feature  median_rho  iqr_rho  t_vs_zero  p_wilcoxon   q_bh  frac_same_sign
         degree     -0.0255   0.0534   -17.4191      0.0000 0.0000          0.7278
       strength     -0.0689   0.0722   -36.6786      0.0000 0.0000          0.9026
    betweenness      0.1333   0.0759    63.9681      0.0000 0.0000          0.9838
    closeness_d      0.2489   0.0770   121.8865      0.0000 0.0000          1.0000
     redundancy     -0.2179   0.0835   -93.4142      0.0000 0.0000          1.0000
         bridge      0.4985   0.1007   156.3091      0.0000 0.0000          1.0000
  participation     -0.1676   0.1310   -51.5129      0.0000 0.0000          0.9763
within_module_z     -0.0186   0.0647   -11.4461      0.0000 0.0000          0.6454
          kcore      0.0556   0.1352    14.7985      0.0000 0.0000          0.7104
    eigenvector      0.0834   0.0745    41.0599      0.0000 0.0000          0.9313
       pagerank     -0.0379   0.0555   -26.3785      0.0000 0.0000          0.8152
     clustering     -0.1658   0.0888   -69.9105      0.0000 0.0000          0.9925
```


## Table S3. Feature median within-subject |Spearman| matrix (Stage 7; prune rule |rho| >= 0.9)

```
                 degree  strength  betweenness  closeness_d  redundancy  bridge  participation  within_module_z  kcore  eigenvector  pagerank  clustering
degree            1.000     0.538        0.948        0.942      -0.609   0.083          0.570            0.954  0.796        0.949     0.997      -0.881
strength          0.538     1.000        0.519        0.479      -0.387  -0.150          0.252            0.544  0.409        0.471     0.548      -0.435
betweenness       0.948     0.519        1.000        0.946      -0.716   0.255          0.501            0.910  0.713        0.879     0.954      -0.956
closeness_d       0.942     0.479        0.946        1.000      -0.627   0.269          0.492            0.893  0.761        0.942     0.934      -0.898
redundancy       -0.609    -0.387       -0.716       -0.627       1.000  -0.335         -0.277           -0.603 -0.395       -0.547    -0.618       0.694
bridge            0.083    -0.150        0.255        0.269      -0.335   1.000          0.023            0.037 -0.027        0.163     0.074      -0.424
participation     0.570     0.252        0.501        0.492      -0.277   0.023          1.000            0.543  0.454        0.558     0.565      -0.463
within_module_z   0.954     0.544        0.910        0.893      -0.603   0.037          0.543            1.000  0.750        0.890     0.955      -0.836
kcore             0.796     0.409        0.713        0.761      -0.395  -0.027          0.454            0.750  1.000        0.832     0.773      -0.652
eigenvector       0.949     0.471        0.879        0.942      -0.547   0.163          0.558            0.890  0.832        1.000     0.928      -0.818
pagerank          0.997     0.548        0.954        0.934      -0.618   0.074          0.565            0.955  0.773        0.928     1.000      -0.887
clustering       -0.881    -0.435       -0.956       -0.898       0.694  -0.424         -0.463           -0.836 -0.652       -0.818    -0.887       1.000
```


## Table S4. Nested models (Stage 9)

```
                       model  n_predictors  median_within_subject_R2  iqr_within_subject_R2  cv_R2_grouped_by_subject  delta_cvR2_vs_M1
                     M0_null             0                    0.0000                 0.0000                   -0.0000           -0.0000
                   M1_degree             1                    0.0002                 0.0008                   -0.0000            0.0000
          M2_degree_strength             2                    0.0098                 0.0187                    0.0103            0.0103
     M3_strength_plus_degree             2                    0.0098                 0.0187                    0.0103            0.0103
  M3_betweenness_plus_degree             2                    0.0683                 0.0680                    0.0706            0.0706
  M3_closeness_d_plus_degree             2                    0.4082                 0.1605                    0.3523            0.3523
   M3_redundancy_plus_degree             2                    0.2917                 0.1401                    0.0187            0.0187
       M3_bridge_plus_degree             2                    0.1651                 0.0863                    0.1465            0.1465
M3_participation_plus_degree             2                    0.0077                 0.0166                    0.0055            0.0055
          M3_wmz_plus_degree             2                    0.0059                 0.0124                    0.0049            0.0049
        M3_kcore_plus_degree             2                    0.0026                 0.0050                    0.0013            0.0013
  M3_eigenvector_plus_degree             2                    0.0542                 0.0905                    0.0304            0.0304
     M3_pagerank_plus_degree             2                    0.0124                 0.0366                    0.0012            0.0012
   M3_clustering_plus_degree             2                    0.0842                 0.0727                    0.0749            0.0749
          M4_degree_plus_set             7                    0.5120                 0.1279                    0.2942            0.2942
```


## Table S5. Within-subject standardized regression, CR1 SEs (Stage 11)

```
        feature  beta_standardized  cluster_robust_se        t      p  n_subjects  n_rows  coupling_risk   q_bh
    betweenness            -0.0000             0.0000  -5.5578 0.0000         801  365256           True 0.0000
    closeness_d             0.0001             0.0000  47.2718 0.0000         801  365256           True 0.0000
     redundancy            -0.0000             0.0000 -14.0372 0.0000         801  365256           True 0.0000
         bridge             0.0001             0.0000 109.2366 0.0000         801  365256          False 0.0000
  participation            -0.0000             0.0000 -35.1002 0.0000         801  365256          False 0.0000
within_module_z            -0.0000             0.0000 -26.4393 0.0000         801  365256          False 0.0000
          kcore             0.0001             0.0000  48.6183 0.0000         801  365256          False 0.0000
     clustering             0.0001             0.0000  56.2659 0.0000         801  365256          False 0.0000
```


## Table S6. Degree-preserving null arbitration, all features (Stage 15; 12 subjects x 100 nulls, seed 20270927)

```
        feature  median_rho_null  iqr_rho_null  abs_p95_null  median_rho_observed  obs_exceeds_p95
    betweenness           0.1675        0.0342        0.2102               0.1333            False
         bridge          -0.5957        0.0502        0.6538               0.4985            False
     redundancy          -0.6228        0.0469        0.6807              -0.2179            False
  participation           0.3909        0.0695        0.4609              -0.1676            False
within_module_z           0.0942        0.0448        0.1499              -0.0186            False
          kcore           0.0627        0.0323        0.1003               0.0556            False
     clustering           0.6846        0.0443        0.7314              -0.1658            False
    eigenvector           0.0926        0.0317        0.1304               0.0834            False
       pagerank           0.0618        0.0304        0.0961              -0.0379            False
```

Verdict: Outcome C - no observed association exceeds its null p95 (deep-verified from raw records by gate V09).


## Table S6b. Null-residualization proxy vs spline on observed data (12 null subjects)

```
        feature  median_rho_spline  median_rho_20bin  median_abs_delta  p95_abs_delta
    betweenness             0.1028            0.1425            0.0504         0.1333
         bridge             0.4661            0.5206            0.0436         0.1258
     clustering            -0.1469           -0.1686            0.0479         0.1319
    eigenvector             0.1078            0.1331            0.0480         0.1341
          kcore             0.0361            0.0750            0.0647         0.1354
       pagerank            -0.0460           -0.0074            0.0466         0.1450
  participation            -0.1173           -0.0697            0.0639         0.1041
     redundancy            -0.1826           -0.2011            0.0467         0.1158
within_module_z            -0.0211            0.0114            0.0482         0.1417
```

Association-level median |delta rho| = 0.0502 (null bands: 0.10-0.73). Point-level residuals differ in the tails (median Spearman(R_spline, R_20bin) = 0.865); both are degree-orthogonal. The stored per-null R_null re-derives bit-exactly (gate V09).


## Table S7. Robustness matrix (Stage 20: R1 estimator ladder, R2 extremes, R5 winsorization)

```
       analysis parameter         feature                                   statistic   value
   R1_estimator M2_linear     betweenness                   median within-subject rho -0.2430
   R1_estimator M2_linear     closeness_d                   median within-subject rho -0.1388
   R1_estimator M2_linear      redundancy                   median within-subject rho  0.0308
   R1_estimator M2_linear          bridge                   median within-subject rho  0.4351
   R1_estimator M2_linear   participation                   median within-subject rho -0.3455
   R1_estimator M2_linear within_module_z                   median within-subject rho -0.3766
   R1_estimator M2_linear           kcore                   median within-subject rho -0.2511
   R1_estimator M2_linear      clustering                   median within-subject rho  0.1838
   R1_estimator     P_df3     betweenness                   median within-subject rho  0.1056
   R1_estimator     P_df3     closeness_d                   median within-subject rho  0.2205
   R1_estimator     P_df3      redundancy                   median within-subject rho -0.2000
   R1_estimator     P_df3          bridge                   median within-subject rho  0.4964
   R1_estimator     P_df3   participation                   median within-subject rho -0.1801
   R1_estimator     P_df3 within_module_z                   median within-subject rho -0.0534
   R1_estimator     P_df3           kcore                   median within-subject rho  0.0353
   R1_estimator     P_df3      clustering                   median within-subject rho -0.1417
   R1_estimator   Q_bin20     betweenness                   median within-subject rho  0.1552
   R1_estimator   Q_bin20     closeness_d                   median within-subject rho  0.2692
   R1_estimator   Q_bin20      redundancy                   median within-subject rho -0.2504
   R1_estimator   Q_bin20          bridge                   median within-subject rho  0.5237
   R1_estimator   Q_bin20   participation                   median within-subject rho -0.1157
   R1_estimator   Q_bin20 within_module_z                   median within-subject rho  0.0042
   R1_estimator   Q_bin20           kcore                   median within-subject rho  0.0449
   R1_estimator   Q_bin20      clustering                   median within-subject rho -0.1897
   R2_threshold      top1            (ZR) median standardized residual in extreme set  3.7016
   R2_threshold      top5            (ZR) median standardized residual in extreme set  1.6842
R5_winsorized_R     0.999     betweenness                   median within-subject rho  0.1333
R5_winsorized_R     0.999     closeness_d                   median within-subject rho  0.2489
R5_winsorized_R     0.999      redundancy                   median within-subject rho -0.2179
R5_winsorized_R     0.999          bridge                   median within-subject rho  0.4985
R5_winsorized_R     0.999   participation                   median within-subject rho -0.1676
R5_winsorized_R     0.999 within_module_z                   median within-subject rho -0.0186
R5_winsorized_R     0.999           kcore                   median within-subject rho  0.0556
R5_winsorized_R     0.999      clustering                   median within-subject rho -0.1658
```


## Table S8. Biological enrichment (10,000 permutations, two-sided, BH-q)

```
           set       category_col                   category  n_top  observed  expected  delta_pp  p_perm   q_bh
     top10_CIS    major_structure                  Brainstem      0    0.0000    0.0263   -2.6300  0.3895 0.3895
     top10_CIS    major_structure                     CORTEX     20    0.4444    0.8772  -43.2700  0.0001 0.0002
     top10_CIS    major_structure                 Cerebellum      3    0.0667    0.0219    4.4700  0.0700 0.0875
     top10_CIS    major_structure                  Subcortex     10    0.2222    0.0439   17.8400  0.0001 0.0002
     top10_CIS    major_structure                   Thalamus     12    0.2667    0.0307   23.6000  0.0001 0.0002
     top10_CIS         hemisphere          BILATERAL_MIDLINE      3    0.0667    0.0219    4.4700  0.0694 0.2082
     top10_CIS         hemisphere                          L     21    0.4667    0.4890   -2.2400  0.7551 0.7579
     top10_CIS         hemisphere                          R     21    0.4667    0.4890   -2.2400  0.7579 0.7579
     top10_CIS functional_network                 cerebellar      3    0.0667    0.0219    4.4700  0.0665 0.1431
     top10_CIS functional_network               default mode      4    0.0889    0.1996  -11.0700  0.0795 0.1431
     top10_CIS functional_network           dorsal attention      3    0.0667    0.1009   -3.4200  0.4633 0.4633
     top10_CIS functional_network     frontoparietal control      3    0.0667    0.1140   -4.7400  0.3402 0.3990
     top10_CIS functional_network                     limbic      1    0.0222    0.0570   -3.4800  0.3547 0.3990
     top10_CIS functional_network                somatomotor      1    0.0222    0.1689  -14.6600  0.0050 0.0225
     top10_CIS functional_network                subcortical     22    0.4889    0.1009   38.8000  0.0001 0.0009
     top10_CIS functional_network ventral attention/salience      7    0.1556    0.1031    5.2500  0.2956 0.3990
     top10_CIS functional_network                     visual      1    0.0222    0.1338  -11.1500  0.0194 0.0582
     top10_CIS    cortical_status                 CEREBELLUM      3    0.0667    0.0219    4.4700  0.0663 0.0663
     top10_CIS    cortical_status                   CORTICAL     20    0.4444    0.8772  -43.2700  0.0001 0.0001
     top10_CIS    cortical_status                SUBCORTICAL     22    0.4889    0.1009   38.8000  0.0001 0.0001
top10_residual    major_structure                  Brainstem      9    0.2000    0.0263   17.3700  0.0001 0.0002
top10_residual    major_structure                     CORTEX     21    0.4667    0.8772  -41.0500  0.0001 0.0002
top10_residual    major_structure                 Cerebellum      8    0.1778    0.0219   15.5800  0.0001 0.0002
top10_residual    major_structure                  Subcortex      7    0.1556    0.0439   11.1700  0.0022 0.0027
top10_residual    major_structure                   Thalamus      0    0.0000    0.0307   -3.0700  0.3763 0.3763
top10_residual         hemisphere          BILATERAL_MIDLINE      8    0.1778    0.0219   15.5800  0.0001 0.0003
top10_residual         hemisphere                          L     19    0.4222    0.4890   -6.6800  0.3507 0.3507
top10_residual         hemisphere                          R     18    0.4000    0.4890   -8.9000  0.2118 0.3177
top10_residual functional_network                 cerebellar      8    0.1778    0.0219   15.5800  0.0001 0.0004
top10_residual functional_network               default mode      5    0.1111    0.1996   -8.8500  0.1681 0.2161
top10_residual functional_network           dorsal attention      2    0.0444    0.1009   -5.6400  0.2076 0.2335
top10_residual functional_network     frontoparietal control      0    0.0000    0.1140  -11.4000  0.0101 0.0182
top10_residual functional_network                     limbic      8    0.1778    0.0570   12.0800  0.0018 0.0054
top10_residual functional_network                somatomotor      3    0.0667    0.1689  -10.2200  0.0607 0.0910
top10_residual functional_network                subcortical     16    0.3556    0.1009   25.4700  0.0001 0.0004
top10_residual functional_network ventral attention/salience      3    0.0667    0.1031   -3.6400  0.4565 0.4565
top10_residual functional_network                     visual      0    0.0000    0.1338  -13.3800  0.0048 0.0108
top10_residual    cortical_status                 CEREBELLUM      8    0.1778    0.0219   15.5800  0.0001 0.0001
top10_residual    cortical_status                   CORTICAL     21    0.4667    0.8772  -41.0500  0.0001 0.0001
top10_residual    cortical_status                SUBCORTICAL     16    0.3556    0.1009   25.4700  0.0001 0.0001
```


## Table S9. Chokepoint candidates at k = 5% (Stage 22; per-node null NOT_ESTABLISHED by design)

```
 node_id         parcel_name major_structure functional_network   degree    CIS  residual  bridge  participation  clustering  in_cis_top5  in_residual_top5  bridge_upper_half null_arbitration_node_level                                        spatial_control
     286 RH_DorsAttn_Post_17          CORTEX   dorsal attention 124.0000 0.0011    0.0002  0.7462         0.8375      0.3438         True              True               True             NOT_ESTABLISHED NOT_ESTABLISHED (no MNI centroids in frozen manifests)
     442      LH_Hippocampus       Subcortex        subcortical 160.0000 0.0017    0.0002  0.7455         0.8347      0.3106         True              True               True             NOT_ESTABLISHED NOT_ESTABLISHED (no MNI centroids in frozen manifests)
     451  Cerebellar_Region6      Cerebellum         cerebellar 142.0000 0.0017    0.0005  0.7663         0.7990      0.3036         True              True               True             NOT_ESTABLISHED NOT_ESTABLISHED (no MNI centroids in frozen manifests)
```


## Table S9b. Chokepoint threshold sensitivity

```
 top_frac  k  n_cis_top  n_res_top  n_both  n_candidates_with_position  candidate_share_pct
   0.0100  5          5          5       1                           1               0.2193
   0.0200  9          9          9       2                           2               0.4386
   0.0500 23         23         23       3                           3               0.6579
   0.1000 46         46         46       7                           7               1.5351
```


## Table S10. Human vs fly comparison (Stage 22b; fly negative preserved verbatim)

```
                                                property                                                                                                                                             human                                                                         fly                                                                                                                   interpretation
                                        Unit of analysis                                                                                   456-node atlas PARCEL (4S456; macroscopic region, NOT a neuron)                  individual NEURON (FAFB v783, 139k neurons; targets 3,518)                              Cross-scale comparison is architectural only; scales differ by ~5 orders of magnitude in unit size.
                                   CIS-degree dependence                                                                                                 median rho(CIS, degree) = 0.943 (Paper 1, frozen)          strong (fly Paper 1: CIS dominated by degree; visual fraction 80%)                                  Both scales: raw CIS is degree-confounded; explicit control is mandatory before interpretation.
    Degree-independent residual (matched/control design)                                                                                          delta = 0.104; 801/801 subjects > 0; CI [0.1007, 0.1073]                     delta = 0.100; 778/801 sign-positive (fly Paper 1 E03b)                                                          A small positive degree-independent CIS residual exists at BOTH scales.
       Residual reproducibility (this paper, same pairs)                                                                                              rho(delta_ours, delta_paper1) = 0.785; median 0.1040                     not re-run (frozen v1.0.0 artifacts consumed read-only)                                                             Human side re-derived independently; fly side preserved as released.
Degree-preserving null VERDICT on the residual mechanism                                             Stage 15: feature-R associations DO NOT exceed degree-preserving null p95 (Outcome C, all 9 features)                  z = 1.21, p = 0.109 - DID NOT survive (fly v1.0.0, frozen) At NEITHER scale does the residual mechanism survive a degree-preserving null. Same-direction negatives; no universal-law claim.
       Network-position signature of high-residual nodes                                                            bridge rho = +0.4985; closeness_d +0.2489; redundancy -0.2179 (within-subject medians) ME.131 case: betweenness z = +4.08 vs degree-matched peers; case study ONLY                  Human: population-level associations (null-qualified). Fly: single pre-registered case; NOT a population claim.
                 Predictive learnability of the residual                                                                                  ridge cv-R2 = 0.574 (permuted-R control 0.0024; degree-only ~ 0)                    NOT_ESTABLISHED (no equivalent benchmark in fly release)                                        Learnable structure beyond degree exists in human; fly equivalent absent - do not equate.
                    Anatomical concentration of extremes top-10% CIS UNDER-represents cortex (share 0.44 vs expected 0.88, q<0.001); enrichment NOT_ESTABLISHED for cell type (parcels are not cell types)                 ME.131 = optic lobe (visual); fly visual contribution ~ 80%                                                Human extremes avoid cortex; fly concentrated in visual system. Anatomies differ.
                       Visual-system contribution to CIS                                                                                                                       ~2% (human, frozen Paper 1)                                                  ~80% (fly, frozen Paper 1)                             Architecture does NOT transfer at the anatomical level ('architecture replicates, anatomy doesn't').
                 Cell-type / neurotransmitter annotation                                                                               NOT_AVAILABLE (macroscopic parcels carry no cell-type ground truth)               available per neuron (FAFB annotations: nt_type, super_class)                                    Resolution asymmetry is structural; human cell-type claims are NOT_ESTABLISHED in this study.
                              Robustness of associations                                                             estimator ladder + winsorization: sign-consistent for bridge/participation (Stage 20)                                 fly study internal robustness only (v1.0.0)                                    Human feature associations are estimator-robust in sign; magnitudes differ across estimators.
                                   Causal interpretation                                                                                              NONE licensed (observational structural connectomes)                                    NONE licensed (observational connectome)                                Both studies are observational; removal-CIS is a network quantity, not a perturbation experiment.
```
