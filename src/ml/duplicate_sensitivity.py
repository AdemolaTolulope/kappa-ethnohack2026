"""Duplicate-structure aggregation sensitivity for the PTGS2 activity-band task.

The primary analysis collapses exact canonical structures by keeping the lowest measured
IC50. This module asks the obvious reviewer question: how much does that choice matter?
It re-runs the identical eligibility filters, splitting protocol and model configuration
under three prespecified aggregation rules and reports them side by side.

It never overwrites the primary analysis: it writes a separate report.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from sklearn.model_selection import StratifiedGroupKFold

from src.chemistry.features import descriptors, feature_vector, scaffold
from src.data_pipeline import curate
from src.ml.train import eval_metrics, random_forest, stratified_group_holdout

ACTIVE_MAX_NM = 1000.0
INACTIVE_MIN_NM = 10000.0
DESCRIPTOR_KEYS = ('formula', 'mw', 'logp', 'tpsa', 'hbd', 'hba', 'rotatable_bonds', 'fraction_csp3')


def eligible_measurements(rows):
    """Same ordered eligibility filters as the primary curation, without any deduplication."""
    out = []
    for r in rows:
        try:
            val = float(r['standard_value'])
        except (ValueError, TypeError, KeyError):
            continue
        if not math.isfinite(val) or val <= 0:
            continue
        if not r.get('canonical_smiles') or r.get('standard_relation') != '=' or r.get('assay_type') != 'B':
            continue
        if r.get('target_organism') != 'Homo sapiens' or r.get('potential_duplicate') == 1:
            continue
        if r.get('data_validity_comment'):
            continue
        d = descriptors(r['canonical_smiles'])
        if d is None:
            continue
        out.append({'activity_id': r.get('activity_id'), 'molecule_chembl_id': r.get('molecule_chembl_id'),
                    'document_chembl_id': r.get('document_chembl_id'), 'document_year': r.get('document_year'),
                    'canonical_smiles': d['canonical_smiles'], 'ic50_nM': val, **{k: d[k] for k in DESCRIPTOR_KEYS}})
    return pd.DataFrame(out)


def label_from_ic50(value):
    if value <= ACTIVE_MAX_NM:
        return 1
    if value >= INACTIVE_MIN_NM:
        return 0
    return None  # grey band is never relabelled


def aggregate(df, strategy):
    """Return one row per canonical structure under the requested aggregation rule."""
    if strategy not in {'lowest_ic50', 'median_ic50', 'exclude_conflicting'}:
        raise ValueError(strategy)
    work = df.copy()
    work['band_label'] = work['ic50_nM'].map(label_from_ic50)
    work['labelled_ic50_nM'] = work['ic50_nM'].where(work['band_label'].notna())
    g = work.groupby('canonical_smiles', sort=True)
    stats = pd.DataFrame({
        'count': g['ic50_nM'].size(),
        'min_all_nM': g['ic50_nM'].min(),
        'median_all_nM': g['ic50_nM'].median(),
        'n_active_records': g['band_label'].apply(lambda s: int((s == 1).sum())),
        'n_inactive_records': g['band_label'].apply(lambda s: int((s == 0).sum())),
        'min_labelled_nM': g['labelled_ic50_nM'].min(),
        'median_labelled_nM': g['labelled_ic50_nM'].median(),
    }).reset_index()
    stats['conflicting'] = (stats['n_active_records'] > 0) & (stats['n_inactive_records'] > 0)
    n_conflicting = int(stats['conflicting'].sum())
    if strategy == 'lowest_ic50':
        # Reproduces the primary curation exactly: the grey band is removed first, then the
        # lowest surviving labelled measurement represents the structure.
        stats['representative_ic50_nM'] = stats['min_labelled_nM']
    elif strategy == 'median_ic50':
        # Alternative: every eligible measurement contributes, including grey-band values.
        stats['representative_ic50_nM'] = stats['median_all_nM']
    else:
        stats = stats[~stats['conflicting']].copy()
        stats['representative_ic50_nM'] = stats['median_all_nM']
    stats['label'] = stats['representative_ic50_nM'].map(label_from_ic50)
    stats = stats.dropna(subset=['label']).copy()
    stats['label'] = stats['label'].astype(int)
    # One representative measurement row supplies the descriptors and the document identity.
    first = df.sort_values('ic50_nM').drop_duplicates('canonical_smiles').set_index('canonical_smiles')
    keep = [c for c in ['molecule_chembl_id', 'document_chembl_id', 'document_year', 'activity_id', *DESCRIPTOR_KEYS] if c in first.columns]
    out = stats.merge(first[keep], left_on='canonical_smiles', right_index=True, how='left')
    out.attrs['dropped_conflicts'] = n_conflicting if strategy == 'exclude_conflicting' else 0
    out.attrs['multi_record_structures'] = int((stats['count'] > 1).sum())
    return out.sort_values('canonical_smiles').reset_index(drop=True)


def evaluate_strategy(df, strategy, rows=None, seed=17):
    """Score one aggregation rule with the primary protocol plus a 3-fold scaffold CV.

    Row ordering determines which structures land in fold 0, so the primary rule is taken
    directly from `curate()` (the code path behind the reported result) and is checked
    against the stored metrics. The alternative rules are ordered deterministically by
    representative IC50 and canonical SMILES; their folds are therefore re-derived, which is
    why the 3-fold CV mean and spread are reported alongside the single holdout.
    """
    if strategy == 'lowest_ic50':
        agg = curate(rows)
        agg = agg[['canonical_smiles', 'ic50_nM', 'label', 'molecule_chembl_id', 'document_chembl_id', 'document_year']].copy()
        n_conflicts_dropped = 0
        multi_record = int((df.groupby('canonical_smiles').size() > 1).sum())
        counts = df.groupby('canonical_smiles').size()
        agg['count'] = agg['canonical_smiles'].map(counts).fillna(1).astype(int)
    else:
        agg = aggregate(df, strategy)
        agg['ic50_nM'] = agg['representative_ic50_nM']
        n_conflicts_dropped = int(agg.attrs.get('dropped_conflicts', 0))
        multi_record = agg.attrs.get('multi_record_structures')
        agg = agg.sort_values(['ic50_nM', 'canonical_smiles'], kind='mergesort').reset_index(drop=True)
    if len(agg) < 50 or agg['label'].nunique() != 2:
        return {'strategy': strategy, 'status': 'insufficient data or class support', 'n_structures': int(len(agg))}
    agg = agg.copy()
    agg['scaffold'] = agg['canonical_smiles'].map(scaffold)
    X = np.vstack(agg['canonical_smiles'].map(feature_vector))
    y = agg['label'].to_numpy()
    groups = agg['scaffold'].to_numpy()
    tr, te = stratified_group_holdout(y, groups, 5, seed, 0)
    assert not (set(groups[tr]) & set(groups[te])), 'scaffold leakage'
    assert not (set(agg.iloc[tr]['canonical_smiles']) & set(agg.iloc[te]['canonical_smiles'])), 'structure leakage'
    model = random_forest(seed=seed)
    model.fit(X[tr], y[tr])
    p = model.predict_proba(X[te])[:, 1]
    metrics = eval_metrics(y[te], p)

    # 3-fold training-only-style scaffold CV over the whole aggregated set: mean and spread.
    cv = []
    for fold, (a, b) in enumerate(StratifiedGroupKFold(3, shuffle=True, random_state=29).split(X, y, groups)):
        m = random_forest(seed=29 + fold)
        m.fit(X[a], y[a])
        cv.append(eval_metrics(y[b], m.predict_proba(X[b])[:, 1]))
    cv_summary = {k: {'mean': float(np.mean([c[k] for c in cv])), 'sd': float(np.std([c[k] for c in cv], ddof=1))}
                  for k in ('roc_auc', 'pr_auc', 'balanced_accuracy_at_0_5', 'matthews_corrcoef_at_0_5')}
    return {'strategy': strategy,
            'n_structures': int(len(agg)),
            'n_active': int(y.sum()),
            'n_inactive': int((y == 0).sum()),
            'active_prevalence': float(y.mean()),
            'n_conflicting_structures_dropped': n_conflicts_dropped,
            'n_scaffolds': int(len(set(groups))),
            'train_n': int(len(tr)),
            'test_n': int(len(te)),
            'test_active_prevalence': float(y[te].mean()),
            'n_structures_with_multiple_records': int((agg['count'] > 1).sum()) if 'count' in agg else multi_record,
            'holdout_metrics': metrics,
            'three_fold_scaffold_cv': cv_summary,
            'fold_metrics': cv}


def run(rows_path='data/raw/chembl_ptgs2_ic50.jsonl', out='results/reports/duplicate_sensitivity.json'):
    rows = [json.loads(x) for x in Path(rows_path).read_text().splitlines() if x.strip()]
    df = eligible_measurements(rows)
    conflicts = (df.groupby('canonical_smiles')['ic50_nM']
                 .apply(lambda s: bool((s <= ACTIVE_MAX_NM).any() and (s >= INACTIVE_MIN_NM).any())))
    report = {
        'question': 'How sensitive are class balance and held-out performance to the duplicate-structure aggregation rule?',
        'primary_analysis': 'lowest IC50 per canonical structure (the reported primary result); unchanged by this analysis',
        'eligible_measurement_records_before_dedup': int(len(df)),
        'unique_structures_before_dedup': int(df['canonical_smiles'].nunique()),
        'structures_with_multiple_eligible_records': int((df.groupby('canonical_smiles').size() > 1).sum()),
        'structures_with_active_and_inactive_records': int(conflicts.sum()),
        'protocol': 'Identical eligibility filters, Bemis-Murcko scaffold groups, first fold of StratifiedGroupKFold(n_splits=5, shuffle=True, seed=17) and identical random-forest configuration (350 trees, min_samples_leaf=2, class_weight=balanced, max_features=sqrt, seed=17). Each rule is additionally scored by 3-fold scaffold CV (seed=29). Because the structure sets differ, each rule receives its own fold assignment; this is a sensitivity analysis, not a re-selection of the primary model.',
        'strategies': {},
    }
    for strategy in ('lowest_ic50', 'median_ic50', 'exclude_conflicting'):
        report['strategies'][strategy] = evaluate_strategy(df, strategy, rows=rows)
    base = report['strategies']['lowest_ic50'].get('holdout_metrics', {})
    for name, res in report['strategies'].items():
        if 'holdout_metrics' in res and base:
            res['delta_vs_primary_holdout'] = {
                k: float(res['holdout_metrics'][k] - base[k]) for k in
                ('roc_auc', 'pr_auc', 'balanced_accuracy_at_0_5', 'matthews_corrcoef_at_0_5')}

    # Reproduction check: the lowest-IC50 rule must rebuild the reported primary numbers.
    try:
        stored = json.loads(Path('results/reports/model_metrics.json').read_text())['primary_models']['Random forest']
        mine = report['strategies']['lowest_ic50']['holdout_metrics']
        report['primary_reproduction_check'] = {k: {'sensitivity_run': mine[k], 'stored_primary': stored[k],
                                                     'absolute_difference': abs(mine[k] - stored[k])}
                                                for k in ('roc_auc', 'pr_auc', 'balanced_accuracy_at_0_5')}
        report['primary_reproduction_check']['reproduced_within_1e-9'] = all(
            abs(mine[k] - stored[k]) < 1e-9 for k in ('roc_auc', 'pr_auc', 'balanced_accuracy_at_0_5'))
    except (FileNotFoundError, KeyError) as exc:
        report['primary_reproduction_check'] = {'status': f'could not compare to stored primary metrics: {exc}'}

    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    r = run()
    print(json.dumps({'records': r['eligible_measurement_records_before_dedup'],
                      'unique_structures': r['unique_structures_before_dedup'],
                      'multi_record_structures': r['structures_with_multiple_eligible_records'],
                      'conflicting_structures': r['structures_with_active_and_inactive_records']}, indent=2))
    for name, res in r['strategies'].items():
        m, cv = res.get('holdout_metrics', {}), res.get('three_fold_scaffold_cv', {})
        print(f"{name:20s} n={res['n_structures']:5d} prev={res['active_prevalence']:.3f} "
              f"holdout ROC={m.get('roc_auc', float('nan')):.4f} PR={m.get('pr_auc', float('nan')):.4f} "
              f"balacc={m.get('balanced_accuracy_at_0_5', float('nan')):.4f} MCC={m.get('matthews_corrcoef_at_0_5', float('nan')):.4f} | "
              f"CV ROC={cv.get('roc_auc', {}).get('mean', float('nan')):.4f}±{cv.get('roc_auc', {}).get('sd', float('nan')):.4f}")
    print('primary reproduction:', r.get('primary_reproduction_check', {}).get('reproduced_within_1e-9'))
