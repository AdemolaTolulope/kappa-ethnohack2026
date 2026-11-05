# Research reconnaissance and defensible gap

**Reconnaissance date:** 2026-11-05. **Scope:** focused desk review of major public resources and published platform/database papers, plus feasibility test against ChEMBL REST.

## What already exists (so KAPPA does not claim to invent it)

- **LOTUS** is a large, referenced open natural-products knowledge base linking structures to organisms and source literature. It already supports organism–compound occurrence exploration and open data releases. [Rutz et al., eLife 2022, DOI 10.7554/eLife.70780](https://doi.org/10.7554/eLife.70780); [LOTUS data](https://doi.org/10.5281/zenodo.5794107).
- **IMPPAT** curates Indian medicinal plants, phytochemicals, therapeutic-use and formulation associations. Its 2018 paper describes 1,742 plants and 9,596 phytochemicals in the then-reported release. Access/reuse for individual downloadable files and site content must be checked at point of acquisition; do not assume the site is an unrestricted API. [Mohanraj et al., Scientific Reports 2018, DOI 10.1038/s41598-018-22631-z](https://doi.org/10.1038/s41598-018-22631-z); [current portal](https://cb.imsc.res.in/imppat/).
- **ChEMBL** is a curated bioactivity resource with REST APIs, target/assay/document provenance and extensive activity data. KAPPA uses its actual human PTGS2 IC50 measurements rather than asserting a new bioactivity corpus. [Zdrazil et al., NAR 2024, DOI 10.1093/nar/gkad1004](https://doi.org/10.1093/nar/gkad1004).
- **PubChem** exposes compound records, standard identifiers and APIs. [Kim et al., PubChem 2025 update, NAR 2025, DOI 10.1093/nar/gkae1059](https://doi.org/10.1093/nar/gkae1059).
- **OREGANO** demonstrates a broad drug/natural compound knowledge-graph approach for computational repurposing. **NP-KG** describes natural product–drug interaction knowledge graph construction from biomedical ontologies and literature. Graph integration itself is not a KAPPA novelty claim. [Taneja et al., arXiv:2209.11950](https://arxiv.org/abs/2209.11950).
- **Open Targets** already integrates target–disease evidence for therapeutic hypothesis building; the **GWAS Catalog** provides curated GWAS associations and ancestry/study metadata. KAPPA does not replace either and currently does not import variant-level associations. [Ochoa et al., NAR 2025, DOI 10.1093/nar/gkae1128](https://doi.org/10.1093/nar/gkae1128); [Cerezo et al., NAR 2025, DOI 10.1093/nar/gkae1070](https://doi.org/10.1093/nar/gkae1070).
- Molecular ML is well established; MoleculeNet recommends scaffold splits for appropriate molecular generalization assessments and highlights benchmark sensitivity to dataset/split choices. [Wu et al., Chemical Science 2018, DOI 10.1039/C7SC02664A](https://doi.org/10.1039/C7SC02664A).

## Defensible project gap (bounded, not absolute)

The gap is **not** “there is no database / no knowledge graph / no AI for plants.” Existing resources cover these areas. For a hackathon-scale scientific demonstrator, the unmet practical need is a transparent, executable path from a traceable natural-product occurrence/identity through a *specific measured target assay dataset* to a leakage-conscious molecular model, a declared applicability-domain check and an evidence-tiered user-facing interpretation. The prototype demonstrates this narrow integration with a known plant natural product and human PTGS2 assay data while expressly separating occurrence evidence from therapeutic, genetic and clinical claims.

This is an **integration and reproducibility contribution**, not a claim of first-in-field scientific method. Phase 11 adds one attributed secondary ethnobotanical literature report and an independent verified CPIC CYP2C19–clopidogrel guideline demonstration. These are not generalized ethnobotanical coverage, population genomics, pathway enrichment, target–disease genetics, docking, or a validated KAPPA PGx prediction. The ClinVar record is an identity cross-reference only; no patient genotype or curcumin/PTGS2 pharmacogenomic relationship is asserted.

## Pilot choice and feasibility

Pilot context: *Curcuma longa*–curcumin as an illustrative plant/compound identity and occurrence anchor; human PTGS2 (COX-2; ChEMBL CHEMBL230) as a well-annotated biochemical target with assay records. ChEMBL API returned 7,482 human target IC50 records at retrieval. After predeclared exact-assay, data-quality, grey-zone and structure deduplication, 3,164 unique canonical structures remained, with both activity bands represented. This was checked by actually fetching and processing the API response on 2026-11-05.

Why this is feasible: stable public target and compound IDs; measured records with literature/assay IDs; suitable data volume for a modest, transparent baseline model. Why it is limited: this is a single-target biochemical benchmark and does not establish that the plant, extract, or curcumin treats disease. Curcumin appears in the assay corpus; prediction on it is therefore flagged as a known-training-compound retrospective score, not a prospective natural-product discovery result.

## Landscape refresh (2026-11-05)

A fuller comparison, with per-resource purpose, evidence carried, limits and whether KAPPA duplicates it, is in
[`competitive_landscape.md`](competitive_landscape.md). Additions since the initial reconnaissance:

- **NPASS 2023** holds 43,285 natural products with measured activity values against ~7,700 targets and
  explicitly distinguishes measured activity from similarity-estimated profiles (Zhao et al., NAR 2023,
  DOI 10.1093/nar/gkac1069). KAPPA's activity layer is a deliberately narrow ChEMBL slice, not a competitor.
- **IMPPAT 2.0** reports 4,010 Indian medicinal plants, 17,967 phytochemicals, 189,386 plant–part–phytochemical
  and 89,733 plant–part–therapeutic-use associations, with predicted (not measured) targets/ADMET
  (Vivek-Ananth et al., ACS Omega 2023, DOI 10.1021/acsomega.3c00156).
- **NP-KG v3.0.0** is released as a multi-GB knowledge graph for natural-product–drug interactions
  (Taneja et al., Zenodo 2024, DOI 10.5281/zenodo.12536780).
- **A 2026 compound-centric framework** links LOTUS occurrence, taxonomy reconciliation, Murcko scaffolds and
  "conservative ChEMBL-linked bioactivity evidence" for plant chemical space. This is the closest published
  work in spirit, so KAPPA must **not** claim novelty for combining plant occurrence, scaffolds and ChEMBL
  evidence; its claim is limited to the enforced evidence-type contract and refusal rule.
