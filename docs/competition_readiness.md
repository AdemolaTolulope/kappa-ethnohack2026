# Competition readiness against the EthnoHack judging criteria

Assessed 2026-11-05 by evidence in this repository only. Where a criterion is weak, the weakness is stated and
a practical remedy is given. **KAPPA is not declared competition-ready**: two blocking, non-technical gaps
remain (team composition and registration/eligibility; see `docs/release_checklist.md`).

| # | Criterion | Evidence in the repo | Honest weakness | Action taken this cycle |
|---|---|---|---|---|
| 1 | **Scientific relevance** | Problem documented from the primary literature of the field (LOTUS, NPASS, IMPPAT, NP-KG, 2026 compound-centric framework); target and assay provenance retained per record | One target, one assay family; ethnobotany is a single secondary report | `docs/competitive_landscape.md`, `docs/innovation_statement.md` |
| 2 | **Innovation** | Evidence-type contract enforced in API/UI; explicit refusal rule demonstrated on a real out-of-domain molecule; aggregation sensitivity and the withdrawn historical metrics both disclosed | The integration *concept* is published elsewhere; novelty must be described as the enforced contract, not the idea | Innovation statement narrowed to what is novel and lists what is not |
| 3 | **Technical implementation** | 12 API routes, 8 UI views, 21 tests, RDKit/scikit-learn/NetworkX, typed graph with provenance, no external runtime calls | No container, no CI, no public deployment | Technical assessment written; defects (graph keys, OOD gate, UI overlaps, AD wording, SMILES overwrite) fixed and tested; ethnobotany now has a fail-closed validator, not a placeholder |
| 4 | **Data-science quality** | Scaffold-group holdout, training-only CV, two internal stress tests, calibration diagnostics, applicability reference, permutation importance, duplicate-aggregation sensitivity with a reproduction check, **7-protocol diagnosis of the withdrawn 0.832/0.966 metrics** | No external validation; uncalibrated probabilities; single-split threshold metrics shown to be unstable | Sensitivity analysis implemented and reported; the instability is stated, and the unreproducible historical pair is withdrawn with evidence (`docs/historical_metric_discrepancy.md`) |
| 5 | **Feasibility** | Cached acquisition, deterministic pipeline, 13 MB bundle that reproduces to 1e-16, runs offline | Live re-acquisition path is untested this cycle; deployment unverified | Bundle verified by clean-room extraction |
| 6 | **Potential impact** | A researcher can go from plant → compound → measured records → model estimate → missing evidence in one screen; outputs explicitly say what to check next | No user study; no measured time-to-answer | Next-step list added to the demo script and limitations |
| 7 | **Presentation quality** | 10-slide deck rendered and visually corrected; demo/narration scripts; disclosure and provenance appendices | Video not recorded; deck fonts substitute Carlito for Aptos until rendered on a machine with Aptos | Five layout defects fixed after rendering; slide 10 no longer implies a completed submission |

## Where KAPPA would lose points, and what would fix it

1. **No external validation** (criteria 1 and 4). The single most persuasive addition would be scoring one
   genuinely independent PTGS2 IC50 source with no shared publications or structures. Nothing else moves the
   scientific score as much.
2. **No calibration** (criterion 4). Fitting calibration inside training folds and reporting holdout Brier/ECE
   would let the interface say "about X% of similarly-predicted molecules were active" without overclaiming.
3. **Thin ethnobotanical layer** (criteria 1 and 6). One record is a demonstration, not a corpus. The validator
   is real (required provenance, refusal of compound linkage, 3 tests) but a second and third independent,
   properly licensed source with locality/community attribution is what would materialise this angle.
4. **Unverified deployment** (criterion 5). A container plus a hosted URL would make the "working workbench"
   claim checkable by a judge in one click.

## What is genuinely strong

- The **refusal rule** is unusual and demonstrable: an out-of-reference molecule returns `null`, in the API and
  in the UI, and a test enforces it.
- The **out-of-domain refusal is visible, not asserted**: an out-of-reference molecule shows "Not rankable ·
  probability withheld" with the similarity diagnostic and the reason, while an in-domain molecule still gets a
  number — both verified in a headless browser this session.
- The **aggregation sensitivity** — 371 structures with multiple measurements, 32 structurally ambiguous
  structures, three rules compared under one protocol with an exact reproduction check — is the kind of
  diligence judges rarely see in a weekend project.
- The **PGx module** does not pretend: a real CPIC guideline, filtered to the intended phenotype and population
  context, kept disconnected from the phytochemical pilot, with the ClinVar label explained correctly.
- Everything quantitative can be regenerated from the bundle in minutes.

## Recommendation

Submit, but submit *as* what it is: a reproducible evidence-contract workbench with one honest benchmark, not
as a validated discovery engine. Put the refusal rule and the aggregation sensitivity in the first two minutes
of the video; they are the parts a scientific judge cannot get from a database screenshot.
