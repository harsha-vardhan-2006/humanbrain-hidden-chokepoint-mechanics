# Biological annotation sources (Paper 2 / human)

Evidence discipline: every field in
`results_annotation/human_node_biological_annotations.csv` is traceable to a
source below. Anything not derivable is `NOT_AVAILABLE`; anything not
testable in this dataset is `NOT_ESTABLISHED`. A macroscopic atlas parcel is
NEITHER an individual neuron NOR a cell type.

## S1 - Node identity / atlas labels

- **Dataset:** AOMIC ID1000 derived connectomes, Zenodo record 19796783
  (CC-BY-4.0), `atlas_4S456Parcels` parcellation.
- **Evidence used:** region-label field extracted 2026-09-23 from
  `connectomes_part_1.zip` (field `atlas_4S456Parcels_region_labels`),
  frozen at `00_MANIFEST/manifests/atlas_4S456_system_labels.csv`
  (+ PROVENANCE sidecar).
- **Mapping:** node_id -> parcel label (direct, 1:1). Cortical labels carry
  Yeo-7 network prefixes (Yeo et al. 2011, 7-network scheme as embedded in
  the labels); subcortical/cerebellar labels are standard abbreviations
  expanded only where unambiguous (e.g. `Pu` -> Putamen); ambiguous forms
  remain UNKNOWN.
- **Confidence:** HIGH for label identity (direct); MAPPED_HIGH_CONFIDENCE
  for hemisphere/lobe/system derived from the labels.
- **Limitations:** the atlas ships no parcel centroids -> MNI x/y/z are
  NOT_AVAILABLE (no invented coordinates); no layer information -> cortical
  layer NOT_AVAILABLE.

## S2 - Functional network assignment

- **Source:** Yeo-7 prefixes on cortical labels (as in S1); subcortical /
  cerebellar parcels -> `subcortical` / `cerebellar` functional tags.
- **Method:** direct prefix mapping, no re-estimation.
- **Limitations:** Yeo-7 is a cortical scheme; subcortical tags are
  structural, not functional-parcellation assignments.

## S3 - Cell class / neuronal class / neurotransmitter / transcriptomics

- **Status:** NOT_AVAILABLE for all 456 parcels.
- **Reason:** the dataset contains no single-cell or histological ground
  truth at parcel resolution; a parcel-level majority cell class cannot be
  established from connectivity. Enrichment tests against these fields are
  therefore NOT_ESTABLISHED (reported as such in
  `results_annotation/BIOLOGICAL_ENRICHMENT.json`).
- **Species discipline:** no mouse/macaque cell-type transfer was applied.
  External atlases (Allen HBA, HPA) were NOT integrated because no
  parcel-level mapping without invented coordinates could be defended.

## S4 - Cell-type annotation on the fly side (comparison only)

- **Source:** frozen `fruitfly` v1.0.0 release tables (`e07_annotated`:
  `nt_type`, `super_class` per neuron).
- **Use:** fly-side descriptive annotation ONLY; never mapped onto human
  parcels; never presented as human cell-type evidence.

