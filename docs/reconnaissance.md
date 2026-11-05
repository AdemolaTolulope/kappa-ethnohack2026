# Phase 1 reconnaissance and execution plan

**Checked:** 2026-11-05. **Execution environment:** Python 3.13.16, Node 20.20.2; scikit-learn, Pandas, NumPy, NetworkX and plotting stack were available; RDKit, FastAPI and Uvicorn were initially absent and installed from pip. ChEMBL REST, PubChem PUG REST and Wikidata SPARQL responded successfully without credentials. No pre-existing project files were present.

## Focused findings

1. LOTUS already offers referenced organism–natural-product occurrence knowledge; IMPPAT already curates Indian medicinal plant, phytochemical and therapeutic-use relations. Do not claim KAPPA is the first resource/graph.
2. ChEMBL provides a suitable assay dataset with target and activity IDs. The human PTGS2 (CHEMBL230) endpoint produced 7,482 IC50 records; enough data for a meaningful, narrowly scoped benchmark.
3. A live Wikidata check confirms a P703 statement linking curcumin Q312266 to *Curcuma longa* Q42562; PubChem CID 969516 supplies a standard structure cross-check. This is an occurrence/identity context only, not a medicinal-use claim.
4. Human target identity can be cross-referenced to UniProt P35354, but no patient-level pharmacogenomic response data were ingested. KAPPA exposes that evidence gap rather than claiming pharmacogenomic prediction.
5. Defensible gap: a small, reproducible, source-aware hand-off from botanical occurrence through real, target-specific assay data to leakage-conscious ML and applicability diagnostics, with evidence types and limits shown in the application.

## Pilot decision

Use curcumin/*Curcuma longa* as a source-checkable illustrative natural-product anchor and human PTGS2 biochemical IC50 as the model task. Selection is based on accessible identifiers and measured data volume, not an asserted therapeutic indication. ChEMBL has 7,482 records; processing yielded 3,164 structures in two declared IC50 bands after an ambiguity band was excluded.

## Implementation sequence (completed status)

1. Reconnaissance, literature/database comparison, pilot selection — **done** (`docs/research_gap.md`, `docs/data_provenance.md`).
2. Architecture and explicit evidence boundary — **done** (`docs/architecture.md`, `docs/scientific_methodology.md`).
3. Live data retrieval, auditable JSONL cache, missingness/filter audit — **done** (`src/data_pipeline.py`, `results/reports/data_quality.json`).
4. RDKit structure/descriptor pipeline and identifier context — **done**.
5. Random Forest + logistic baseline, scaffold holdout and grouped scaffold CV — **executed and metrics saved** (`results/reports/model_metrics.json`).
6. NetworkX evidence graph and transparent score/weight sensitivity — **done**.
7. FastAPI service and responsive research UI — **running at the live preview**.
8. Tests and endpoint verification — **7 tests passing; API and frontend JavaScript syntax checked**.
9. Documentation and reproducible scientific figures — **done**.
10. 10-slide presentation, under-10-minute pitch, demo and Devpost draft — **done**.

## Open scientific work (not represented as complete)

Independent external assay validation, licence-cleared ethnobotanical-use integration, patient/population pharmacogenomic evidence, calibrated uncertainty, experimental validation and licensed production hosting remain future work. No credentials or team identities were required for the executed prototype; confirmed team details must be filled by the actual team before submission.
