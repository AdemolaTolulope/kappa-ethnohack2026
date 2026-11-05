# Scientific methodology

## Research question and scope
Can RDKit features classify curated measured human PTGS2 IC50 records into operational strong (≤1 µM) and weak (≥10 µM) bands under scaffold-group holdout, and can KAPPA present the resulting uncalibrated model estimate alongside distinct, source-backed evidence and applicability diagnostics? This is a biochemical-assay research task, not clinical prediction.

## Unit of analysis and labels
The modeling unit is one canonicalized chemical structure after exact canonical-SMILES duplicate collapse. Records require IC50, exact standard relation, nM units, assay type B, Homo sapiens target, no potential-duplicate or activity-validity flags, and valid RDKit structure. Active label = IC50 ≤1,000 nM. Inactive label = IC50 ≥10,000 nM. Intermediate values are excluded and are not treated as inactive. Labels are assay-context operational bands, not clinical pharmacology.

The representative record for an exact structure is selected by lowest IC50. This prevents exact-structure split leakage but means the retained publication year need not represent the first report; temporal analyses disclose this caveat.

## Molecular features and models
RDKit generates seven physicochemical descriptors (MW, Crippen LogP, TPSA, HBD, HBA, rotatable-bond count, fraction Csp3) and a 512-bit Morgan radius-2 fingerprint. No plant, gene or outcome feature is included in the assay classifier. Primary prespecified model: balanced RandomForestClassifier (350 trees, min leaf 2, sqrt max features, seed 17). Baseline: class-weighted standardized regularized LogisticRegression (C=0.1).

## Holdout, CV and sensitivity
Exact structures are deduplicated before group assignment. The **primary rule keeps the lowest surviving measured IC50** per canonical structure, because the grey band is removed before collapse; this choice is not hidden. A prespecified sensitivity analysis (`python -m src.ml.duplicate_sensitivity`) repeats the identical protocol under a median rule and under a rule that excludes structures carrying both an active and an inactive measurement (371 structures have multiple eligible measurements; 32 conflict). The primary result is unchanged and reproduces exactly; ranking metrics move only modestly, while the threshold-0.5 operating point moves substantially (balanced accuracy 0.637 → 0.671 / 0.729). Results and caveats: `docs/scientific_integrity_audit.md`. Bemis–Murcko scaffold (including an explicit acyclic group) is the unit of group separation. A fixed first fold of `StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=17)` is used as the main held-out evaluation; the realized split is 2,462 train / 702 test, with zero scaffold overlap. It is not forced to exact 80/20 row proportions.

Training-only evaluation uses three folds of `StratifiedGroupKFold` on the training partition for both estimators and for RF hyperparameter sensitivity. The primary model was prespecified; the held-out test is not used for model selection. Report ROC-AUC, prevalence-aware PR-AUC, precision/recall/F1 at 0.5, balanced accuracy, MCC, confusion matrix, Brier, log loss and calibration diagnostics. No confidence interval is inferred from fold SD.

Two further same-source stress tests hold out publication documents (with shared test scaffolds removed from training) and publication year ≥2019 (also scaffold-disjoint). They remain internal ChEMBL analyses; they do not constitute external validation. Details and limitations are in `validation_report.md`.

## Probability and applicability
Model outputs are uncalibrated. No post-hoc calibration is fitted on the test set. Held-out reliability diagrams, equal-width-bin ECE and Brier/log-loss against a constant training-prevalence baseline are descriptive only.

Maximum Morgan radius-2 Tanimoto similarity to training molecules is an applicability diagnostic. The artifact threshold is 0.3236: the fifth percentile of training-only scaffold out-of-fold compounds’ maximum similarity to their fold training references. It is a relative empirical reference, not a calibrated confidence guarantee or scientifically validated domain boundary. Similarity is not an activity component. The interface withholds model-only triage outside this reference range and flags exact training-structure overlaps as retrospective.

## Evidence profile (not a composite score)
The prediction API returns separate axes: model probability, applicability, exact ChEMBL assay/structure match, chemical identity match, plant-level context, ethnobotanical record, PGx evidence status, and missing evidence. There is no arithmetic average of model output, similarity, occurrence, identity, measured activity or PGx. A plant-level report is not compound-specific evidence and does not become assay activity. A missing record is not evidence of biological absence.

## Explanations and audit trail
Grouped permutation importance is calculated on the held-out scaffold test set for descriptors and the fingerprint block, with five repeats. It describes model reliance, not mechanism. Nearest training examples are context, not causal explanation. SHAP, mechanistic inference, calibrated probability and uncertainty intervals are not claimed.

## Pharmacogenomic evidence demonstration
A separate CPIC API example verifies the CYP2C19–clopidogrel pair, gene, *2 allele function, guideline and phenotype-specific recommendations. The recommendation route exposes only records for the intended cached `CVI ACS PCI ` population context and intermediate/poor metabolizer phenotypes. NCBI ClinVar VCV000016897 is used only for the c.681G>A / rs4244285 / *2 molecular identity alias; its ESummary reports a germline classification of 'Likely benign; other' for a not-specified trait, a disease-association label that says nothing about drug-metabolizer function and is not used to contradict CPIC's 'no function' assignment. A single *2 allele does not determine a full genotype or patient phenotype. No patient data are used; no graph edge links this guideline to curcumin, plant use or PTGS2.

## Ethnobotanical context
One secondary-source report from Velayudhan et al. (2012) is represented with the article's attribution to a Malayalam book, source gaps and no named locality/community. It documents a reported practice, not efficacy or safety; the underlying book was not independently accessed. The report is plant-level and is not mechanistically linked to curcumin or the PTGS2 classifier. See `data/processed/ethnobotanical_claims.json` and the provenance register.
