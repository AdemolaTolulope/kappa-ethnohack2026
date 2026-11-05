# Release checklist — EthnoHack 2026 submission

Status as of **2026-11-05**. Only items marked DONE have been executed and verified in this workspace.
Everything under OPEN requires a human decision, a human credential, or a human judgement and must not be
described as complete before it actually happens.

## DONE (verified in this workspace)

- [x] Cached ChEMBL PTGS2 acquisition (7,482 raw records) and curated dataset (3,164 unique structures; 2,505 active, 659 inactive).
- [x] Scaffold-group holdout (2,462 train / 702 test, no scaffold overlap), training-only StratifiedGroupKFold CV, internal document- and time-held-out stress tests.
- [x] Uncalibrated probability diagnostics (Brier 0.1284, ECE 0.1198) and training-only empirical applicability reference (max Tanimoto 0.3235867).
- [x] Composite evidence score removed; separate evidence axes (identity, measured activity, occurrence, secondary report, PGx) preserved.
- [x] CPIC CYP2C19–clopidogrel demonstration cached with phenotype/`CVI ACS PCI` population filtering; ClinVar VCV000016897 cached as a molecular-identity cross-reference including its "Likely benign; other" germline label and its interpretation boundary.
- [x] `pytest -q` → 17 passed (includes duplicate-aggregation rules and out-of-domain withholding).
- [x] Duplicate-structure aggregation sensitivity run (lowest / median / conflicting-excluded) with an exact reproduction check of the primary result.
- [x] Out-of-domain control verified end-to-end: sucrose max Tanimoto 0.193 below the 0.3236 reference, triage value withheld by API and UI.
- [x] Competitive landscape, technical assessment, scientific integrity audit, innovation statement and this readiness assessment written from cited sources and executed commands.
- [x] Running FastAPI app exercised route-by-route; live headless-Chromium pass over all eight views with 0 console errors and 0 failed requests (screenshots in `results/smoke/`).
- [x] Documentation set reconciled: methodology, architecture, research gap, responsible AI, limitations, model card, provenance register, data provenance, phase-11 audit, validation report, research data README.
- [x] 10-slide deck rebuilt and rendered to `presentation/rendered/` (PDF + 10 slide PNGs); four layout defects found in the render and fixed.
- [x] Submission copy drafted: Devpost description, pitch script, demo script, video narration, team-contribution template, third-party disclosure.
- [x] Local git repository initialised with the current tree committed.
- [x] Self-contained bundle built at `submission/KAPPA_ethnohack2026_bundle.zip` (110 files, 13.2 MB; includes cached data, model, figures, rendered deck and screenshots) and verified by extracting it to an empty directory, where `pytest -q` passed and `python -m src.run_pipeline` reproduced the stored metrics to floating-point round-off.

## Deliverables index (requested set)

| # | Deliverable | Where |
|---|---|---|
| 1 | Problem statement | `docs/innovation_statement.md` §1 |
| 2 | Innovation statement | `docs/innovation_statement.md` §3 |
| 3 | Competitive landscape analysis | `docs/competitive_landscape.md`, `docs/research_gap.md` |
| 4 | Technical architecture | `docs/architecture.md`, `docs/technical_assessment.md` |
| 5 | Verified scientific workflow | `docs/scientific_methodology.md`, `docs/technical_assessment.md` §3 |
| 6 | Functional demonstration | running app; `results/smoke/`, `submission/demo_script.md` |
| 7 | Reproducible results | `results/reports/`, `results/figures/`, `submission/KAPPA_ethnohack2026_bundle.zip` |
| 8 | Independent validation report | `docs/scientific_integrity_audit.md`, `docs/validation_report.md` |
| 9 | README and documentation | `README.md`, `docs/` |
| 10 | Public repository release checklist | `docs/github_release_checklist.md` |
| 11 | 10-slide pitch deck | `presentation/KAPPA_pitch_deck.pptx`, rendered in `presentation/rendered/` |
| 12 | ≤10-minute pitch script | `submission/pitch_script.md` (~6.6 min spoken), `submission/video_narration.md` |
| 13 | Devpost submission draft | `submission/devpost_description.md` |
| 14 | Data/software/licence disclosure | `submission/third_party_disclosures.md`, `docs/provenance_register.md` |
| 15 | Unresolved limitations and blockers | this section and `docs/limitations.md`, `docs/competition_readiness.md` |

## OPEN — must be completed by the team

1. **Team composition (blocking).** The rules require 2–5 members. `submission/team_contributions.md` is a template: each member's role and contribution must be written by the people involved, not invented. A solo submission is not compliant as written.
2. **Registration / eligibility (blocking, verify with organisers).** The Devpost landing page lists registration as closed on 2026-10-31 and describes the event as students-only, while the rules page lists broader participant categories. Confirm in writing with the organisers whether this team can submit and whether a late registration path exists before investing further in video production.
3. **Public source repository (blocking).** A public repo URL is required. The workspace is a local git repository only — it has no remote and no credentials, so nothing has been pushed. Steps: create the remote, add it, push, then confirm the README, licence, data-source documentation and third-party disclosures are visible on the public page.
4. **Deployment URL (if the submission form asks for one).** The app currently runs only in this sandbox (`uvicorn backend.main:app`). A public deployment needs hosting, and the host must allow outbound calls only to the already-cached sources (the running app reads caches; it does not need live ChEMBL access).
5. **Pitch video ≤ 10 minutes (blocking).** Not recorded. `submission/video_narration.md` and `submission/demo_script.md` are the script; the recorded cut must match what the app actually does, keep the "internal benchmark, not clinical" framing, and show the PGx panel as a disconnected demonstration.
6. **Deck ownership check.** The rendered deck is clean, but it was rendered with Carlito substituting for Aptos. Open it once in PowerPoint/Keynote (or install Aptos) before recording.
7. **Devpost submission (blocking).** Not submitted. Requires everything above.
8. **Public-repository release steps** are itemised in `docs/github_release_checklist.md`; nothing has been pushed and no remote exists.
9. **Human sign-off on claims.** One person should read `docs/model_card.md`, `docs/limitations.md` and `docs/responsible_ai.md` end to end and confirm every number in the deck and scripts still matches `results/reports/model_metrics.json`. Model and data claims were verified here, but accountability for the submission rests with the team.

## Deliberately not claimed anywhere in this project

External/prospective validation, patient or clinical utility, efficacy or safety of curcumin or any plant,
a curcumin–PTGS2 pharmacogenomic relationship, calibrated probabilities, a bioavailable or therapeutically
meaningful natural-product formulation, or first-in-field novelty for the ML, knowledge-graph or
ethnobotanical components.

## Reproduction commands

```bash
python -m pip install -r requirements.txt
python -m src.run_pipeline          # uses the cached acquisition; regenerates data, model, metrics, figures, graph
pytest -q                           # expect 17 passed
uvicorn backend.main:app --host 0.0.0.0 --port 8000
python scripts/make_figures.py      # regenerate result figures
python scripts/build_deck.py        # regenerate the 10-slide deck
soffice --headless --convert-to pdf --outdir presentation/rendered presentation/KAPPA_pitch_deck.pptx
```
