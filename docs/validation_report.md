# Validation and execution report

**Run date:** 2026-11-05. **Status:** full cached-data pipeline completed with the current training code; test suite passed. Results are internal retrospective analyses, not external validation.

## Data and curation

- Source: ChEMBL REST, human PTGS2 / CHEMBL230, IC50, nM; 7,482 raw activity records cached in `data/raw/chembl_ptgs2_ic50.jsonl`.
- Sequential filters, RDKit structure validation, and exact canonical-structure duplicate collapse yielded **3,164 structures**: **2,505 active** (IC50 ≤1 µM) and **659 inactive** (IC50 ≥10 µM). The 1–10 µM grey band was excluded rather than relabelled. Overall positive prevalence is **79.17%**.
- 3,661 structurally valid labelled measurements preceded exact-structure collapse; 497 duplicate structures were removed. ChEMBL document metadata contain 370 distinct document IDs and 11 missing publication years.
- Filtering requires exact standard relation, nM units, single-protein assay type B, Homo sapiens, no potential-duplicate flag, no validity flag, valid structure. Full sequential counts and missingness are in `results/reports/data_quality.json`.
- No biological measurements, labels, citations, or metrics were synthesized. No wet-lab or independent-source external validation was performed.

## Split and primary held-out evaluation

Features are seven RDKit descriptors plus a 512-bit Morgan radius-2 fingerprint. The prespecified model is a class-weighted Random Forest; regularized logistic regression is the baseline. A fixed first fold of `StratifiedGroupKFold(n_splits=5, shuffle=True, seed=17)` holds Bemis–Murcko scaffold groups out. Exact canonical structures are deduplicated before splitting. The realized split is 2,462 train / 702 test (not a forced 80/20 row split); scaffold overlap is zero. Test set: 580 active and 122 inactive, **82.62% active**. Therefore the no-skill PR-AUC baseline on this test set is its positive prevalence, approximately **0.826**.

| Model | ROC-AUC | PR-AUC | Precision @0.5 | Recall @0.5 | F1 | Balanced accuracy | MCC | Brier | Log loss | Confusion matrix (TN,FP; FN,TP) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Random Forest | 0.782 | 0.940 | 0.870 | 0.947 | 0.907 | 0.637 | 0.345 | 0.128 | 0.413 | (40,82;31,549) |
| Logistic regression | 0.703 | 0.907 | 0.875 | 0.781 | 0.825 | 0.624 | 0.214 | 0.202 | 0.733 | (57,65;127,453) |

A high PR-AUC should be interpreted against the **0.826 test prevalence**, and is not a stand-alone quality claim. At threshold 0.5, RF sensitivity is high but balanced accuracy and MCC are modest, with many false positives among the inactive class. These metrics describe this specific ChEMBL split and operational label, not a calibrated probability of biological or therapeutic success.

## Training-only scaffold cross-validation and sensitivity

The 2,462-row training partition was evaluated with three stratified scaffold-group folds (same folds for RF and logistic regression). RF fold ROC-AUCs were **0.847, 0.799, 0.783** (mean 0.810); PR-AUCs **0.939, 0.943, 0.923** (mean 0.935); balanced accuracies **0.689, 0.684, 0.642** (mean 0.672). Logistic means: ROC-AUC 0.722, PR-AUC 0.888, balanced accuracy 0.662. Fold variation is not a confidence interval.

Hyperparameter sensitivity used the same training-only scaffold folds; no held-out test result selected a model. The shipped primary RF configuration remains the prespecified 350-tree, min-leaf-2, `sqrt`-feature model.

| RF parameters (trees / min leaf / max features) | Mean ROC-AUC (SD) | Mean PR-AUC | Mean balanced accuracy |
|---|---:|---:|---:|
| 200 / 1 / sqrt | 0.817 (0.038) | 0.937 | 0.640 |
| 350 / 2 / sqrt (primary) | 0.808 (0.033) | 0.935 | 0.671 |
| 350 / 5 / sqrt | 0.789 (0.034) | 0.927 | 0.699 |
| 500 / 5 / log2 | 0.781 (0.042) | 0.923 | 0.696 |

The trade-off matters: the leaf-5 configuration improves mean balanced accuracy versus the primary RF while lowering ROC-AUC and PR-AUC. No single metric is optimized or represented as universal utility.

## Calibration, threshold, and applicability diagnostics

Probabilities are **uncalibrated**. On the scaffold holdout, RF Brier score is 0.128 (constant training-prevalence baseline 0.146; Brier skill 0.118) and 10-bin equal-width ECE is 0.120. Logistic Brier is 0.202 (skill −0.388) and ECE 0.187. Reliability bins and prediction histograms are in `results/reports/model_metrics.json` and `results/figures/calibration_diagnostics.png`. No post-hoc calibration was fit on the test set.

The application estimates an applicability reference threshold of **0.3236 max Morgan radius-2 Tanimoto**, the fifth percentile of training-only scaffold out-of-fold molecules’ maximum similarity to their fold training set. This is a relative similarity diagnostic, **not** a calibrated confidence guarantee or scientifically validated domain boundary. 1.85% of the held-out test structures fall below it. Similarity is not a positive scoring component; the UI withholds the model-only triage value outside this empirical range. Exact training-structure matches are flagged as retrospective.

## Duplicate-structure aggregation sensitivity (new, 2026-11-05)

Command: `python -m src.ml.duplicate_sensitivity` → `results/reports/duplicate_sensitivity.json`,
`results/figures/duplicate_sensitivity.png`. The primary analysis (lowest IC50 per canonical structure) is
unchanged and reproduces exactly (`reproduced_within_1e-9: true`).

| Rule | Structures | Holdout ROC-AUC | Holdout PR-AUC | Balanced accuracy | MCC | 3-fold CV ROC-AUC |
|---|---:|---:|---:|---:|---:|---:|
| Lowest IC50 (primary) | 3,164 | 0.7819 | 0.9396 | 0.6372 | 0.3449 | 0.7931 ± 0.0387 |
| Median IC50 | 3,084 | 0.7744 | 0.9232 | 0.6707 | 0.3996 | 0.7963 ± 0.0579 |
| Conflicting structures excluded | 3,068 | 0.8250 | 0.9267 | 0.7286 | 0.4636 | 0.8052 ± 0.0149 |

Of 4,327 unique eligible structures, 371 carry more than one eligible measurement and 32 carry both an active
and an inactive measurement. Ranking metrics are moderately stable across rules; the threshold-0.5 operating
point is not (balanced accuracy 0.637–0.729, MCC 0.345–0.464). The primary rule is retained; the exclusion rule
is not adopted because it removes ambiguous structures and shrinks the test set to 464. Details and caveats in
[`scientific_integrity_audit.md`](scientific_integrity_audit.md).

## Internal domain-shift stress tests (not external validation)

| Evaluation | Test / train sizes | Scaffold overlap | RF ROC-AUC | PR-AUC | Balanced accuracy | Interpretation |
|---|---:|---:|---:|---:|---:|---|
| Publication-document-held-out, then shared scaffolds removed from train | test 567 (71 documents) / train 2,043 | 0 | 0.724 | 0.848 | 0.535 | Internal ChEMBL document shift; low balanced accuracy and many false positives |
| Temporal: publication year ≥2019 vs <2019, shared test scaffolds removed from train | test 944 / train 1,689; 11 missing years excluded | 0 | 0.602 | 0.907 | 0.578 | Marked ranking degradation; prevalence differs (87.61% positive) |

Both are internal stress tests from the same curated ChEMBL source and target, not external database, prospective, or experimental validation. The temporal split inherits an important caveat: exact-structure duplicate collapse retains one representative row by lowest IC50, so its publication year may not be the first report. These shifts limit transportability claims.

Grouped permutation importance is descriptive global model reliance, not mechanistic explanation; the fingerprint block dominates. Outputs are in `results/reports/model_metrics.json` and figures. No SHAP, pathway inference, docking, human response prediction, or model calibration claim is made.

## Tests and end-to-end pilot

- `python -m src.run_pipeline` completed on the cached ChEMBL acquisition and regenerated the curated dataset, model artifact (including empirical applicability threshold), metrics, figures, and a GraphML knowledge graph.
- `pytest -q`: **21 passed** (2026-11-05). Two tests added this cycle cover the duplicate-aggregation rules and the out-of-domain withholding behaviour. Tests include label/filter behavior; scaffold group separation; model-only score gating; evidence graph provenance; edge topology versus provenance-key separation; CPIC phenotype/context filtering; ClinVar identity cross-reference and its germline-label semantics; disconnected PGx and phytochemical graph scopes; API and invalid-SMILES checks.
- FastAPI exposes overview, compound search/export, prediction, graph scopes, evidence/metrics, CPIC demonstration, and target identity routes. The UI keeps occurrence, ethnobotanical report, measured activity, predictions, chemical identity, and PGx separate.
- Live-browser smoke test (headless Chromium, served by uvicorn on 2026-11-05): all eight views rendered; prediction, out-of-domain prediction, candidate prioritisation, graph scope switching, and the PGx panel returned data; console errors **0**, failed requests **0**; the evidence graph rendered 40 nodes/38 edges (pilot scope) and 7 nodes/9 edges (PGx scope); layout has no horizontal overflow at 1500 px or 820 px. Screenshots are stored in `results/smoke/`. A screenshot record is not an independent scientific or external validation.
- Interface refinements made from that pass: the compound explorer auto-selects the first record so the structure panel is never blank; the stale caption claiming the structure image was "not embedded" was corrected to describe an RDKit depiction; IC₅₀ values now use significant-figure formatting instead of a fixed one decimal place; the record-count caption states that the API cache exposes 300 records and lists the first 200; the Methods view gained split/validation/calibration/stress-test/applicability rows.
- Bugs found and fixed during that smoke test: edge payloads previously overwrote the graph `source`/`target` topology keys with provenance strings (now emitted as `source_reference`, with a regression test); the evidence-graph view crashed on edges whose endpoints were filtered out of scope; long evidence labels in the prediction card overlapped their values (CSS grid fix); pressing Enter in the SMILES field did not submit; collapsed icon-only navigation had no accessible labels.
- Clean-room reproduction: `submission/KAPPA_ethnohack2026_bundle.zip` was extracted to an empty directory outside the project, then `pytest -q` (**21 passed**) and `python -m src.run_pipeline` were executed there. The rerun reproduced the stored metrics to floating-point round-off only (largest observed difference ≈1.4e-16 across ROC/PR-AUC, balanced accuracy, Brier, log loss, CV folds, stress tests and the applicability threshold), so the documented commands work from a fresh extraction and the pipeline is deterministic given the cached acquisition.
- External experimental validation: **not performed**.

## Independent validation opportunity and reproduction

The next validation should prospectively specify and obtain an independent human-PTGS2 biochemical IC50 dataset (for example, a blinded assay panel or a genuinely source-independent dataset), reconcile target constructs, assay protocol, units and duplicate compounds before scoring, and report prevalence, PR metrics, calibration, domain coverage and uncertainty. A database named “external” is not sufficient if records overlap the training publications or assays.

```bash
python -m pip install -r requirements.txt
python -m src.run_pipeline
pytest -q
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

The first pipeline run fetches ChEMBL; later runs use the JSONL cache. See `docs/phase11_audit.md`, `docs/model_card.md`, `docs/provenance_register.md`, and `docs/limitations.md` for audit, scope, licensing, and risk details.
