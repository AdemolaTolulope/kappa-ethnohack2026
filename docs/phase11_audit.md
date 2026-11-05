# KAPPA Phase 11 scientific, repository, and submission audit

**Audit date:** 2026-11-05 · **Scope:** existing KAPPA pilot continued in place; working data, API and UI retained rather than rebuilt. **Release status:** local implementation and full training run completed; test suite passed; final live-browser smoke, archive regeneration and public submission steps remain.

## Executive summary

Phase 11 addressed a material scientific-design problem: the earlier equal-weight average blended model activity estimates, training similarity, chemical identity, plant occurrence, traditional-use literature and pharmacogenomics into a single candidate score. That score was not scientifically interpretable. It has been removed. Similarity now functions only as a relative applicability diagnostic; only an **uncalibrated activity-band model output** can support exploratory triage, and it is withheld outside a training-derived similarity reference range. Chemical identity, measured activity, plant occurrence, secondary ethnobotanical report and PGx evidence are returned and displayed separately. Missing evidence is not treated as negative biology.

The project now has a positive, independently sourced pharmacogenomic **demonstration**, without implying curcumin/PTGS2 genetics: CPIC CYP2C19–clopidogrel guideline data, a ClinVar molecular-identity cross-reference for CYP2C19 c.681G>A / rs4244285 / *2, and phenotype/indication-filtered recommendations. The ClinVar record is identity-only; recommendations come from CPIC. The PGx component is intentionally disconnected from the plant/assay component.

The refreshed model evaluation is more demanding than the previous split: **RF test ROC-AUC 0.782, PR-AUC 0.940, balanced accuracy 0.637** on a 702-structure scaffold holdout with **82.62% active prevalence**. Document-held-out and temporal/scaffold-disjoint same-ChEMBL stress tests have RF ROC-AUCs **0.724** and **0.602**. These are important transferability warnings, not independent external validation. No experimental, clinical or independent-source validation has been performed.

## Scope and implementation audit

### Retained and verified source records

- ChEMBL CHEMBL230 human PTGS2 IC50 dataset: 7,482 raw activity records; 3,164 curated structure-unique assay representatives after explicit filtering and grey-zone exclusion.
- CPIC API CYP2C19–clopidogrel evidence: gene, *2 allele function, drug, pair, guideline and recommendation resources cached with request URLs and access date.
- NCBI ClinVar VCV000016897 / ESummary: molecular identity (`NM_000769.4(CYP2C19):c.681G>A`, dbSNP rs4244285, aliases including CYP2C19*2). The ESummary carries a germline classification of 'Likely benign; other' (evaluated 2018-08-07) for traits recorded as not specified/not provided; this is a disease-association label, not a drug-response classification, and it is not represented as the response association.
- Wikidata Q312266 P703 → Q42562: community-maintained “found in taxon” occurrence statement, not efficacy.
- Velayudhan et al. (2012): one secondary-source report of a turmeric cough/cold practice, with the paper’s Malayalam-source attribution and absent locality/community limits recorded. The original book was not accessed; no efficacy/safety claim is made.
- Curcumin demonstration is reproducibly cached at `results/reports/curcumin_demo_assessment.json`: exact training-structure match to ChEMBL CHEMBL140 activity 5245329, IC50 79,200 nM (operational inactive band), uncalibrated RF activity estimate 0.150, max training similarity 1.0. This same measured source record is in the model training corpus, so it is explicitly retrospective—not external or prospective evidence.
- Source rights and processing are consolidated in `docs/provenance_register.md`; see also `docs/data_provenance.md`.

### Core code changes

- `src/ml/train.py`: deterministic stratified scaffold holdout, training-only scaffold CV for RF/logistic baseline, training-only RF hyperparameter sensitivity, calibration diagnostics without fitting a test-set calibrator, similarity reference threshold, document-held-out/scaffold-disjoint stress test, temporal/scaffold-disjoint stress test, grouped permutation importance and explicit external-validation status.
- `backend/main.py`: distinct uncalibrated prediction, applicability, exact ChEMBL structure/assay match, chemical identity, plant context, and evidence profile; new cached CPIC evidence endpoint; filtered recommendations to population context `CVI ACS PCI ` and CYP2C19 intermediate/poor metabolizer; graph scopes.
- `src/prioritisation/rank.py`: composite removed; no score outside the empirical similarity range; evidence axes and missingness explicit.
- `src/knowledge_graph/graph.py`: typed/provenance-bearing occurrence, secondary traditional-use report, model-only, measured activity, and a separate disconnected variant/allele/drug/guideline/recommendation component.
- `frontend/index.html`: separate graph scopes and evidence panels; no fabricated score; model-only triage, record status, applicability and missing evidence shown separately; primary-source limitations retained.
- `scripts/make_figures.py` and `scripts/build_deck.py`: removed old composite-weight figure; refreshed model figures/deck for current metrics and evidence scope.

## Reproducible model validation

Current raw/curated counts, label rules, split, metrics, calibration, domain diagnostic, stress tests and caveats are in `docs/validation_report.md` and `results/reports/model_metrics.json`. Summary:

- Curated set: 3,164; 2,505 active / 659 inactive; overall active prevalence 79.17%.
- Primary test set: 702; 580 active / 122 inactive; test active prevalence 82.62%, which is also the approximate no-skill PR-AUC baseline.
- Scaffold test RF: ROC-AUC 0.782, PR-AUC 0.940, balanced accuracy 0.637, MCC 0.345; logistic baseline ROC-AUC 0.703, PR-AUC 0.907, balanced accuracy 0.624.
- RF 3-fold training-only scaffold CV mean ROC-AUC 0.810, mean PR-AUC 0.935, mean balanced accuracy 0.672. Fold variation is not a confidence interval.
- RF Brier 0.128; prevalence-constant Brier 0.146; Brier skill 0.118; 10-bin ECE 0.120. Outputs remain uncalibrated.
- Applicability reference cutoff: max Morgan radius-2 Tanimoto 0.3236, estimated as a 5th percentile from training-only scaffold out-of-fold examples. This is a heuristic relative reference range, not a calibrated confidence guarantee.
- Internal document-held-out/scaffold-disjoint test: n=567, RF ROC-AUC 0.724 and balanced accuracy 0.535.
- Internal temporal/scaffold-disjoint test (year ≥2019): n=944, RF ROC-AUC 0.602 and balanced accuracy 0.578; 11 missing-year structures excluded. Strong prevalence and selection caveat; not external validation.
- Four RF configurations were compared using training-only folds; the min-leaf-5 variant improves mean balanced accuracy over the primary RF but lowers ROC/PR. The prespecified primary model was retained; the held-out test was not used for model selection.
- No independent database validation, blinded evaluation, wet-lab experiment, clinical validation, or test-set recalibration.

## Pharmacogenomic evidence audit

- Cached CPIC gene–drug pair `pairid=110091`, CYP2C19 / RxNorm:32968 clopidogrel, CPIC level A / ClinPGx level 1A, “Actionable PGx,” not removed; pair citations include PMIDs 21716271, 23698643 and 35034351.
- CPIC guideline `id=100411`, ClinPGx PA166251443 (“CYP2C19 and Clopidogrel”); the cited guideline is doi:10.1002/cpt.2526, PMID 35034351.
- CPIC *2 allele record assigns “No function”; that one allele alone does not determine a full diplotype or phenotype.
- ClinVar VCV000016897 is used for variant-name/sequence identity only. The cached ESummary returns a germline classification ('Likely benign; other', evaluated 2018-08-07) for a not-specified trait. No response classification is attributed to ClinVar, and that disease-association label is not read as contradicting CPIC's allele function call.
- Frontend/API show only recommendation records for the intended `CVI ACS PCI ` population context and CYP2C19 intermediate/poor metabolizer phenotypes. These are context-bound published guideline statements, not individual medical advice.
- No genotype is supplied; no PGx edge connects to curcumin, plant use or PTGS2. Recommendation filtering is covered by automated tests.
- CPIC content is CC0 1.0 with attribution/version/current-source caveats; sources and access date are documented in the provenance register.

## Ethnobotanical and traditional-knowledge audit

The plant page and graph now show the secondary-use report as a **plant-level literature claim** distinct from Wikidata occurrence and assay evidence. The 2012 article’s table reports cough/cold practice and cites a Malayalam book (Namboodiri, 2004), not independently accessed. The reviewed table entry names no precise community/locality. KAPPA does not infer one, does not assert efficacy/safety, does not connect the practice to curcumin or the PTGS2 model, and does not reproduce a restricted source. The article’s reuse licence was not independently verified. Further community-specific or primary-source research would require rights, provenance, access and appropriate cultural review.

## End-to-end and automated verification

- `python -m src.run_pipeline`: **completed successfully** on the cached ChEMBL records; regenerated processed data, model artifact with applicability threshold, metrics, figures and GraphML graph.
- `pytest -q`: **17 passed** (2026-11-05), after the duplicate-aggregation and out-of-domain tests were added. Coverage includes RDKit validation, label/filter rules, group-held-out split, score gating, evidence graph provenance and topology/provenance separation, recommendation phenotype/population filtering, ClinVar germline-label semantics, disconnected graph scopes, structure SVG, prediction input validation, API and data counts.
- Interface corrections from that smoke test: compound explorer auto-selects the first record; the structure-panel caption now describes the RDKit depiction; IC₅₀ formatting uses significant figures; the record-count caption states the 300-record API cap and 200 listed rows; long evidence labels no longer overlap values; Enter submits the SMILES field; navigation has accessible labels.
- Headless-browser smoke test of the running app: eight views rendered, prediction/prioritisation/graph/PGx flows returned data, 0 console errors and 0 failed requests; screenshots in `results/smoke/`. This is interface verification, not external scientific validation.
- Judge-facing app exposes overview, plant evidence, compound table and assay records, SMILES prediction, model validation, source-aware graph scopes, separate pharmacogenomic example, export, methods and provenance.
- A live-browser/manual workflow smoke test and archive regeneration are still pending; do not claim them complete until run. The code/tests do not establish successful public hosting.

## EthnoHack 2026 submission readiness

Official event pages reviewed: [EthnoHack Devpost project/rules](https://ethnohack2026.devpost.com/) and [official rules](https://ethnohack2026.devpost.com/rules), accessed 2026-11-05. The posted requirements include a Devpost page, public source repository, README/data licences/reproduction instructions, pitch video ≤10 minutes and slide deck ≤10 slides. Official page lists submission deadline **8 Nov 2026, 04:00 EST**, equivalent to **8 Nov 2026, 10:00 WAT**. The posted rules state team size 2–5 and identify all members on Devpost; the landing page and rules differ in their participant eligibility wording, so eligibility should be confirmed with organizers. Registration is shown as closed 31 Oct 2026. Team membership/registration has not been verified here.

**Current status:** slide deck is 10 slides; written Devpost/demo/video narration drafts exist; AI and third-party data disclosures are drafted; no public GitHub repository, deployment URL, recorded pitch video, team names/roles, registration confirmation or eligibility confirmation is recorded. Thus these documents are preparation materials, not a completed compliant submission. Keep identities/contributions as placeholders until confirmed. Public release requires the team’s permission and a final rights/secret scan.

## Deliverables and release gates

- `docs/phase11_audit.md` (this audit)
- `docs/validation_report.md` (refreshed measured results and validation limits)
- `docs/model_card.md` (updated intended/prohibited uses, validation and domain diagnostic)
- `docs/provenance_register.md` and `docs/data_provenance.md`
- `docs/limitations.md`, README, Devpost copy, demo script, video narration, presentation notes and 10-slide deck
- `results/reports/model_metrics.json`, `results/reports/data_quality.json`, model artifact and graph output
- Remaining before final hand-off: live-browser smoke test; inspect all generated files and claims; update demonstration outputs; run final test/syntax/format checks; archive regeneration; confirm team and event eligibility; user-authorized public repository / deployment / submission steps.
