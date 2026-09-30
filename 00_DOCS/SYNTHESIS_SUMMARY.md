# Synthesis summary - Paper 2 (Hidden Chokepoints)

## Master verdict (numbers on disk; framing bounded accordingly)

1. **Residual exists and is degree-independent.** delta = 0.104
   (801/801 subjects > 0; bootstrap CI [0.1007, 0.1073]); orthogonality
   gate median |rho(R, degree)| = 0.0327. Freeze-1 + V01-V12 all PASS.
2. **Network position predicts the residual out-of-sample.** Ridge on 11
   features: cv-R2 = 0.574 (subject-grouped CV, 3 seeds) vs degree-only
   ~ 0; within-subject permutation control 0.0024. Strongest univariate
   associates (within-subject median rho): bridge +0.4985, closeness_d
   +0.2489, redundancy -0.2179, participation -0.1676, clustering -0.1658.
3. **The mechanism does NOT survive its degree-preserving null.**
   Stage 15 (12 x 100 nulls, exact degree preservation, full CIS +
   feature recomputation per null): every feature's observed |median rho|
   lies inside the null p95 band (Outcome C). The Stage-8/11 associations
   characterize real-graph structure; they are not licensed as
   degree-independent mechanisms.
4. **Chokepoint label is operational only.** Joint-criterion candidates
   (CIS top-k AND residual top-k AND upper-half bridge): 1 node at k = 1%,
   3 at 5%, 7 at 10%. Per-node null arbitration: NOT_ESTABLISHED.
5. **Biology.** Top-CIS nodes significantly UNDER-represent cortex
   (top-10% share 0.44 vs expected 0.88; permutation q < 0.001). All
   cell-type fields NOT_AVAILABLE (parcels are not cell types); cell-type
   enrichment NOT_ESTABLISHED.
6. **Fly comparison.** Fly null verdict preserved (z = 1.21, p = 0.109,
   negative). Human Stage-15 is a same-direction negative at a different
   scale. Shared: degree dominance + small positive residual. Not shared:
   anatomy (visual 2% vs 80%), unit scale, cell-type ground truth.
   No universal-law or same-mechanism claim.

## Spatial control status

MNI centroids are absent from the frozen manifests; the atlas label file
ships names only. Therefore Moran's I / distance-constrained nulls are
**NOT_ESTABLISHED** for this dataset version - recorded rather than
approximated. Risk acknowledged: system-label associations could partially
reflect spatial autocorrelation; the residual itself is defined on graph
structure and the degree-preserving null (which randomizes topology while
preserving degrees, i.e. scrambles spatial clustering) bounds rather than
removes this concern. Any spatial claim requires parcel centroids in a
future protocol.

## What this paper does NOT claim

- No causal claim (observational connectomes; no perturbation).
- No universal mechanism claim (two same-direction null negatives).
- No cell-type claim at parcel resolution.
- No per-node chokepoint claim beyond the operational, null-qualified
  candidate list.

