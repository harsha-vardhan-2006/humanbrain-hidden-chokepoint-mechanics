# Human vs fly - conservative comparison (Paper 2 Stage 22b)

Sources: human numbers re-derived in this study from frozen artifacts;
fly numbers from the frozen `fruitfly` v1.0.0 release (read-only).

### Unit of analysis

- **Human:** 456-node atlas PARCEL (4S456; macroscopic region, NOT a neuron)
- **Fly:** individual NEURON (FAFB v783, 139k neurons; targets 3,518)
- **Interpretation:** Cross-scale comparison is architectural only; scales differ by ~5 orders of magnitude in unit size.

### CIS-degree dependence

- **Human:** median rho(CIS, degree) = 0.943 (Paper 1, frozen)
- **Fly:** strong (fly Paper 1: CIS dominated by degree; visual fraction 80%)
- **Interpretation:** Both scales: raw CIS is degree-confounded; explicit control is mandatory before interpretation.

### Degree-independent residual (matched/control design)

- **Human:** delta = 0.104; 801/801 subjects > 0; CI [0.1007, 0.1073]
- **Fly:** delta = 0.100; 778/801 sign-positive (fly Paper 1 E03b)
- **Interpretation:** A small positive degree-independent CIS residual exists at BOTH scales.

### Residual reproducibility (this paper, same pairs)

- **Human:** rho(delta_ours, delta_paper1) = 0.785; median 0.1040
- **Fly:** not re-run (frozen v1.0.0 artifacts consumed read-only)
- **Interpretation:** Human side re-derived independently; fly side preserved as released.

### Degree-preserving null VERDICT on the residual mechanism

- **Human:** Stage 15: feature-R associations DO NOT exceed degree-preserving null p95 (Outcome C, all 9 features)
- **Fly:** z = 1.21, p = 0.109 - DID NOT survive (fly v1.0.0, frozen)
- **Interpretation:** At NEITHER scale does the residual mechanism survive a degree-preserving null. Same-direction negatives; no universal-law claim.

### Network-position signature of high-residual nodes

- **Human:** bridge rho = +0.4985; closeness_d +0.2489; redundancy -0.2179 (within-subject medians)
- **Fly:** ME.131 case: betweenness z = +4.08 vs degree-matched peers; case study ONLY
- **Interpretation:** Human: population-level associations (null-qualified). Fly: single pre-registered case; NOT a population claim.

### Predictive learnability of the residual

- **Human:** ridge cv-R2 = 0.574 (permuted-R control 0.0024; degree-only ~ 0)
- **Fly:** NOT_ESTABLISHED (no equivalent benchmark in fly release)
- **Interpretation:** Learnable structure beyond degree exists in human; fly equivalent absent - do not equate.

### Anatomical concentration of extremes

- **Human:** top-10% CIS UNDER-represents cortex (share 0.44 vs expected 0.88, q<0.001); enrichment NOT_ESTABLISHED for cell type (parcels are not cell types)
- **Fly:** ME.131 = optic lobe (visual); fly visual contribution ~ 80%
- **Interpretation:** Human extremes avoid cortex; fly concentrated in visual system. Anatomies differ.

### Visual-system contribution to CIS

- **Human:** ~2% (human, frozen Paper 1)
- **Fly:** ~80% (fly, frozen Paper 1)
- **Interpretation:** Architecture does NOT transfer at the anatomical level ('architecture replicates, anatomy doesn't').

### Cell-type / neurotransmitter annotation

- **Human:** NOT_AVAILABLE (macroscopic parcels carry no cell-type ground truth)
- **Fly:** available per neuron (FAFB annotations: nt_type, super_class)
- **Interpretation:** Resolution asymmetry is structural; human cell-type claims are NOT_ESTABLISHED in this study.

### Robustness of associations

- **Human:** estimator ladder + winsorization: sign-consistent for bridge/participation (Stage 20)
- **Fly:** fly study internal robustness only (v1.0.0)
- **Interpretation:** Human feature associations are estimator-robust in sign; magnitudes differ across estimators.

### Causal interpretation

- **Human:** NONE licensed (observational structural connectomes)
- **Fly:** NONE licensed (observational connectome)
- **Interpretation:** Both studies are observational; removal-CIS is a network quantity, not a perturbation experiment.


## Mandatory framing

- The fly residual's failure to survive its degree-preserving null
  (z = 1.21, p = 0.109) is preserved verbatim; it is a first-class
  negative result.
- The human Stage-15 null arbitration reached the same direction
  (Outcome C for all 9 features). Two same-direction negatives at
  different scales DO NOT license 'universal law' or 'same mechanism'
  claims - they show only that, at both scales, degree alone explains
  the null-level structure of the CIS-residual association machinery.
- Shared: degree dominance; small positive degree-independent residual;
  null-negative arbitration. Species/network-specific: anatomical
  concentration, visual contribution, unit of analysis, availability
  of cell-type ground truth, predictive benchmark.
