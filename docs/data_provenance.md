# Data provenance and cleaning

The authoritative Phase 11 source/rights table is [`provenance_register.md`](provenance_register.md). This file records the curation outputs and label rules for the human PTGS2 model.

**Retrieval date:** 2026-11-05. ChEMBL REST target CHEMBL230 returned **7,482** raw human PTGS2 IC50 records in nM. Raw response lines are cached at `data/raw/chembl_ptgs2_ic50.jsonl`; processing is reproducible in `src/data_pipeline.py`.

## Explicit filtering and labels

- Retain records with numeric, finite, positive standard values, parseable structure, `standard_type=IC50`, `standard_relation='='`, `standard_units='nM'`, single-protein assay type B, Homo sapiens target, no ChEMBL potential-duplicate flag, and no activity validity flag.
- Exclude the **1–10 µM** interval as ambiguous/intermediate. This is not evidence of inactivity.
- Canonicalize with RDKit and collapse exact canonical-structure duplicates before train/test splitting. The representative record is selected by lowest IC50, which can affect publication-year assignment.
- Final curated set: **3,164** unique structures, 2,505 active at ≤1 µM and 659 inactive at ≥10 µM; positive prevalence 79.17%. Full sequential exclusions and missing fields are in `results/reports/data_quality.json`.
- No biological observations or labels were synthesized. The analysis is literature-record curation, not a prospective experimental study or representative distribution of natural products.

## Scope boundaries

The plant occurrence statement, the secondary ethnobotanical report, measured ChEMBL assay records, model estimates, ClinVar molecular identity cross-reference, and CPIC clinical guideline data are separate evidence types. They are not averaged or used to infer one another. See [`phase11_audit.md`](phase11_audit.md), [`model_card.md`](model_card.md), and [`limitations.md`](limitations.md).
