# Technical assessment of the KAPPA repository

Independent inspection performed 2026-11-05, before any further modification. Nothing was rebuilt; the
existing modules were executed, exercised through the API and browser, and read line by line where a
claim depended on them. Status vocabulary: **functional** (executes and its output is used),
**partial** (executes but with a documented scope limit), **stub/documentation-only** (no computational
behaviour), **removed** (deleted because it misrepresented evidence).

## 1. Inventory and status

| Area | Files | Status | What it actually does | Evidence |
|---|---|---|---|---|
| Data acquisition | `src/data_pipeline.py::fetch` | functional (cached) | Paginates ChEMBL `activity.json` for CHEMBL230, IC50, nM; writes JSONL with 15 provenance fields | `data/raw/chembl_ptgs2_ic50.jsonl`, 7,482 rows |
| Curation | `src/data_pipeline.py::curate` | functional | Exact-relation, nM, single-protein (`assay_type=='B'`), human, no duplicate/validity flag, grey band 1–10 µM dropped, RDKit canonicalisation, exact-structure dedup keeping lowest IC50 | `results/reports/data_quality.json`, 3,164 structures |
| Curation audit | `audit_dataset` | functional | Ordered, non-overlapping sequential exclusions plus separate missingness counts | `results/tables/filter_counts.csv` |
| Chemistry | `src/chemistry/features.py` | functional | RDKit validation, canonical SMILES, 7 descriptors, 512-bit Morgan r=2, Bemis–Murcko scaffold | used by model and API |
| ML training | `src/ml/train.py` | functional | Scaffold-group holdout, training-only 3-fold CV, 4-point hyperparameter sensitivity, document- and time-held-out stress tests, calibration diagnostics, permutation importance, applicability reference, joblib bundle | `results/reports/model_metrics.json` |
| Duplicate sensitivity | `src/ml/duplicate_sensitivity.py` | functional (**new this session**) | Three aggregation rules under identical protocol, plus a reproduction check against the stored primary metrics | `results/reports/duplicate_sensitivity.json` |
| Applicability gate | `src/prioritisation/rank.py` | functional | Returns model probability, similarity diagnostic, and the **triage value only inside the empirical range**; lists missing evidence | `/api/predict` returns `null` for sucrose |
| Evidence graph | `src/knowledge_graph/graph.py` | functional (scope-limited) | Typed MultiDiGraph with node/edge provenance; PGx component intentionally disconnected; edge payload separates topology from provenance | `/api/graph`, GraphML export |
| PGx (CPIC) | `src/pharmacogenomics/cpic_demo.py` | functional (scope-limited) | Verifies pair/allele/guideline/recommendations and refuses to write partial records; recommendation rows filtered to intermediates/poor metabolisers and `CVI ACS PCI ` | `data/raw/cpic_cyp2c19_clopidogrel.json` |
| PGx (ClinVar) | `src/pharmacogenomics/clinvar_identity.py` | functional (identity only) | Asserts accession, cDNA change, `*2` alias and rs4244285 cross-reference before caching; carries the germline label *and* its interpretation boundary | `data/raw/clinvar_cyp2c19_star2.json` |
| Ethnobotany | `data/processed/ethnobotanical_claims.json`; `src/ethnobotany/__init__.py` | **documentation-only** | A single attributed, qualified secondary-source record; the Python package is an empty placeholder | claim id `VELAYUDHAN2012-T1-COUGH-COLD` |
| Backend | `backend/main.py` | functional | 11 routes (page, overview, compounds, structure SVG, graph, predict, pharmacogenomics, genomic-context, data-quality, metrics, export) | exercised route-by-route, see §3 |
| Frontend | `frontend/index.html` | functional | Single-file SPA, 8 views, reads only relative `/api/*`, no external CDN | headless-browser pass, 0 console errors |
| Tests | `tests/test_core.py`, `tests/test_api.py` | functional | 17 tests covering curation, splits, gating, graph provenance/topology, PGx filtering, ClinVar semantics, OOD withholding, API behaviour | `pytest -q` → 17 passed |
| Figures | `scripts/make_figures.py`, `src/ml/train.py::_figures` | functional | 10 PNGs regenerated from results | `results/figures/` |
| Deck | `scripts/build_deck.py` | functional | Generates a 10-slide deck; rendered and visually checked this session | `presentation/rendered/` |
| Notebooks | `notebooks/*.ipynb` | partial | Read the executed outputs; they do not retrain models | 6 notebooks |
| Removed | composite scoring | **removed** | Equal-weight evidence average deleted; a test asserts no score outside the empirical range | `tests/test_core.py` |

## 2. Things that were incorrectly represented, and their current state

1. **A single "candidate score" averaged dissimilar evidence types.** Removed; only the uncalibrated model
   probability survives, and only inside the empirical similarity range.
2. **ClinVar was described as carrying no clinical-significance summary.** Wrong: VCV000016897 has
   `germline_classification = "Likely benign; other"` (evaluated 2018-08-07) for traits recorded as
   "not specified"/"not provided". Corrected in code, cache, UI, deck, notebooks and documentation, with a
   test pinning the interpretation (disease-association label ≠ drug-metaboliser function).
3. **Graph edges lost their topology.** `{'source':u,'target':v,**d}` let the provenance field overwrite
   the node id, so every edge looked dangling and the graph view crashed for filtered scopes. Fixed;
   provenance is now `source_reference`, with a regression test.
4. **The compound panel claimed a structure image was "not embedded"** while rendering one, and showed
   sub-nanomolar IC50 values as `0.0`. Both fixed.
5. **Test count and validation statements drifted** between the model card, validation report and audit.
   Reconciled to the executed outputs.

## 3. Executed verification (actual outputs)

```
pytest -q                                        -> 17 passed
python -m src.run_pipeline                       -> raw 7,482; curated 3,164; 2,505 active / 659 inactive
python -m src.ml.duplicate_sensitivity           -> 3 rules scored; primary reproduction check True
curl /api/overview|compounds|metrics|export|graph|pharmacogenomics|genomic-context  -> 200
POST /api/predict (curcumin)                     -> 200, probability 0.150, exact training match
POST /api/predict (sucrose)                      -> 200, max Tanimoto 0.193, candidate_priority_score null
POST /api/predict ("not_a_smiles")               -> 400, "Invalid SMILES string"
headless Chromium, 8 views                       -> 0 console errors, 0 failed requests
```

## 4. Real limitations of the implementation (not cosmetic)

- **One target, one assay family.** Everything quantitative rests on human PTGS2 biochemical IC50 records
  in ChEMBL; no cell-based, phenotypic or organism-level endpoint is modelled.
- **No external validation.** Both stress tests are internal ChEMBL re-splits.
- **Uncalibrated probabilities.** Diagnostics only; no calibration curve is fitted and none is claimed.
- **Ethnobotany is one qualified secondary report**, not a corpus, and `src/ethnobotany/` is a placeholder
  package rather than a parser or ontology mapper. It should be described that way in any write-up.
- **PGx is a demonstration of curated evidence**, not a KAPPA-computed pharmacogenomic prediction.
- **The graph is a demonstration artefact** (72 nodes on the pilot build), not a queryable knowledge base.
- **Deployment is unverified**: the app has only ever run from this sandbox via uvicorn.

## 5. Recommended next engineering steps, in priority order

1. Package the ethnobotany layer properly (parser + source schema + licence check) before adding any
   second record; a one-record module that looks like infrastructure invites overclaiming.
2. Add a second, genuinely independent assay source for the same target to test transportability.
3. Fit and report a calibration model **inside training folds only**, then re-report Brier/ECE.
4. Add `pandera`/`pydantic` schema validation at the data boundary so silent field drift cannot recur.
5. Containerise (`Dockerfile` + pinned requirements) to make the deployment claim verifiable.
