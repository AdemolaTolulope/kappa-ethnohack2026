# Scientific integrity audit — 2026-11-05

Scope: independent check of the current KAPPA repository against its own documentation. Every number below
was produced by a command in this session; the command is given so it can be re-run. Discrepancies found are
reported, not silently fixed, and the resolution of each is stated.

## 1. Duplicate-structure aggregation sensitivity (new analysis)

Command: `python -m src.ml.duplicate_sensitivity` (≈35 s) → `results/reports/duplicate_sensitivity.json`,
`results/figures/duplicate_sensitivity.png`.

Eligible measurements before deduplication: **5,035 records / 4,327 unique canonical structures**;
**371** structures have more than one eligible measurement; **32** structures carry both an active
(≤1 µM) and an inactive (≥10 µM) measurement.

Identical protocol for all three rules: same eligibility filters, Bemis–Murcko scaffold groups, first fold of
`StratifiedGroupKFold(n_splits=5, shuffle=True, seed=17)`, random forest (350 trees, `min_samples_leaf=2`,
`class_weight='balanced'`, `max_features='sqrt'`, seed 17), plus a 3-fold scaffold CV (seed 29).

| Aggregation rule | Structures | Active / inactive | Prevalence | Train / test | Test prevalence | Holdout ROC-AUC | Holdout PR-AUC | Balanced acc. | MCC | 3-fold CV ROC-AUC (mean ± SD) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Lowest IC50 (**primary, unchanged**) | 3,164 | 2,505 / 659 | 0.792 | 2,462 / 702 | 0.826 | **0.7819** | **0.9396** | 0.6372 | 0.3449 | 0.7931 ± 0.0387 |
| Median IC50 | 3,084 | 2,417 / 667 | 0.784 | 2,443 / 641 | 0.791 | 0.7744 | 0.9232 | 0.6707 | 0.3996 | 0.7963 ± 0.0579 |
| Conflicting structures excluded | 3,068 | 2,410 / 658 | 0.786 | 2,604 / 464 | 0.774 | 0.8250 | 0.9267 | 0.7286 | 0.4636 | 0.8052 ± 0.0149 |

**Reproduction check.** The lowest-IC50 rule is executed through the same `curate()` code path as the
reported primary result, and the audit asserts agreement with `results/reports/model_metrics.json`:
ROC-AUC, PR-AUC and balanced accuracy reproduce to absolute difference **0.0** (`reproduced_within_1e-9: true`).

**What this means, and what it does not.**
- Ranking performance is *moderately* stable: holdout ROC-AUC spans 0.774–0.825 and PR-AUC 0.923–0.940 across
  rules. PR-AUC must be read against prevalence (0.77–0.83), where the no-skill baseline is the prevalence itself.
- The **threshold-0.5 operating point is not stable**: balanced accuracy moves 0.637 → 0.729 and MCC
  0.345 → 0.464 depending on how duplicates are handled. Any claim about "how many compounds we would
  correctly triage" is therefore fragile and is not made anywhere in this project.
- The exclusion rule looks strongest partly because it removes 32 genuinely ambiguous structures and shrinks
  the test set to 464 structures; the 3-fold CV means overlap within one SD, so the difference is not
  established. It is not adopted as the primary analysis.
- Because each rule has its own structure set, each gets its own fold assignment; a paired comparison on a
  common subset was **not** performed and is listed as future work.

## 1b. Historical metric discrepancy: 0.832 / 0.966 vs 0.7819 / 0.9396 (Priority C)

Command: `python scripts/diagnose_historical_metrics.py` (≈60 s) → `results/reports/historical_metric_diagnosis.json`.
Full write-up: [`historical_metric_discrepancy.md`](historical_metric_discrepancy.md).

Seven protocols were scored against the historical pair, using the same featuriser, model factory and curation
filters as the primary analysis. None reproduces it.

| Protocol | ROC-AUC | PR-AUC |
|---|---|---|
| Audited primary (retained) | 0.7819 | 0.9396 |
| Random stratified split, no grouping (leakage) | 0.9270 | 0.9763 |
| Scaffold folds 0–4 | 0.7819 / 0.7959 / 0.8023 / 0.8392 / 0.8589 | 0.9396 / 0.9277 / 0.9302 / 0.9399 / 0.9554 |
| Scaffold split, no exact-structure dedup | 0.8140 | 0.9517 |
| Grey band relabelled inactive (5,035 rows) | 0.7416 | 0.7732 |
| Pooled out-of-fold, 5 folds | 0.8194 | 0.9400 |
| Random split, duplicates kept | 0.8979 | 0.9698 |
| One arbitrary scaffold split, 12 seeds | 0.8039 – 0.8797 | 0.9202 – 0.9704 |

Findings: the historical pair lies **inside** the spread of a single arbitrary scaffold split (closest seed 6 →
0.8416 / 0.9650), which is the most consistent explanation — one favourable, non-pre-registered split. Leakage
produces the high PR-AUC but overshoots ROC-AUC by 0.09, so it is ruled out as the cause of *this* pair. The
decision is recorded as: **audited primary retained, historical pair withdrawn, no verified error found.** No
number in the app, deck, docs or bundle was altered to match the historical figure.

## 2. Applicability domain: a real out-of-domain control

Threshold (training-only, from the stored model bundle): **0.3235867** (5th percentile of max Morgan r2
Tanimoto for training-only scaffold out-of-fold molecules against their fold training set).

Control compound: sucrose (disaccharide, far from the drug-like PTGS2 assay chemistry).
Computed similarity against the training partition: **0.1930** — below threshold.

Live API response (`POST /api/predict`, recorded in `results/reports/out_of_domain_control.json`):

```
max_training_similarity     0.19298245614035087
in_domain                   False
candidate_priority_score    null
applicability status        "outside empirical reference range or unavailable"
chemical identity           "structure syntax validated only; named identity unconfirmed"
measured bioactivity        "not found in loaded subset; not evidence of inactivity"
```

The UI renders "Not rankable", the 42.6% uncalibrated probability, and the Tanimoto 0.193 diagnostic
(`results/smoke/rank_out_of_domain.png`). **The gate is real behaviour, not a slogan.**

Borderline caveat: stearic acid scores Tanimoto 0.325, which sits just *above* the empirical threshold and is
therefore triaged (0.590). The threshold is an empirical 5th-percentile reference, not a validated domain
boundary, and near-threshold behaviour should be read that way.

## 3. Reproducibility

| Check | Command | Result |
|---|---|---|
| Test suite | `pytest -q` | **21 passed** |
| Full pipeline | `python -m src.run_pipeline` | 7,482 raw → 3,164 curated (2,505 / 659); metrics, figures and GraphML regenerated |
| Clean-room extraction | unzip the rebuilt `submission/KAPPA_ethnohack2026_bundle.zip` (126 files) in an empty dir | **21 passed**; pipeline reproduced stored metrics to ≤1.2e-16 |
| Historical-metric diagnosis | `python scripts/diagnose_historical_metrics.py` | 7 protocols scored; none reproduces 0.832 / 0.966; primary unchanged (§1b) |
| Ethnobotany validation | `python -m src.ethnobotany` and `GET /api/ethnobotany` | coverage note + 1 validated record; validator rejects records that assert compound linkage |
| Sensitivity analysis | `python -m src.ml.duplicate_sensitivity` | primary reproduction check True |
| Live app | `uvicorn backend.main:app` | all routes 200/expected; invalid SMILES → 400 |

## 4. Consistency across artefacts

Checked: `docs/model_card.md`, `docs/validation_report.md`, `README.md`, `frontend/index.html`,
`presentation/KAPPA_pitch_deck.pptx`, `submission/*`, notebooks.

- Test count: the audit, validation report, technical assessment and readiness docs now all state 21 (17 before the AD/ethnobotany additions).
- Metrics quoted in the deck, README, model card and app match `model_metrics.json` (ROC 0.7819 → 0.782,
  PR 0.9396 → 0.940, balanced accuracy 0.6372 → 0.637, prevalence 0.8262 → 82.6%).
- ClinVar: all artefacts now describe the "Likely benign; other" germline label and its boundary; none of them
  claims the record carries no significance summary (this was wrong before 2026-11-05).
- The deck's "delivered" slide previously implied a completed submission; it now says "working API + UI
  (local) … 10-slide deck + rendered PDF".
- The earlier overstatement that `src/ethnobotany/` was "an empty package" is now historical: the package exists
  and validates the record fail-closed (Priority B). `docs/technical_assessment.md` §4 is updated accordingly.
- The bundle zip in `submission/` predates the AD/ethnobotany changes and is untracked; it must be regenerated
  before it is offered as the portable copy.

## 5. Security and identity

- No credentials, tokens, private keys or personal data found: `grep` for `API_KEY|SECRET|password|token`
  returns nothing; `.env.example` contains only `KAPPA_DATA_DIR=data`.
- No external calls at request time: the app reads cached ChEMBL/CPIC/ClinVar/UniProt files; outbound
  requests happen only in explicit fetch scripts.
- `submission/team_contributions.md` is an **empty template**. Contributor identities are unconfirmed and must
  not be fabricated.
- No telemetry, analytics, cookies or tracking in the frontend; no CDN dependencies.

## 6. Data provenance summary

| Dataset | Source and date | Licence and obligations |
|---|---|---|
| ChEMBL PTGS2 IC50 | ChEMBL REST, target CHEMBL230, cached 2026-11-05 | CC BY-SA 3.0; attribution and share-alike; verify current terms |
| CPIC CYP2C19–clopidogrel | `api.cpicpgx.org`, cached 2026-11-05 | CC0 1.0; CPIC asks for attribution, version, access date and current-source caveat |
| ClinVar VCV000016897 | NCBI E-utilities ESummary, cached 2026-11-05 | Public domain-style NCBI terms; identity cross-reference only |
| UniProt P35354 | UniProt REST, cached 2026-11-05 | CC BY 4.0 attribution |
| Wikidata Q312266 / Q42562 | P703 occurrence triple, checked 2026-11-05 | CC0 |
| Ethnobotanical report | Velayudhan et al. 2012, IJTK 11(4):607–614 | Cited, not reproduced; underlying Malayalam source unverified |

Full register: `docs/provenance_register.md`, `docs/data_provenance.md`, `submission/third_party_disclosures.md`.

## 7. Claims explicitly *not* supported by this audit

External or prospective validation; clinical utility or individual response prediction; efficacy or safety of
curcumin or any plant; a curcumin–PTGS2 pharmacogenomic relationship; calibrated probabilities; a validated
applicability boundary; a curated ethnobotanical corpus; completion of the EthnoHack submission.

## 8. Residual risks and next actions

1. Paired, common-subset comparison of aggregation rules (removes split-assignment noise).
2. Calibration fitted inside training folds, reported on holdout, before any probability is described as a risk.
3. A second independent assay source for the same target, to test transportability honestly.
4. ~~Package or remove the placeholder ethnobotany module~~ — **done** (Priority B): `src/ethnobotany/` validates
   records fail-closed. Next step is corpus scope, not packaging: a licence-cleared second and third record with
   the same field discipline before any coverage claim is made.
5. Rebuild the release bundle after the AD/ethnobotany changes and re-run the clean-room check (the current zip
   predates them).
6. Human sign-off by a team member on every quantitative claim before submission.
