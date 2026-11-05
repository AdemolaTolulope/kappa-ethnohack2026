# Historical metric discrepancy: ROC-AUC 0.832 / PR-AUC 0.966 vs audited 0.7819 / 0.9396

Status: **investigated 2026-11-05; cause not recoverable from this repository; audited primary retained.**

## 1. The discrepancy

| Pair | ROC-AUC | PR-AUC | Where it comes from |
|---|---|---|---|
| Historical | 0.832 | 0.966 | Quoted earlier in the project. No script, config, log or report file in this repository produces or records it. |
| Audited primary | 0.7819 | 0.9396 | `results/reports/model_metrics.json`, produced by `python -m src.run_pipeline` (pre-registered scaffold-group holdout, fixed seed 17, fold 0, 2,462 train / 702 test, test prevalence 0.8262). |

Both pairs were computed on the same curated file that exists today (`data/processed/ptgs2_curated.csv`,
3,164 structures: 2,505 active ≤1 µM, 659 inactive ≥10 µM), because no other curated version exists in the
repository or in its git history. The two pairs therefore differ in **protocol**, not in data — or the
historical pair was produced from data that is no longer in the repository.

## 2. What was tested

`scripts/diagnose_historical_metrics.py` re-runs the identical featuriser (`src.chemistry.features.feature_vector`),
model factory (`src.ml.train.random_forest`) and curation filters under seven protocols, and reports each
against the historical pair. Output: `results/reports/historical_metric_diagnosis.json`. The primary analysis is
read, never written.

| Candidate explanation | ROC-AUC | PR-AUC | ΔROC vs 0.832 | ΔPR vs 0.966 |
|---|---|---|---|---|
| A. Random stratified 80/20 split, no scaffold grouping (analogue leakage; 223 shared scaffolds across the split) | 0.9270 | 0.9763 | +0.0950 | +0.0103 |
| B. Every fold of the fixed 5-fold scaffold-group split | 0.7819 / 0.7959 / 0.8023 / 0.8392 / 0.8589 | 0.9396 / 0.9277 / 0.9302 / 0.9399 / 0.9554 | best fold +0.0269 | best fold −0.0106 |
| C. Scaffold split, no exact-structure deduplication (3,661 measurement rows) | 0.8140 | 0.9517 | −0.0180 | −0.0143 |
| D. Grey band (1–10 µM) relabelled inactive instead of dropped (5,035 measurement rows, 1,374 grey-band rows) | 0.7416 | 0.7732 | −0.0904 | −0.1928 |
| E. Pooled out-of-fold predictions across the five scaffold folds (n = 3,164) | 0.8194 | 0.9400 | −0.0126 | −0.0260 |
| F. Random 80/20 split on the non-deduplicated frame (the same structure's measurement rows can land on both sides) | 0.8979 | 0.9698 | +0.0659 | +0.0038 |
| G. One arbitrary scaffold-group 80/20 split, seed sweep (12 seeds) | range 0.8039 – 0.8797 | range 0.9202 – 0.9704 | closest seed (6): 0.8416, Δ +0.0096 | closest seed (6): 0.9650, Δ −0.0010 |

(C and F both keep duplicate measurement rows; only F splits them at random rather than by scaffold.)

## 3. Findings

1. **No tested protocol reproduces the historical pair exactly.** No data version, split, dedup rule, label rule
   or aggregation rule available in this repository yields 0.832 / 0.966.
2. **The pair is inside the sampling distribution of a single, arbitrary scaffold split.** Across 12 unpacked
   80/20 scaffold-group splits of the same data, ROC-AUC spans 0.804 – 0.880 and PR-AUC spans 0.920 – 0.970.
   The historical pair (0.832, 0.966) sits comfortably inside that cloud; the closest split (seed 6) gives
   0.8416 / 0.9650. This is the **most consistent single explanation**: the historical numbers look like one
   favourable split, not a pre-registered one.
3. **Leakage explains the high PR but not the ROC.** A random split inflates PR-AUC toward 0.97 but pushes ROC-AUC
   to 0.93, i.e. 0.09 *above* the historical value. So "we accidentally used a random split" is ruled out as the
   cause of *this particular pair*.
4. **The sensitivity variants move in the wrong direction.** Removing dedup (C) or relabelling the grey band (D)
   lowers both metrics; the wider 1 µM cut with 5,035 rows collapses PR-AUC to 0.773, which is nothing like 0.966.
5. **A metric-name mix-up remains possible but is unverifiable.** With active prevalence 0.83, threshold-based
   PR-ish numbers in this project land near 0.83–0.87 (e.g. precision_at_0.5 = 0.870, recall_at_0.5 = 0.947, and
   0.8318 and 0.8327 appear as fold-level precision/recall values in the CV and hyperparameter sweep). Reading 0.832 off a
   table of ROC-AUC values would require the ROC column itself, so this is noted only as an unresolved
   possibility, not a finding.

## 4. Decision

- **The audited primary result is retained**: ROC-AUC 0.7819, PR-AUC 0.9396, balanced accuracy 0.6372,
  MCC 0.3449, Brier 0.1284 on the pre-registered scaffold-group holdout. No number in the app, deck, docs or
  bundle was changed to match the historical pair.
- **The historical 0.832 / 0.966 pair is withdrawn** from every artefact under our control (it appears nowhere in
  the repository except this document and the diagnosis script's input constant).
- **No verified error was found** in the audited evaluation that would justify adopting 0.832 / 0.966.

## 5. What this means for the claim set

The difference is a *reporting-protocol* difference of roughly 0.05 ROC-AUC / 0.03 PR-AUC in the direction of
optimism. It reinforces the project's existing position: a single scaffold holdout is a noisy estimate of
generalisation, which is why `docs/model_card.md` reports the 3-fold training-only scaffold CV (0.7931 ± 0.0387)
and the internal publication- and time-held-out stress tests (0.7235 and 0.6022) alongside it, and why the deck
quotes 0.782 rather than a "best" split. Numbers selected by looking at the evaluation are not evidence.

## 6. Reproduce

```bash
python scripts/diagnose_historical_metrics.py     # ~60 s, writes results/reports/historical_metric_diagnosis.json
python -m src.run_pipeline                        # regenerates the audited primary (unchanged)
```
