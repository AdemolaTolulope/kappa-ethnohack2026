# KAPPA
## Knowledge-guided AI for Phyto-Pharmacogenomic Assessment

**EthnoHack 2026 · Natural Products for Drug Discovery**

KAPPA is a reproducible research prototype that keeps botanical occurrence, ethnobotanical literature, measured human PTGS2 (COX-2) assays, model estimates, chemical identity, and pharmacogenomic evidence as separate evidence types. It combines RDKit processing, a scaffold-aware ML benchmark, provenance-labelled knowledge-graph scopes and a judge-facing web workbench. It is **not** a clinical, therapeutic or patient-response system.

## Current pilot results · 2026-11-05

- Acquired **7,482** ChEMBL human PTGS2 IC50/nM activity records; curated **3,164** exact-structure representatives: 2,505 at IC50 ≤1 µM and 659 at ≥10 µM. The intermediate 1–10 µM band is omitted, not labelled inactive.
- Evaluated a class-weighted Random Forest and logistic-regression baseline using a fixed stratified Bemis–Murcko scaffold-group holdout. Test size **702**; active prevalence **82.62%** (the no-skill PR-AUC baseline).
- Random Forest: ROC-AUC **0.782**, PR-AUC **0.940**, balanced accuracy **0.637**, MCC **0.345**. Logistic baseline: ROC-AUC **0.703**, PR-AUC **0.907**, balanced accuracy **0.624**.
- Document-held-out and temporal/scaffold-disjoint analyses remain **internal ChEMBL stress tests**, not external validation; temporal ROC-AUC was **0.602**. No external database, prospective, wet-lab or clinical validation has been performed.
- Predictions are uncalibrated. A training-only Tanimoto reference threshold is shown as a relative applicability diagnostic, not a probability of correctness. Exact training-structure overlap (including the illustrative curcumin input) is retrospective.
- **Duplicate-structure sensitivity:** of 4,327 unique eligible structures, 371 carry more than one measurement and 32 carry both an active and an inactive one. Repeating the protocol with a median rule or with conflicting structures excluded gives holdout ROC-AUC 0.774 / 0.825 (primary 0.782) and balanced accuracy 0.671 / 0.729 (primary 0.637): ranking is moderately stable, the threshold-0.5 operating point is not. The primary result is unchanged and the analysis is reported separately.
- No evidence types are averaged. Similarity is not a reward; model-only triage is withheld outside the empirical reference range — verified end-to-end with sucrose (max Tanimoto 0.193 < 0.3236 → `candidate_priority_score: null`). Read [`docs/validation_report.md`](docs/validation_report.md), [`docs/scientific_integrity_audit.md`](docs/scientific_integrity_audit.md) and [`docs/model_card.md`](docs/model_card.md).

## Why KAPPA exists (and what it does not claim)

The problem is not missing data but missing evidence contracts: occurrence, traditional-use reports, measured
activity and pharmacogenomic guidance are routinely joined without recording which kind of statement a link is,
and the resources themselves document this (LOTUS, NPASS, IMPPAT, NP-KG; see
[`docs/competitive_landscape.md`](docs/competitive_landscape.md)). KAPPA's bounded contribution is an
evidence-type contract with an explicit refusal rule, implemented and tested rather than asserted
([`docs/innovation_statement.md`](docs/innovation_statement.md)). It does **not** claim to be the first
integrated natural-product platform, and it explicitly credits the published work it overlaps with.

## Verified evidence demonstrations

- **Occurrence:** Wikidata Q312266 P703 reports curcumin “found in taxon” *Curcuma longa* Q42562. This is occurrence/taxonomy context, not traditional use or efficacy.
- **Ethnobotany:** one separately attributed 2012 secondary-source report describes a turmeric cough/cold practice. The paper cites a Malayalam book not independently accessed and does not identify the specific community/locality. It is a report of a practice, not efficacy or safety evidence; no mechanistic connection to curcumin/PTGS2 is asserted.
- **Pharmacogenomics:** a verified, independent CPIC CYP2C19–clopidogrel guideline demonstration includes an identity-only ClinVar cross-reference for CYP2C19 c.681G>A / rs4244285 / *2, whose cached 'Likely benign; other' germline label concerns a not-specified disease trait rather than drug-metabolizer function. CPIC recommendations are displayed only with the intended phenotype and `CVI ACS PCI` population context. The demo has no patient genotype and is intentionally disconnected from the natural-product/curcumin model.

Source rights, retrieval URLs and limitations are in [`docs/provenance_register.md`](docs/provenance_register.md). Do not infer evidence from data sources not downloaded and verified.

## Run locally

Requires Python 3.10+ (tested here with Python 3.13), compatible RDKit wheels and internet access for first ChEMBL acquisition.

```bash
cd KAPPA
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\\Scripts\\activate
python -m pip install -r requirements.txt
python -m src.run_pipeline      # first run fetches ChEMBL; later runs use cache
pytest -q
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Open http://localhost:8000. The app includes overview, plant-level evidence, compounds/assays, SMILES prediction, genomic context, evaluation, disconnected plant/assay and PGx graph views, evidence-aware triage, methods and provenance. Export the curated table with the in-app CSV action. No credentials are required.

## Project map

- `src/data_pipeline.py` — paginated ChEMBL acquisition, explicit filters and data audit.
- `src/chemistry/` — RDKit structure parsing, descriptors and fingerprints.
- `src/ml/train.py` — scaffold holdout/CV, imbalance-aware metrics, training-only sensitivity, calibration diagnostics, applicability and internal stress tests.
- `src/ml/duplicate_sensitivity.py` — lowest/median/conflict-excluded aggregation rules under one protocol, with a reproduction check against the primary result.
- `src/knowledge_graph/` — typed evidence/provenance graph with separate components.
- `src/prioritisation/` — model-only in-domain triage; no composite evidence score.
- `src/pharmacogenomics/cpic_demo.py` — cached CPIC API demonstration fetch.
- `backend/main.py` — FastAPI endpoints and static application.
- `frontend/index.html` — responsive no-CDN research UI.
- `data/` — cached source records and processed outputs; see rights register before re-use.
- `results/` — measured metrics, audit outputs, figures and tables.
- `docs/` — audit, validation, model card, provenance, methodology, limitations and responsible-AI notes.
- `submission/`, `presentation/` — draft materials; team identity and contributions remain placeholders until confirmed.

## Scientific and cultural guardrails

Model scores are not affinity estimates, clinical outcomes or treatment benefit. Ethnobotanical reports do not establish efficacy. CPIC evidence is not applied to individuals. Traditional knowledge is not detached from its source and cultural context. Data sources retain their own licences; KAPPA’s MIT code licence does not relicense them. Generative-AI-assisted development is disclosed in [`submission/third_party_disclosures.md`](submission/third_party_disclosures.md).

## EthnoHack submission status

The slide deck is capped at 10 slides, renders cleanly ([`presentation/rendered/`](presentation/rendered/)), and written Devpost, demo and video drafts are prepared. The pipeline, tests and running interface have been verified locally, including a headless-browser pass with screenshots in [`results/smoke/`](results/smoke/).

A portable copy of the whole project (cached data, model, figures, rendered deck, screenshots) is at `submission/KAPPA_ethnohack2026_bundle.zip`; it was extracted to a clean directory where the tests passed and the pipeline reproduced the stored metrics. A public source repository, deployment URL, pitch recording, confirmed 2–5 member team and Devpost submission are **not** in place, and the organisers still need to confirm whether late registration and this team's eligibility are possible. Do not describe KAPPA as a completed submission until those gates are satisfied. The itemised state, including the exact commands and the claims this project deliberately does not make, is in [`docs/release_checklist.md`](docs/release_checklist.md).

## Attribution and licences

KAPPA code is MIT-licensed. ChEMBL records carry CC BY-SA 3.0 terms; CPIC curated content is CC0 1.0 with attribution/current-version caveats; other sources retain their own terms. The article underlying the secondary ethnobotanical report was not independently licence-verified and is cited, not reproduced. See [`docs/provenance_register.md`](docs/provenance_register.md) and [`references.bib`](references.bib).
