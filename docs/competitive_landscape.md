# Competitive landscape and KAPPA's bounded contribution

Prepared 2026-11-05. Every external claim below is attributed to the cited publication or documentation.
KAPPA's own numbers come from this repository and are reproducible with `python -m src.run_pipeline`,
`python -m src.ml.duplicate_sensitivity` and `pytest -q`.

## 1. What the literature says the problem is

The natural-products field is not short of data. It is short of *connected, attributable* data, and the
connection step is where unsupported inference usually enters.

- LOTUS was built precisely because structures and organisms lived in separate resources with "scarce
  interlinkages", and because references were reported without standards, which "breaks the crucial
  evidentiary link required for tracing information back to the original data" [@rutz2022lotus].
- NPASS curates quantitative activity values and species sources, and explicitly separates
  experimentally measured activity from similarity-estimated profiles for compounds that have no
  measurement [@zhao2023npass].
- IMPPAT 2.0 curates plant–part–phytochemical and plant–part–therapeutic-use associations and adds
  predicted targets/ADMET, which are model outputs rather than measurements [@vivekananth2023imppat2].
- NP-KG assembles ontologies plus literature-mined relations for pharmacokinetic natural-product–drug
  interactions and reports that relation-extraction error and conflicting assertions remain part of the
  artefact [@taneja2022npkg; @taneja2024npkgv3].
- A 2026 compound-centric framework takes LOTUS occurrence data, reconciles taxonomy, dereplicates by
  InChIKey, computes Murcko scaffolds and links "conservative ChEMBL-linked bioactivity evidence", and
  states that occurrence-oriented resources need downstream work to handle "bias, redundancy, and
  evidential heterogeneity" [@compoundcentric2026].

So the research problem KAPPA addresses is real and documented: evidence exists, but the hand-offs
between botanical, chemical, assay and genomic layers each introduce ambiguity, and the literature
itself identifies this as unresolved work.

## 2. What existing resources do, and what they do not do

| Resource | Primary purpose | Evidence it carries | Limits relevant to KAPPA | Does KAPPA duplicate it? |
|---|---|---|---|---|
| **LOTUS** | Referenced structure–organism occurrence pairs, disseminated via Wikidata [@rutz2022lotus] | Occurrence with literature references; hundreds of thousands of pairs | Occurrence only; no activity, no assay-level labels, no model, no PGx; coverage is literature-limited by construction | No — KAPPA uses one attributed occurrence triple explicitly as occurrence, not as use or activity |
| **IMPPAT 2.0** | Phytochemistry of 4,010 Indian medicinal plants: 17,967 phytochemicals, 189,386 plant–part–phytochemical and 89,733 plant–part–therapeutic-use associations [@vivekananth2023imppat2] | Manually curated use/occurrence associations; predicted targets and ADMET | Predicted targets/ADMET are computation, not measurement; therapeutic-use associations are not efficacy; Indian-plant scope | No — KAPPA ingests none of it; it would be a source to cite, not to re-create |
| **KNApSAcK** | Species–metabolite occurrence | Occurrence | Non-standardised organism field, awkward access (noted by LOTUS authors) [@rutz2022lotus] | No |
| **NPASS 2023** | Quantitative NP activity and species-source data: 43,285 NPs with activity values against ~7,700 targets, 958,866 activity records [@zhao2023npass] | Measured activity, plus similarity-estimated profiles for unmeasured NPs | Database-scale; activity values are heterogeneous across assays; estimation layer is similarity-based | No — KAPPA's activity layer is a small, deliberately filtered ChEMBL slice, not a replacement |
| **ChEMBL** | Curated bioactivity database with assay/document provenance [@zdrazil2024chembl] | Measured activities with assay and document identifiers | Records need assay-level filtering; duplicate structures and conflicting measurements need decisions | No — KAPPA consumes it |
| **PubChem** | Chemical identity and properties for >100 M compounds [@kim2025pubchem] | Identity, computed properties | Identity is not bioactivity, efficacy or safety | No — KAPPA uses identity lookup |
| **UniProt** | Protein sequence/function reference | Target identity | No activity or variant-response claim | No |
| **Open Targets** | Target–disease evidence integration for therapeutic hypotheses [@ochoa2025opentargets] | Genetic, expression, literature, tractability evidence for targets | Target-centric; not natural-product occurrence, not a phytochemical prioritisation tool | No overlap in the pilot; KAPPA does not claim target–disease evidence |
| **GWAS Catalog** | Curated variant–trait associations [@cerezo2025gwas] | Statistical genetic associations | Association ≠ function ≠ drug response; not consulted for curcumin/PTGS2 in this pilot | No |
| **PharmGKB / CPIC / PharmVar** | Curated PGx knowledge, allele function and prescribing guidelines | Gene–drug pairs, allele definitions, recommendations | Guidelines exist for specific gene–drug pairs (here CYP2C19–clopidogrel), not for curcumin | No — KAPPA displays a CPIC example and states that no curcumin guideline exists |
| **NP-KG** | Ontology + literature knowledge graph for pharmacokinetic natural-product–drug interactions [@taneja2022npkg] | Literature-mined and ontology relations, 745,512 nodes / 7,249,576 edges in the published version | Pharmacokinetic interaction focus; extraction error and contradictory edges acknowledged; not an assay-labelled benchmark | No — KAPPA's graph is a small provenance-typed demonstration, not a literature-mined at-scale KG |
| **Compound-centric plant chemical space (2026)** | Occurrence → taxonomic reconciliation → scaffolds → ChEMBL-linked bioactivity evidence [@compoundcentric2026] | LOTUS occurrence plus conservative ChEMBL linkage | Closest published work in spirit; it is a framework paper, not a deployed tool with a local UI | **Partially, in concept** — KAPPA must not claim novelty for "plant occurrence + scaffold + ChEMBL evidence" |
| **MoleculeNet-style benchmarks** | Standardised ML datasets/metrics for molecular property prediction [@wu2018moleculenet] | Benchmarked splits and metrics | Benchmarks rarely address evidence-type separation or provenance in an application | No — KAPPA follows benchmark practice rather than defines it |

## 3. Where KAPPA genuinely adds something

**Innovation statement.** KAPPA is a small, reproducible research workbench that keeps eight evidence
classes — botanical occurrence, documented traditional use, phytochemical occurrence, measured
biochemical activity, computational activity estimate, target identity, genetic association and
pharmacogenomic guideline evidence — operationally separate, attaches provenance to each, and refuses to
emit a blended "candidate score". Its distinctive mechanisms are the ones the landscape above does not
provide as a working, downloadable artefact:

1. **An evidence-type contract enforced in code and UI.** Every API response and card carries its evidence
   class; the historical equal-weight composite was deleted and a regression test prevents a score outside
   the empirical similarity range. Missing evidence is returned as *missing*, never scored as negative.
2. **A model whose uncertainty is priced in.** Scaffold-group holdout, training-only CV, two internal
   domain-shift stress tests, uncalibrated-probability diagnostics and an empirical 5th-percentile
   similarity reference. The out-of-domain control (sucrose, max Tanimoto 0.193 < 0.3236) returns
   `candidate_priority_score: null` from the live API — a behaviour, not a claim.
3. **Aggregation-choice transparency.** The duplicate-structure decision that most activity models make
   silently is run three ways and reported side by side (`docs/scientific_integrity_audit.md`, §2).
4. **A pharmacogenomic component that does not pretend.** A verified CPIC CYP2C19–clopidogrel guideline
   with phenotype/`CVI ACS PCI`-conditioned wording, a ClinVar identity cross-reference whose
   "Likely benign; other" label is explained as a disease-association call rather than a function call,
   and an explicit statement that no curcumin PGx guidance exists.

**What KAPPA is not.** It is not the first integrated natural-product platform; it is not a replacement
for LOTUS, IMPPAT, NPASS, ChEMBL, Open Targets or NP-KG; it does not perform target–disease inference,
pathway enrichment, docking or clinical prediction; it has no external validation. The integration
*concept* is established in the literature — KAPPA's contribution is the reproducible, evidence-typed
implementation and the discipline of what it refuses to output.

## 4. What a reviewer can verify in ten minutes

```bash
python -m src.run_pipeline             # rebuild data, model, metrics, figures, graph
python -m src.ml.duplicate_sensitivity # three aggregation rules, side by side
python scripts/make_figures.py         # regenerate result figures
pytest -q                              # 21 tests
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Then: open the app, submit curcumin (retrospective exact match), submit sucrose (score withheld), and read
the PGx panel. Every number quoted above is in `results/reports/`.

## 5. References

See [`references.bib`](../references.bib): `rutz2022lotus`, `zhao2023npass`, `vivekananth2023imppat2`,
`taneja2022npkg`, `taneja2024npkgv3`, `compoundcentric2026`, `zdrazil2024chembl`, `kim2025pubchem`,
`ochoa2025opentargets`, `cerezo2025gwas`, `wu2018moleculenet`, `lee2022cpic`.
