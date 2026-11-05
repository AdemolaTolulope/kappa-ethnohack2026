# Third-party data, software and AI-assisted development disclosure

## AI assistance
AI-assisted development through Arena.ai Agent Mode was used during project continuation to draft/edit code, tests, data documentation, validation/model-card text, submission copy and slide content, and to help analyze pipeline outputs. Human verification remains required for the code, metrics, citations, licenses, and scientific interpretations. The project does not use a remote generative-AI inference service in its running application. Biological observations, publications, associations and validation metrics were not generated or fabricated by the assistant.

## External data and evidence
- **ChEMBL REST / CHEMBL230:** human PTGS2 IC50 assay records, source IDs retained. ChEMBL states its database is CC BY-SA 3.0; attribute and preserve share-alike obligations. Check current terms before redistribution.
- **CPIC API:** gene, *2 allele, clopidogrel pair, guideline and phenotype-specific recommendations; curated content CC0 1.0. CPIC requests attribution, API URL, access date, version, relevant publication and a current-source caveat.
- **NCBI ClinVar E-utilities:** VCV000016897 molecular identity cross-reference for c.681G>A / rs4244285 / *2. Cached ESummary reports a germline classification of 'Likely benign; other' (last evaluated 2018-08-07) with traits 'not specified'/'not provided'. This is a Mendelian disease-association label, not a drug-response classification, and it is not used to contradict CPIC's 'no function' allele assignment.
- **Wikidata Q312266/Q42562:** CC0 structured-data occurrence statement, attributed to Wikidata and subject to statement-reference quality; this is not efficacy.
- **PubChem CID 969516:** structure/identifier cross-reference; not biological efficacy.
- **UniProt P35354:** target identity context; CC BY 4.0 attribution.
- **Velayudhan et al. (2012):** secondary ethnobotanical source. A brief attributed summary is kept with source/context limitations; the underlying Malayalam work was not independently accessed and the paper's reuse licence was not verified. No traditional-knowledge community or locality is inferred.

Full query URLs, access dates, transformations and rights cautions are in `docs/provenance_register.md`.

## Software
RDKit, scikit-learn, FastAPI, NetworkX, Pandas, NumPy, Matplotlib, python-pptx and transitive dependencies retain their own upstream licences. See `requirements.txt`, `LICENSE`, project documentation and upstream notices. No third-party model weights are used; the Random Forest is fit by the included pipeline.

## Original project integration and attribution
The KAPPA-specific data filters, RDKit feature/model workflow, scaffold validation, evidence-aware ranking API, provenance graph, interface and project materials are integrated in this repository; standard libraries and external datasets remain third-party. These are project integrations, not claims of novel algorithms.

Team identities and individual contributions are intentionally left as placeholders pending confirmation. Do not publish the submission page with incomplete or assumed contributor information.
