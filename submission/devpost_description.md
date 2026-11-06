# KAPPA — Knowledge-guided AI for Phyto-Pharmacogenomic Assessment

**Challenge track:** Natural Products for Drug Discovery  
**Short description:** A runnable research workbench that keeps plant occurrence, a carefully qualified secondary-use report, measured PTGS2 assay records, uncalibrated model estimates and pharmacogenomic guideline evidence separate and traceable.

## Problem
Natural-product evidence spans plant records, chemical structures, biochemical assays and human genomic resources. Combining them without provenance can make occurrence look like efficacy, a model score like validation, or an unrelated pharmacogenomic association look plant-specific. Researchers need a reproducible way to inspect evidence while preserving its source and uncertainty.

## What we built
KAPPA is an interactive FastAPI/RDKit/scikit-learn/NetworkX prototype with:

- Live/cacheable ChEMBL acquisition and explicit curation for human PTGS2 (CHEMBL230) IC50 records.
- RDKit structure validation, canonicalization, molecular descriptors and Morgan fingerprints.
- Random Forest and logistic baseline evaluated with a scaffold-group holdout, training-only scaffold CV, hyperparameter sensitivity, calibration diagnostics, applicability reference and internal document/temporal stress tests.
- A typed graph with distinct plant occurrence, secondary ethnobotanical report, measured assay, model-only and separate pharmacogenomic evidence.
- A structure lookup/prediction interface that exposes exact assay matches, chemical identity, applicability and missing-evidence status without a composite evidence score.
- API, CSV export, validation reports, model card, provenance register and a 10-slide presentation.

## How it works
We retrieved 7,482 ChEMBL human PTGS2 IC50/nM activity records. Following predeclared exact-relation, unit, assay, species, quality-flag and structure filters, and exact canonical-structure duplicate collapse, 3,164 structures remained: 2,505 at IC50 ≤1 µM and 659 at ≥10 µM. The 1–10 µM interval is omitted, not labelled inactive. Features are seven RDKit descriptors plus a 512-bit Morgan radius-2 fingerprint. The fixed scaffold-group split contains 2,462 training and 702 test structures, with no shared Bemis–Murcko scaffold.

Scores remain uncalibrated. Similarity is a relative applicability diagnostic, not a positive score or confidence guarantee. Chemical identity, measured activity, traditional-use context and PGx are never averaged into a composite. The model-only triage value is withheld outside the training-derived similarity reference range; exact training-structure hits are marked retrospective.

## Results and limitations
- Random Forest scaffold test: ROC-AUC **0.782**, PR-AUC **0.940**, balanced accuracy **0.637**, MCC **0.345**.
- Logistic-regression baseline: ROC-AUC **0.703**, PR-AUC **0.907**, balanced accuracy **0.624**.
- Test active prevalence is **82.62%**, so this is also the approximate no-skill PR-AUC baseline; PR-AUC is not interpreted without that context.
- Internal same-source publication/scaffold-disjoint test ROC-AUC: **0.724**. Temporal/scaffold-disjoint test ROC-AUC: **0.602**. These are internal ChEMBL stress tests, not external validation.
- **Duplicate-structure sensitivity (new):** of 4,327 unique eligible structures, 371 carry more than one eligible measurement and 32 carry both an active and an inactive measurement. Repeating the identical protocol with a median rule and with conflicting structures excluded gives holdout ROC-AUC **0.774** / **0.825** (primary 0.782) and balanced accuracy **0.671** / **0.729** (primary 0.637). Ranking is moderately stable; the threshold-0.5 operating point is not, so no claim is made about triage accuracy at a fixed cutoff.
- **Refusal rule demonstrated:** sucrose has a maximum training similarity of **0.193**, below the **0.3236** empirical reference, and the API returns `candidate_priority_score: null` while the interface shows "Not rankable · probability withheld" with the similarity value and the reason. An in-domain molecule still receives its number in the same view.
- **Provenance is enforced, not described:** the single ethnobotanical record passes a fail-closed validator that requires authors, year, title, journal and a URL or DOI, requires non-empty limitations, and rejects any record that asserts a compound linkage. `python -m src.ethnobotany` and `/api/ethnobotany` expose the coverage statement ("limited demonstration corpus — not a systematic ethnobotanical survey").
- **Numbers withdrawn when unreproducible:** an earlier draft quoted ROC-AUC 0.832 / PR-AUC 0.966. Seven protocols were re-run and none reproduces that pair, which instead sits inside the spread of one arbitrary scaffold split; the audited 0.782 / 0.940 result is retained and the historical pair is withdrawn (`docs/historical_metric_discrepancy.md`).
- No independent database or experimental/clinical validation has been performed. Read [`docs/validation_report.md`](../docs/validation_report.md), [`docs/scientific_integrity_audit.md`](../docs/scientific_integrity_audit.md) and [`docs/limitations.md`](../docs/limitations.md).

## Evidence demonstrations

- **Occurrence:** Wikidata’s P703 statement links curcumin Q312266 to *Curcuma longa* Q42562; this is botanical occurrence only.
- **Ethnobotanical context:** a 2012 secondary review reports one turmeric cough/cold practice and cites a Malayalam source not independently accessed. The entry does not identify a specific community/locality. It is not evidence of efficacy or safety, and is not linked to curcumin/PTGS2.
- **Pharmacogenomics:** independently, a cached CPIC CYP2C19–clopidogrel guideline example shows CPIC level A / ClinPGx 1A, with CPIC intermediate/poor-metabolizer recommendations filtered to the stated ACS/PCI context. ClinVar VCV000016897 is used only for molecular identity (c.681G>A / rs4244285 / *2); its cached germline label — "Likely benign; other", for a not-specified trait — is a disease-association statement, not a drug-metaboliser function call. This component is disconnected from the phytochemical model and is not patient advice.

## How this differs from existing resources

LOTUS, IMPPAT, NPASS, ChEMBL, PubChem, Open Targets, the GWAS Catalog and NP-KG already provide the databases and much of the integration; a 2026 compound-centric framework already links plant occurrence, taxonomy, scaffolds and ChEMBL evidence. KAPPA does not claim to be the first integrated natural-product platform. Its contribution is narrower and checkable: an evidence-type contract enforced in code and UI, with an explicit refusal rule, reproducible benchmarks, and a pharmacogenomic component that stays disconnected and non-prescriptive. The full comparison matrix, with per-resource limits and overlap, is in [`docs/competitive_landscape.md`](../docs/competitive_landscape.md).

## Technologies
Python, RDKit, scikit-learn, Pandas, NumPy, FastAPI, NetworkX, Matplotlib, JavaScript/HTML/CSS, pytest, ChEMBL REST, CPIC API and NCBI ClinVar E-utilities.

## Data, rights and responsible research
Source queries, retrieval dates, rights, transformations and limitations are in [`docs/provenance_register.md`](../docs/provenance_register.md). ChEMBL data are CC BY-SA 3.0; CPIC curated content is CC0 1.0 with attribution/current-source caveats. Other sources retain their own terms. The secondary ethnobotanical article’s reuse licence was not independently verified. KAPPA does not infer community identity or use restricted knowledge. Significant AI-assisted development is disclosed in [`third_party_disclosures.md`](third_party_disclosures.md).

## Impact and next steps
KAPPA demonstrates a reproducible, bounded research workflow—not a discovery claim or clinical tool. Next: rights-cleared, source- and community-grounded ethnobotanical evidence; independent assay evaluation with overlap checks; a prospective blinded assay; broader expert review; and continuous source/version monitoring.

## Team and submission status
- **Team name:** [Confirm]
- **Members and actual contributions:** [Add confirmed names and contribution statements]
- **No contributor identity or contribution is claimed in this draft.**

Source code: https://github.com/AdemolaTolulope/kappa-ethnohack2026 (public, branch `main`, verified by an anonymous clone that passed 22 tests and reproduced the reported metrics). The pipeline and interface are verified (22 tests, clean-room bundle reproduction to ≤1.2e-16, headless-browser pass). A persistent deployment URL, the pitch video, confirmed team/eligibility and the Devpost submission itself are not yet in place. The posted EthnoHack event information lists a 2–5 person team, a public source repository, a pitch video of at most 10 minutes and a slide deck of at most 10 slides; the event landing-page and rules eligibility wording should be confirmed with organizers. See [`docs/phase11_audit.md`](../docs/phase11_audit.md).

**Repository:** https://github.com/AdemolaTolulope/kappa-ethnohack2026  
**Demo URL:** none — the app runs locally; no persistent public deployment is claimed.
