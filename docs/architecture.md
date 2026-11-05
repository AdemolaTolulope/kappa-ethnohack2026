# Architecture

```text
ChEMBL REST -> raw JSONL cache -> explicit curation -> RDKit features
                                                   -> scaffold holdout/CV + stress tests
                                                   -> metrics, model artifact, figures
                                                   -> FastAPI prediction/evaluation endpoints

Wikidata occurrence + secondary ethnobotanical claim + measured ChEMBL activity
     -> separate typed evidence records -> plant/assay NetworkX component -> SVG graph/UI

CPIC API gene/allele/drug/guideline/recommendations + ClinVar identity cross-reference
     -> phenotype/population-filtered evidence -> disconnected PGx graph component/UI

All sources -> provenance register / audit / model card / submission drafts
```

Python modules separate retrieval and cleaning (`src/data_pipeline.py`), chemistry (`src/chemistry`), training/evaluation (`src/ml`), provenance graph (`src/knowledge_graph`), evidence profile (`src/prioritisation`) and API (`backend`). The lightweight frontend is inline HTML/CSS/JavaScript and does not require a CDN. Cached JSONL/CSV/JSON is sufficient at pilot scale; SQLite/PostgreSQL is not added without a concrete multi-user requirement.

Main routes include `/api/overview`, `/api/compounds`, `/api/predict`, `/api/graph?scope=pilot|pharmacogenomics|all`, `/api/pharmacogenomics`, `/api/genomic-context`, `/api/metrics`, `/api/data-quality` and `/api/export`. The graph scope filter makes the pharmacogenomic demonstration explicitly disconnected from plant and assay records.

Run from the repository root. The server should bind to `0.0.0.0` for preview/deployment compatibility. The UI must use relative URLs through the serving origin.
