"""Diagnose the historical 0.832 / 0.966 metric report against the audited primary result.

The project previously reported ROC-AUC 0.832 and PR-AUC 0.966. The audited primary evaluation on the
same curated data gives 0.7819 / 0.9396. This script tests the plausible explanations that are
recoverable from the data currently in the repository:

  A. random stratified split (no scaffold grouping) — analogue leakage across splits;
  B. every fold of the fixed scaffold-group holdout;
  C. scaffold-group holdout without exact-structure deduplication;
  D. scaffold-group holdout on a wider activity threshold (active <=1 uM vs inactive >1 uM, grey band kept);
  E. pooled out-of-fold predictions across the five scaffold folds;
  F. random split on the non-deduplicated frame (same analogue twice, once in each split);
  G. spread of a single arbitrary scaffold-group train/test split over many seeds (was the historical pair
     simply one favourable, non-pre-registered split?).

It reports what reproduces the historical numbers and what does not. It does not modify any primary result.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold, train_test_split

from src.chemistry.features import feature_vector, scaffold
from src.ml.train import random_forest


def load():
    df = pd.read_csv('data/processed/ptgs2_curated.csv')
    df['scaffold'] = df['canonical_smiles'].map(scaffold)
    X = np.vstack(df['canonical_smiles'].map(feature_vector))
    return df, X


def score(Xtr, ytr, Xte, yte, seed=17):
    m = random_forest(seed=seed)
    m.fit(Xtr, ytr)
    p = m.predict_proba(Xte)[:, 1]
    return {'roc_auc': float(roc_auc_score(yte, p)), 'pr_auc': float(average_precision_score(yte, p)),
            'test_n': int(len(yte)), 'test_prevalence': float(np.mean(yte))}


def main():
    df, X = load()
    y = df['label'].to_numpy()
    groups = df['scaffold'].to_numpy()
    out = {'historical_report': {'roc_auc': 0.832, 'pr_auc': 0.966,
                                 'note': 'numbers quoted earlier in the project; origin not recorded in this repository'},
           'audited_primary': {'roc_auc': 0.7819, 'pr_auc': 0.9396,
                               'source': 'results/reports/model_metrics.json'}}

    # A. random stratified split, no grouping
    tr, te = train_test_split(np.arange(len(y)), test_size=0.2, random_state=17, stratify=y)
    out['random_stratified_split_no_grouping'] = score(X[tr], y[tr], X[te], y[te])
    out['random_stratified_split_no_grouping']['scaffold_overlap_between_splits'] = int(
        len(set(groups[tr]) & set(groups[te])))

    # B. every fold of the fixed scaffold-group holdout
    folds = {}
    for i, (a, b) in enumerate(StratifiedGroupKFold(5, shuffle=True, random_state=17).split(X, y, groups)):
        folds[f'fold_{i}'] = score(X[a], y[a], X[b], y[b])
        folds[f'fold_{i}']['scaffold_overlap'] = int(len(set(groups[a]) & set(groups[b])))
    out['scaffold_group_holdout_folds'] = folds

    # C. no exact-structure dedup: rebuild labelled records without collapsing duplicates
    from src.ml.duplicate_sensitivity import eligible_measurements, label_from_ic50
    rows = [json.loads(x) for x in Path('data/raw/chembl_ptgs2_ic50.jsonl').read_text().splitlines() if x.strip()]
    full = eligible_measurements(rows)          # every eligible measurement row, grey band included
    raw = full.copy()
    raw['label'] = raw['ic50_nM'].map(label_from_ic50)
    raw = raw.dropna(subset=['label']).copy()
    raw['label'] = raw['label'].astype(int)
    Xr = np.vstack(raw['canonical_smiles'].map(feature_vector))
    yr = raw['label'].to_numpy()
    gr = raw['canonical_smiles'].map(scaffold).to_numpy()
    a, b = next(iter(StratifiedGroupKFold(5, shuffle=True, random_state=17).split(Xr, yr, gr)))
    out['no_exact_structure_dedup'] = score(Xr[a], yr[a], Xr[b], yr[b])
    out['no_exact_structure_dedup']['n_records'] = int(len(yr))

    # D. grey band relabelled instead of dropped (inactive = anything above 1 uM), duplicates kept as rows.
    #    Note: applying this label *after* the lowest-IC50 collapse is a no-op -- every structure carrying a
    #    grey-band measurement also carries a non-grey one, so the collapsed frame is unchanged. The variant
    #    that can actually move the metrics keeps every measurement row and labels the grey band inactive.
    wide = full.copy()
    wide['label'] = (wide['ic50_nM'] <= 1000).astype(int)
    Xw = np.vstack(wide['canonical_smiles'].map(feature_vector))
    yw = wide['label'].to_numpy()
    gw = wide['canonical_smiles'].map(scaffold).to_numpy()
    a, b = next(iter(StratifiedGroupKFold(5, shuffle=True, random_state=17).split(Xw, yw, gw)))
    out['grey_band_relabelled_inactive'] = score(Xw[a], yw[a], Xw[b], yw[b])
    out['grey_band_relabelled_inactive']['n_records'] = int(len(yw))
    out['grey_band_relabelled_inactive']['n_inactive'] = int((yw == 0).sum())
    out['grey_band_relabelled_inactive']['n_grey_band_rows'] = int(len(full) - len(raw))
    out['no_exact_structure_dedup']['n_inactive'] = int((yr == 0).sum())

    # E. pooled out-of-fold predictions across the five scaffold folds
    oof = np.full(len(y), np.nan)
    for a, b in StratifiedGroupKFold(5, shuffle=True, random_state=17).split(X, y, groups):
        m = random_forest(seed=17)
        m.fit(X[a], y[a])
        oof[b] = m.predict_proba(X[b])[:, 1]
    out['pooled_out_of_fold'] = {'roc_auc': float(roc_auc_score(y, oof)),
                                 'pr_auc': float(average_precision_score(y, oof)),
                                 'test_n': int(len(y)), 'test_prevalence': float(np.mean(y))}

    # F. random split on the non-deduplicated frame
    ar, br = train_test_split(np.arange(len(yr)), test_size=0.2, random_state=17, stratify=yr)
    out['no_dedup_random_split'] = score(Xr[ar], yr[ar], Xr[br], yr[br])
    out['no_dedup_random_split']['test_n'] = int(len(br))

    # G. spread of one arbitrary scaffold-group 80/20 split across seeds
    sweep = []
    for seed in range(12):
        a, b = next(iter(StratifiedGroupKFold(5, shuffle=True, random_state=seed).split(X, y, groups)))
        r = score(X[a], y[a], X[b], y[b], seed=17)
        r['split_seed'] = seed
        sweep.append(r)
    rocs = np.array([r['roc_auc'] for r in sweep])
    prs = np.array([r['pr_auc'] for r in sweep])
    closest = min(sweep, key=lambda r: abs(r['roc_auc'] - 0.832) + abs(r['pr_auc'] - 0.966))
    out['single_split_seed_sweep'] = {
        'n_splits': len(sweep),
        'roc_range': [float(rocs.min()), float(rocs.max())],
        'pr_range': [float(prs.min()), float(prs.max())],
        'closest_split': closest,
        'per_seed': sweep,
    }

    def dist(target):
        return {'roc_delta': target['roc_auc'] - 0.832, 'pr_delta': target['pr_auc'] - 0.966}

    out['agreement_with_historical'] = {
        'random_stratified_split_no_grouping': dist(out['random_stratified_split_no_grouping']),
        'best_scaffold_fold': dist(max(folds.values(), key=lambda z: z['roc_auc'])),
        'no_exact_structure_dedup': dist(out['no_exact_structure_dedup']),
        'grey_band_relabelled_inactive': dist(out['grey_band_relabelled_inactive']),
        'pooled_out_of_fold': dist(out['pooled_out_of_fold']),
        'no_dedup_random_split': dist(out['no_dedup_random_split']),
        'closest_single_split': dist(closest),
    }
    Path('results/reports/historical_metric_diagnosis.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
