# PROVENANCE — humanbrain-hidden-chokepoint-mechanics (v2.0.0)

This repository is the **standalone release vehicle** for Paper 2 of the
cross-species control-impact series, per the Paper 2 master prompt
(Step 25). It is a flattened mirror of a frozen study, not an independent
analysis history.

## Lineage

| Item | Value |
|---|---|
| Canonical parent repo | `github.com/harsha-vardhan-2006/humanbrain_cross_species_cis` |
| Parent study tree | `13_CROSS_SPECIES_CIS/02_PAPER2_HIDDEN_CHOKEPOINTS/` |
| Parent release tag | `v2.0.0` → commit `9e9cfd1` (checksum manifest) |
| Manuscript commit | `80fe5ba` (formal `RESEARCH_PAPER.md`) |
| Parent freeze commit | `5ee7ecc` (STUDY FREEZE declaration) |
| Imported parent history | full parent `main` history, preserved verbatim up to the flatten commit |

## Flatten operation (this repo's release commit)

1. Clone the parent repo at freeze commit `5ee7ecc` (no local/hardlinked objects).
2. Prune non-study top-level trees: `00_Metadata/`, `99_Logs/` (Paper-1
   acquisition phase; referenced by nothing in this study), the Paper-1
   study trees `13_CROSS_SPECIES_CIS/{00_MANIFEST…SUBMISSION_PACKAGE}`,
   and the parent root `README.md`.
3. `git mv` all contents of
   `13_CROSS_SPECIES_CIS/02_PAPER2_HIDDEN_CHOKEPOINTS/` to the repository
   root (rename-tracked; `13_MANUSCRIPT/RESEARCH_PAPER.md` byte-identical
   to parent).
4. Add this `README.md`, `PROVENANCE.md`, and a whitelist `.gitignore`
   scoped to the flattened layout; keep `LICENSE` (MIT) and
   `dist/SHA256SUMS_paper2.txt` unchanged.

No scientific file was edited: every result, script, table, figure, and
manuscript file is **byte-identical** to the parent freeze state.

## Frozen release archive

- `humanbrain_hidden_chokepoint_mechanics_v2.0.0.zip` — 119 entries,
  SHA256 `45c758b8067b46f0758a18f1e5a70b197c3e8d6ede0b26c0739ceb50ebfd1e0e`
  (manifest `dist/SHA256SUMS_paper2.txt`, built from the parent repo
  release tree). The ZIP itself is not tracked in git (regenerable,
  checksummed instead).

## Read-only upstream inputs

- **Paper 1:** `humanbrain_cross_species_cis` v1.1.0 (human CIS, 801 × 456,
  read-only).
- **Fly:** `fruitfly` v1.0.0 (FAFB v783; fly null result z = 1.21,
  p = 0.109 preserved verbatim).
- **Data:** AOMIC ID1000 derived structural connectomes
  (Zenodo 19796783, CC-BY-4.0); 4S456 parcellation.

## Tag

Tag `v2.0.0` in this repo marks the standalone release head (flatten +
docs). It is an independent tag object — the parent repo's `v2.0.0` tag
(commit `9e9cfd1`) remains untouched and canonical for the parent tree.
