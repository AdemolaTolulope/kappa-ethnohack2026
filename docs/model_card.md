# Model card: KAPPA human PTGS2 IC50 activity-band classifier

**Version:** Phase 11 pilot, generated 2026-11-05. Artifact: `models/ptgs2_rf.joblib`. Full metrics: `results/reports/model_metrics.json` and `docs/validation_report.md`.

## Intended use

Research triage of candidate molecular structures for an operational, literature-derived human PTGS2 biochemical IC50 activity-band task. The application presents an uncalibrated model output for exploratory prioritization only when the structure is within a training-derived similarity reference range. Exact training-structure overlap is identified as retrospective.

## Prohibited / unsupported use

Not for clinical diagnosis, patient- or genotype-level prediction, treatment selection, efficacy or safety claims, binding-affinity estimates, plant/extract activity claims, or evidence that traditional practices work. The score is not a clinical or therapeutic probability. This is not a model of pharmacogenomic response.

## Data and labels

- ChEMBL target CHEMBL230, human PTGS2; 7,482 raw IC50/nM activity records retrieved 2026-11-05.
- After predeclared quality filters, structure validation and exact canonical structure deduplication: 3,164 structures; 2,505 active at IC50 ≤1,000 nM and 659 inactive at IC50 ≥10,000 nM. The 1–10 µM grey band is excluded, not treated as inactive.
- Positive prevalence: 79.17% overall and 82.62% in the scaffold test partition. Assay records are literature-selected and heterogeneous, not a representative natural-product or therapeutic distribution.
- Raw and curated provenance: `data/raw/chembl_ptgs2_ic50.jsonl`, `data/processed/ptgs2_curated.csv`, `results/reports/data_quality.json`, `docs/provenance_register.md`.

## Model and evaluation

- **Features:** seven RDKit descriptors (MW, calculated LogP, TPSA, HBD, HBA, rotatable bonds, fraction Csp3) plus a 512-bit Morgan radius-2 fingerprint.
- **Primary estimator:** `RandomForestClassifier(n_estimators=350, min_samples_leaf=2, max_features='sqrt', class_weight='balanced', random_state=17)`.
- **Baseline:** imputed, standardized, regularized logistic regression with class weights.
- **Primary split:** fixed first fold of stratified five-fold scaffold-group holdout (seed 17); exact structures deduplicated before split; 2,462 train / 702 test, zero shared scaffolds.
- **Primary RF test:** ROC-AUC 0.782, PR-AUC 0.940 against 0.826 test prevalence, balanced accuracy 0.637, MCC 0.345, Brier 0.128. Logistic baseline ROC-AUC 0.703, PR-AUC 0.907, balanced accuracy 0.624.
- **Additional validation:** three-fold training-only scaffold CV; training-only hyperparameter sensitivity; document-held-out and temporal/scaffold-disjoint internal ChEMBL stress tests. The latter two are not external validation and show degraded balance/ranking, particularly temporal ROC-AUC 0.602.
- **Calibration:** no calibration model fitted. RF probabilities are uncalibrated; held-out ECE 0.120. Report reliability diagnostics and the constant-prevalence baseline; do not interpret outputs as event probabilities.

## Applicability and output behavior

The artifact stores training SMILES and a threshold of 0.3236 maximum Morgan radius-2 Tanimoto. It is the fifth percentile of max similarities for training-only scaffold out-of-fold compounds against their fold’s training references. This is a relative empirical diagnostic, not a calibrated confidence or validated scientific domain boundary. Similarity is not rewarded as activity. The app withholds the model-only triage value outside the empirical reference range, displays identity/activity/ethnobotanical/PGx evidence as separate axes, and flags exact training matches as retrospective.

## Limitations, risks, and monitoring

- Class imbalance, ChEMBL publication/assay selection bias, assay-condition variation, target and chemical-series coverage, label cut-offs, duplicate collapse and publication-year caveats.
- Internal scaffold CV/test do not establish external generalization. Document/time shifts are substantial; independent data and blinded experimental validation are absent.
- The binary bands are operational; the intermediate interval is omitted. Scores do not represent continuous potency.
- Descriptor/fingerprint importance is associative model behavior, not a causal or mechanistic account.
- Human users should inspect original assay records and use an independently specified experimental protocol before making research decisions. Any material new data, model, feature, label, threshold or intended use requires a fresh validation and card revision.

## Governance and attribution

ChEMBL source data retain their upstream CC BY-SA 3.0 attribution/share-alike conditions; KAPPA's code licence does not relicense them. AI-assisted development is disclosed in `submission/third_party_disclosures.md`. No biological observations, independent validation results, or contributor identities are fabricated.
