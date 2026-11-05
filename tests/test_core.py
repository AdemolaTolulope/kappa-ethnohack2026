import json
from pathlib import Path
from src.chemistry.features import descriptors, fingerprint, scaffold
from src.prioritisation.rank import score_candidate
from src.knowledge_graph.graph import build_graph, graph_payload
from src.data_pipeline import curate, audit_dataset
from src.ml.train import stratified_group_holdout
from src.ml.duplicate_sensitivity import aggregate, eligible_measurements, label_from_ic50
import numpy as np

ROOT=Path(__file__).resolve().parents[1]

def test_rdkit_validates_and_canonicalizes():
    d=descriptors('CCO')
    assert d['formula']=='C2H6O'
    assert d['mw']>40
    assert len(fingerprint('CCO'))==512
    assert descriptors('not-a-smiles') is None

def test_scaffold_deterministic():
    assert scaffold('CCO')=='__acyclic__'
    assert scaffold('c1ccccc1')==scaffold('c1ccccc1')

def test_model_only_triage_is_withheld_outside_domain_and_no_composite():
    inside=score_candidate(model_probability=.8,max_similarity=.4,applicability_threshold=.3)
    outside=score_candidate(model_probability=.8,max_similarity=.2,applicability_threshold=.3)
    assert inside['candidate_priority_score']==.8
    assert outside['candidate_priority_score'] is None
    assert 'score' not in inside
    assert 'training_similarity' not in inside
    assert len(inside['missing_evidence'])==4

def test_graph_edges_carry_source_and_evidence():
    g=build_graph([])
    assert g.has_edge('plant:curcuma_longa','compound:curcumin')
    e=next(iter(g['plant:curcuma_longa']['compound:curcumin'].values()))
    assert e.get('source') and e.get('evidence')

def test_edge_payload_keeps_topology_ids_distinct_from_provenance():
    g=build_graph([{'chembl_id':'CHEMBL_X','name':'X','smiles':'CCO','activity_id':1,'ic50_nM':500}])
    p=graph_payload(g); ids={n['id'] for n in p['nodes']}
    assert p['edges'] and all(e['source'] in ids and e['target'] in ids for e in p['edges'])
    assert all(e.get('source_reference') for e in p['edges'])

def test_cpic_and_clinvar_demo_is_verified_and_disconnected():
    pgx=json.loads((ROOT/'data/raw/cpic_cyp2c19_clopidogrel.json').read_text())
    claim=json.loads((ROOT/'data/processed/ethnobotanical_claims.json').read_text())['records'][0]
    g=build_graph([],pgx,claim); p=graph_payload(g)
    ids={n['id'] for n in p['nodes']}
    assert 'pgx:variant:rs4244285' in ids
    assert 'pgx:drug:clopidogrel' in ids
    assert 'use:VELAYUDHAN2012-T1-COUGH-COLD' in ids
    assert not any(e['source'].startswith('pgx:') and e['target'].startswith(('plant:','compound:','target:')) for e in p['edges'])
    recs=[n for n in p['nodes'] if n.get('kind')=='guideline_recommendation']
    assert len(recs)==2 and all('CVI ACS PCI' in str(n.get('population_context')) for n in recs)

def test_stratified_group_holdout_has_no_group_leakage():
    groups=np.repeat(np.arange(40),4)
    y=np.tile([1,1,1,0],40)
    tr,te=stratified_group_holdout(y,groups,n_splits=5,seed=17,fold=0)
    assert not set(groups[tr]) & set(groups[te])
    assert len(set(y[tr]))==2 and len(set(y[te]))==2

def test_pipeline_uses_declared_activity_bands_and_records_audit():
    base={'activity_id':1,'molecule_chembl_id':'CHEMBL_X','canonical_smiles':'CCO','standard_type':'IC50','standard_relation':'=','standard_units':'nM','assay_type':'B','target_organism':'Homo sapiens','target_pref_name':'PTGS2','document_chembl_id':'DOC','document_year':2020,'document_journal':'Test','potential_duplicate':0,'data_validity_comment':None}
    rows=[{**base,'activity_id':1,'standard_value':'500'},{**base,'activity_id':2,'molecule_chembl_id':'CHEMBL_Y','canonical_smiles':'CCN','standard_value':'5000'}]
    df=curate(rows); audit=audit_dataset(rows,df)
    assert len(df)==1 and int(df.iloc[0].label)==1
    assert audit['sequential_exclusion_counts']['weak_intermediate_band']==1
    assert audit['curated_unique_structures']==1


def _dup_rows():
    base={'standard_type':'IC50','standard_relation':'=','standard_units':'nM','assay_type':'B','target_organism':'Homo sapiens',
          'potential_duplicate':0,'data_validity_comment':None,'molecule_chembl_id':'CHEMBL_TEST','document_chembl_id':'DOC','document_year':2020}
    # CCO: active 100 nM plus inactive 20,000 nM -> conflicting structure.
    # CCCl: active 200 nM and 800 nM -> concordant active.
    # c1ccccc1: single inactive 50,000 nM.
    # CCCCCC: single grey-band 5,000 nM -> never labelled.
    return [
        {**base,'activity_id':1,'canonical_smiles':'CCO','standard_value':'100'},
        {**base,'activity_id':2,'canonical_smiles':'CCO','standard_value':'20000'},
        {**base,'activity_id':3,'canonical_smiles':'CCCl','standard_value':'200'},
        {**base,'activity_id':4,'canonical_smiles':'CCCl','standard_value':'800'},
        {**base,'activity_id':5,'canonical_smiles':'c1ccccc1','standard_value':'50000'},
        {**base,'activity_id':6,'canonical_smiles':'CCCCCC','standard_value':'5000'},
    ]

def test_duplicate_aggregation_rules_are_explicit_and_preserve_primary():
    df=eligible_measurements(_dup_rows())
    assert label_from_ic50(5000) is None  # grey band never relabelled
    lowest=aggregate(df,'lowest_ic50').set_index('canonical_smiles')
    median=aggregate(df,'median_ic50').set_index('canonical_smiles')
    excl=aggregate(df,'exclude_conflicting').set_index('canonical_smiles')
    # Grey-band-only structure is excluded from every rule.
    for frame in (lowest,median,excl):
        assert 'CCCCCC' not in frame.index
    # Lowest rule labels the conflicting structure active; median rule also active (median of 100 and 20000 = 10050 -> inactive).
    assert lowest.loc['CCO','label']==1
    assert median.loc['CCO','label']==0
    # Exclusion rule drops the conflicting structure entirely.
    assert 'CCO' not in excl.index
    assert excl.loc['CCCl','label']==1 and excl.loc['c1ccccc1','label']==0

def test_ethnobotany_records_validate_and_never_assert_compound_linkage():
    from src.ethnobotany import ClaimValidationError, coverage_note, load_claims, summarise
    payload = load_claims(ROOT/'data/processed/ethnobotanical_claims.json')
    assert len(payload['records']) == 1
    s = summarise(payload['records'][0])
    assert s['compound_linkage'] == 'not asserted'
    assert s['is_efficacy_evidence'] is False
    assert s['is_compound_specific_evidence'] is False
    assert s['limitations'] and s['source_url_or_doi'].startswith('https://')
    note = coverage_note(ROOT/'data/processed/ethnobotanical_claims.json')
    assert note['records'] == 1 and 'limited demonstration corpus' in note['status']

def test_ethnobotany_validation_fails_closed(tmp_path):
    from src.ethnobotany import ClaimValidationError, load_claims
    bad = tmp_path/'claims.json'
    bad.write_text(json.dumps({'retrieval_date':'2026-11-05','records':[{
        'claim_id':'X','taxon':'X','claim_type':'t','reported_indication_as_published':'i',
        'evidence_status':'e','source':{'authors':['A'],'year':2000,'title':'t','journal':'j','url':'https://example.org'},
        'limitations':['l'],'compound_linkage':'curcumin causes the effect'}]}))
    try:
        load_claims(bad)
    except ClaimValidationError as exc:
        assert 'compound_linkage' in str(exc)
    else:
        raise AssertionError('a record asserting compound linkage must be rejected')
