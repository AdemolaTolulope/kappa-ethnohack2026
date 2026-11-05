# Interface smoke-test screenshots

Captured 2026-11-05 with headless Chromium (Playwright) against `uvicorn backend.main:app`
on the cached ChEMBL/CPIC/ClinVar data. Every view rendered, the prediction, out-of-domain,
prioritisation, graph-scope and PGx flows returned data, and the run produced 0 console
errors and 0 failed requests.

These are interface-verification artefacts. They are not independent scientific validation,
and the screenshots do not substitute for a human visual review before release.

| File | View |
|---|---|
| `overview.png` | Research overview |
| `ethnobotany.png` | Plant & knowledge explorer |
| `compounds.png` | Compound explorer with an auto-selected structure |
| `prediction.png` | Compound explorer after a curcumin SMILES submission |
| `genomics.png` | Genomic context / CPIC CYP2C19–clopidogrel panel |
| `ml.png` | Machine-learning laboratory metrics |
| `graph.png` | Evidence graph, plant & assay scope |
| `graph_pgx.png` | Evidence graph, pharmacogenomics scope |
| `rank.png` | Candidate prioritisation (empty state) |
| `prioritisation_run.png` | Candidate prioritisation after a curcumin submission |
| `methods.png` | Methods & evidence |
| `overview_820.png` | Overview at 820 px width (collapsed icon navigation) |

Duplicated filenames from the first capture pass (`compound_explorer`, `plant_and_knowledge`,
`genomic_context`, `ml_laboratory`, `evidence_graph`, `methods_and_evidence`) were removed so
each view has one current screenshot.
