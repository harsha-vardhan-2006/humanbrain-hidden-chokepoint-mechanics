"""Build the node → atlas/biological annotation tables (Paper 2 / human).

Evidence discipline (master rules):
  - Node = ATLAS PARCEL (macroscopic). NEVER an individual neuron.
  - Everything derives from the frozen label file
    (00_MANIFEST/manifests/atlas_4S456_system_labels.csv + PROVENANCE:
    labels extracted 2026-09-23 from connectomes_part_1.zip field
    atlas_4S456Parcels_region_labels; cortical labels carry Yeo-7
    network prefixes; subcortical/cerebellar use abbreviation labels).
  - Cell-class / neurotransmitter / transcriptomic fields: a macroscopic
    parcel is NOT a cell type; no parcel-level ground truth exists in
    this dataset -> NOT_AVAILABLE (never guessed).
  - MNI coordinates: not present in the frozen cache/manifests ->
    NOT_AVAILABLE (no invented centroids).

Outputs:
  data/node_atlas_mapping.csv            (per master-prompt schema)
  results_annotation/human_node_biological_annotations.csv (evidence-leveled)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

TREE = Path(__file__).resolve().parents[1]
STUDY = TREE.parent
LAB = STUDY / "00_MANIFEST" / "manifests" / "atlas_4S456_system_labels.csv"
OUT_MAP = TREE / "data"
OUT_ANN = TREE / "results_annotation"
OUT_MAP.mkdir(exist_ok=True)
OUT_ANN.mkdir(exist_ok=True)

# Yeo-7 network -> canonical functional network name (source: Yeo 2011
# 7-network parcellation scheme, as embedded in the parcel labels; the
# labels themselves are the direct evidence).
NETWORK_CANON = {
    "Vis": "visual",
    "SomMot": "somatomotor",
    "DorsAttn": "dorsal attention",
    "SalVentAttn": "ventral attention/salience",
    "Limbic": "limbic",
    "Cont": "frontoparietal control",
    "Default": "default mode",
}

# Subcortical abbreviation -> (major_structure, substructure). Only
# expansions that are standard anatomical abbreviations are mapped;
# anything ambiguous stays UNKNOWN. Evidence level: MAPPED_HIGH (standard
# nomenclature) or UNKNOWN - never a guess about histology.
SUBCORTICAL_MAP = {
    "Pu": ("Subcortex", "Putamen"),
    "Ca": ("Subcortex", "Caudate"),
    "NAC": ("Subcortex", "Nucleus Accumbens"),
    "EXA": ("Subcortex", "Extended Amygdala"),
    "GPe": ("Subcortex", "Globus Pallidus external"),
    "GPi": ("Subcortex", "Globus Pallidus internal"),
    "SNc_PBP_VTA": ("Brainstem", "Substantia Nigra / VTA complex"),
    "RN": ("Brainstem", "Red Nucleus"),
    "SNr": ("Brainstem", "Substantia Nigra pars reticulata"),
    "VeP": ("Brainstem", "Ventral Tegmental area (label as provided)"),
    "HN": ("Brainstem", "Habenula (label as provided)"),
    "HTH": ("Subcortex", "Hypothalamus"),
    "MN": ("Brainstem", "Mammillary Nuclei (label as provided)"),
    "STH": ("Subcortex", "Subthalamus"),
    "Pulvinar": ("Thalamus", "Pulvinar"),
    "Anterior": ("Thalamus", "Anterior nuclei"),
    "Medio_Dorsal": ("Thalamus", "Mediodorsal nuclei"),
    "Ventral_Latero_Dorsal": ("Thalamus", "Ventrolateral-dorsal nuclei"),
    "Central_Lateral-Lateral_Posterior-Medial_Pulvinar": (
        "Thalamus", "Central lateral / lateral posterior / medial pulvinar"),
    "Ventral_Anterior": ("Thalamus", "Ventral anterior nuclei"),
    "Ventral_Latero_Ventral": ("Thalamus", "Ventrocaudal nuclei (label as provided)"),
    "Hippocampus": ("Subcortex", "Hippocampus"),
    "Amygdala": ("Subcortex", "Amygdala"),
    "Cerebellar_Region": ("Cerebellum", "Cerebellar region (numbered)"),
}


def parse_label(label: str) -> dict:
    """Split one parcel label into hemisphere + bare name."""
    if label.startswith("LH_") or label.startswith("LH-"):
        return {"hemisphere": "L", "bare": label[3:]}
    if label.startswith("RH_") or label.startswith("RH-"):
        return {"hemisphere": "R", "bare": label[3:]}
    return {"hemisphere": "BILATERAL_MIDLINE", "bare": label}


def main() -> None:
    lab = pd.read_csv(LAB)
    assert len(lab) == 456, f"expected 456 nodes, got {len(lab)}"

    rows_map, rows_ann = [], []
    for r in lab.itertuples(index=False):
        p = parse_label(r.label)
        bare = p["bare"]
        is_cortical_network = r.system in NETWORK_CANON

        # ---- anatomical classification
        if is_cortical_network:
            major = "CORTEX"
            sub = "cortical parcel (" + NETWORK_CANON[r.system] + " network)"
            cortical_status = "CORTICAL"
            func_net = NETWORK_CANON[r.system]
            ann_status_major = "MAPPED_HIGH_CONFIDENCE"
            func_status = "MAPPED_HIGH_CONFIDENCE"
        elif r.system == "Subcortical_Cerebellar":
            key = bare if bare in SUBCORTICAL_MAP else (
                "Cerebellar_Region" if bare.startswith("Cerebellar_Region")
                else None)
            if key:
                major, sub = SUBCORTICAL_MAP[key]
                ann_status_major = "MAPPED_HIGH_CONFIDENCE"
            else:
                major, sub = "UNKNOWN", bare
                ann_status_major = "UNKNOWN"
            cortical_status = "SUBCORTICAL" if major != "Cerebellum" else (
                "CEREBELLUM")
            func_net = "subcortical" if major != "Cerebellum" else "cerebellar"
            func_status = "MAPPED_LOW_CONFIDENCE"  # functional net by exclusion
        else:
            major, sub = "UNKNOWN", bare
            cortical_status = "UNKNOWN"
            func_net = "unknown"
            ann_status_major = "UNKNOWN"
            func_status = "UNKNOWN"

        lobe = ("NOT_AVAILABLE" if not is_cortical_network
                else "NOT_AVAILABLE")  # atlas does not encode lobes
        # (kept explicit: the label source does not provide lobe assignment)

        # ---- atlas mapping table (master schema)
        rows_map.append({
            "node_id": r.node,
            "atlas": "atlas_4S456Parcels",
            "parcel_id": r.node,
            "parcel_name": r.label,
            "hemisphere": p["hemisphere"],
            "lobe": lobe,
            "major_structure": major,
            "substructure": sub,
            "x": "NOT_AVAILABLE", "y": "NOT_AVAILABLE",
            "z": "NOT_AVAILABLE",
            "coordinate_system": "NOT_AVAILABLE",
            "source": "connectomes_part_1.zip::atlas_4S456Parcels_region_labels",
            "source_version": "extracted 2026-09-23 (PROVENANCE txt)",
            "annotation_status": ann_status_major,
        })

        # ---- biological annotation table (evidence-leveled)
        rows_ann.append({
            "node_id": r.node,
            "atlas": "atlas_4S456Parcels",
            "parcel_id": r.node,
            "parcel_name": r.label,
            "hemisphere": p["hemisphere"],
            "major_structure": major,
            "substructure": sub,
            "lobe": lobe,
            "cortical_status": cortical_status,
            "cortical_layer": "NOT_AVAILABLE",
            # A PARCEL IS NOT A CELL TYPE: these stay NOT_AVAILABLE by rule.
            "cell_class": "NOT_AVAILABLE",
            "neuronal_class": "NOT_AVAILABLE",
            "excitatory_inhibitory": "NOT_AVAILABLE",
            "neurotransmitter": "NOT_AVAILABLE",
            "transcriptomic_class": "NOT_AVAILABLE",
            "marker_genes": "NOT_AVAILABLE",
            "functional_network": func_net,
            "x": "NOT_AVAILABLE", "y": "NOT_AVAILABLE", "z": "NOT_AVAILABLE",
            "annotation_source": (
                "atlas_4S456_system_labels.csv (+PROVENANCE); "
                "Yeo-7 prefixes on cortical labels"),
            "annotation_version": "P2-v1.0.0",
            "mapping_confidence": (
                "HIGH" if ann_status_major == "MAPPED_HIGH_CONFIDENCE"
                else "LOW" if func_status == "MAPPED_LOW_CONFIDENCE" else "NONE"),
            "annotation_status": ann_status_major if is_cortical_network
            else (func_status if r.system == "Subcortical_Cerebellar"
                  else "UNKNOWN"),
        })

    pd.DataFrame(rows_map).to_csv(OUT_MAP / "node_atlas_mapping.csv", index=False)
    pd.DataFrame(rows_ann).to_csv(
        OUT_ANN / "human_node_biological_annotations.csv", index=False)

    ann = pd.DataFrame(rows_ann)
    print("wrote data/node_atlas_mapping.csv (456 rows)")
    print("wrote results_annotation/human_node_biological_annotations.csv")
    print("\nmajor_structure counts:")
    print(ann["major_structure"].value_counts().to_string())
    print("\nfunctional_network counts:")
    print(ann["functional_network"].value_counts().to_string())
    print("\nannotation_status counts:")
    print(ann["annotation_status"].value_counts().to_string())
    print("\ncell_class unique:", ann["cell_class"].unique().tolist())


if __name__ == "__main__":
    main()
