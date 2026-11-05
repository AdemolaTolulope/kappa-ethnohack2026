# KAPPA pitch script (approx. 7 minutes)

## Slide 1 — KAPPA

Imagine a promising natural product appearing in a plant record, a chemical database, a target assay and a genomics resource—and each one uses a different identifier, evidence standard and reuse rule. Researchers spend time reconciling those pieces before they can ask a useful question. KAPPA is a research workbench that connects those hand-offs, keeps the sources visible, and makes the limits of computational inference explicit. It is not a treatment recommender.

## Slide 2 — The problem

Natural-product discovery is not short of resources. It is fragmented across botanical occurrence, chemical identity, experimental bioactivity, pathways and human genetics. And the most important scientific failure mode is often not a missing algorithm; it is an overclaim. A compound reported in a plant does not prove a traditional use. A traditional use does not prove clinical efficacy. A model score on a biochemical assay is not a patient outcome. KAPPA makes those boundaries part of the interface.

## Slide 3 — The gap

We reviewed established resources including LOTUS, IMPPAT, ChEMBL, Open Targets, the GWAS Catalog and natural-product knowledge-graph work such as NP-KG. These already provide substantial databases and integration. So our contribution is deliberately narrower: an executable, auditable pathway from a traceable occurrence statement through a real target assay dataset to a scaffold-aware benchmark, applicability check and evidence-tiered research output. We are claiming an integration and reproducibility contribution—not the first natural-products AI or knowledge graph.

## Slide 4 — How it works

Our pilot retains a Wikidata occurrence statement for Curcuma longa and curcumin, separately records a qualified secondary ethnobotanical report, and analyzes human PTGS2 assay records from ChEMBL. FastAPI serves evidence-aware results; NetworkX keeps edge types and sources visible. An independent CPIC CYP2C19–clopidogrel demonstration occupies a disconnected PGx graph component. Occurrence, traditional-use report, assay, model and PGx evidence are not interchangeable.

## Slide 5 — Data and labels

The ChEMBL API returned 7,482 human PTGS2 IC50 records at retrieval. After requiring exact standard relations, nanomolar units, single-protein assay type, human target, no flagged duplicates or validity issues, structure parsing and exact canonical-structure deduplication, 3,164 molecules remained. We label IC50 of one micromolar or less as the strong-activity band, and ten micromolar or greater as weak. We exclude the middle band rather than quietly calling it inactive. There are 2,505 positives and 659 negatives, so imbalance is substantial and reported.

## Slide 6 — Machine learning

We created seven standard physicochemical descriptors and a 512-bit Morgan radius-two fingerprint. Our prespecified primary model is a balanced random forest; logistic regression is the baseline. We used a fixed stratified Bemis–Murcko scaffold-group holdout: 2,462 training and 702 test structures, with no shared scaffold. The RF scaffold-test ROC-AUC is 0.782, compared with 0.703 for logistic regression. Test positive prevalence is 82.6 percent, so the RF PR-AUC of 0.940 must be compared with a no-skill baseline near 0.826. Balanced accuracy is 0.637. Three-fold training-only scaffold CV, sensitivity and calibration diagnostics are reported. Document-held-out and temporal/scaffold-disjoint tests yield RF ROC-AUC 0.724 and 0.602; both are internal ChEMBL stress tests, not external validation.

## Slide 7 — Pharmacogenomics and graph

The graph includes source-typed plant/assay records and a separate verified PGx example. CPIC links CYP2C19–clopidogrel (pair 110091, level A; ClinPGx 1A) and phenotype-conditioned recommendations under guideline 100411. ClinVar VCV000016897 is used only to cross-reference c.681G>A / rs4244285 / *2 nomenclature; its cached summary has no response classification. *2 alone is not a full genotype. The recommendation records are filtered to intermediate/poor metabolizer and the stated ACS/PCI context. No patient genotype or advice is produced, and this evidence is not linked to curcumin or PTGS2.

## Slide 8 — Explanation and prioritisation

For global model behaviour, grouped permutation importance measures ROC-AUC drops on the held-out set; it describes model reliance, not mechanism. A query returns structure properties, nearest measured training examples, similarity and exact training overlap. Curcumin is in the training set, so its output is explicitly retrospective. There is no composite evidence ranking: similarity is a diagnostic only, while identity, ethnobotany, measured activity and PGx remain distinct. The uncalibrated model-only triage value is withheld outside the empirical reference range.

## Slide 9 — Demonstration

In the live prototype, I’ll move from the plant evidence page to the compound explorer, inspect an assay record and structure descriptors, submit a SMILES query, check its similarity and training overlap, and then traverse the evidence graph. The model metrics and data provenance are available in the app, and the processed table can be downloaded. The application is running from the project source and data pipeline, not a static slide mock-up.

## Slide 10 — Impact and next steps

KAPPA demonstrates one reproducible way to connect chemical and bioactivity evidence without turning a database association into a therapeutic claim. The next scientific steps are primary-source ethnobotanical evidence with appropriate provenance, rights and community context; a genuinely independent or prospectively blinded PTGS2 assay evaluation; current CPIC evidence monitoring; expert applicability-domain review; and experimental follow-up. Our result today is not a drug candidate. It is a transparent, runnable research workflow that helps teams decide what evidence exists—and what experiment should come next.
