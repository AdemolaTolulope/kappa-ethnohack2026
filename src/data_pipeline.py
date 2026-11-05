"""Fetch and curate measured human PTGS2 IC50 records from ChEMBL REST API."""
import requests, time, json, math
from pathlib import Path
import pandas as pd
BASE='https://www.ebi.ac.uk/chembl/api/data/activity.json'
TARGET='CHEMBL230' # human prostaglandin G/H synthase 2 (PTGS2)
FIELDS=['activity_id','molecule_chembl_id','canonical_smiles','standard_type','standard_relation','standard_value','standard_units','assay_chembl_id','assay_type','target_organism','target_pref_name','document_chembl_id','document_year','document_journal','potential_duplicate','data_validity_comment']
def fetch(out='data/raw/chembl_ptgs2_ic50.jsonl', limit=None):
    path=Path(out); path.parent.mkdir(parents=True,exist_ok=True)
    params={'target_chembl_id':TARGET,'standard_type':'IC50','standard_units':'nM','limit':1000,'offset':0}
    rows=[]; total=None
    while True:
        r=requests.get(BASE,params=params,timeout=60); r.raise_for_status(); j=r.json()
        total=j['page_meta']['total_count']
        for x in j['activities']: rows.append({k:x.get(k) for k in FIELDS})
        if limit and len(rows)>=limit: rows=rows[:limit]; break
        if not j['page_meta'].get('next'): break
        params['offset']+=params['limit']; time.sleep(.1)
    with path.open('w') as f:
        for x in rows:f.write(json.dumps(x)+'\n')
    return rows, total

def audit_dataset(rows, final_df):
    """Return missingness and sequential filter accounting without double-counting exclusions."""
    from src.chemistry.features import descriptors
    fields=['standard_value','canonical_smiles','standard_relation','standard_units','assay_type','target_organism']
    missing={k:sum(r.get(k) in (None,'') for r in rows) for k in fields}
    eligible=[]; excluded={k:0 for k in ['missing_or_non_numeric_value','nonpositive_or_nonfinite_value','non_exact_relation','wrong_units','not_single_protein_assay','nonhuman_target','duplicate_flag','validity_flag','weak_intermediate_band','invalid_structure']}
    for r in rows:
        try: val=float(r.get('standard_value'))
        except (ValueError,TypeError): excluded['missing_or_non_numeric_value']+=1; continue
        if not math.isfinite(val) or val<=0: excluded['nonpositive_or_nonfinite_value']+=1; continue
        if r.get('standard_relation')!='=': excluded['non_exact_relation']+=1;continue
        if r.get('standard_units')!='nM': excluded['wrong_units']+=1;continue
        if r.get('assay_type')!='B': excluded['not_single_protein_assay']+=1;continue
        if r.get('target_organism')!='Homo sapiens': excluded['nonhuman_target']+=1;continue
        if r.get('potential_duplicate')==1: excluded['duplicate_flag']+=1;continue
        if r.get('data_validity_comment'): excluded['validity_flag']+=1;continue
        if not r.get('canonical_smiles'): excluded['invalid_structure']+=1;continue
        if 1000<val<10000: excluded['weak_intermediate_band']+=1;continue
        if val>1000 and val<10000: continue
        d=descriptors(r['canonical_smiles'])
        if d is None: excluded['invalid_structure']+=1;continue
        eligible.append((d['canonical_smiles'],val))
    audit={'raw_records':len(rows),'missing_counts':missing,'missing_fraction':{k:round(v/max(1,len(rows)),6) for k,v in missing.items()},
      'sequential_exclusion_counts':excluded,'valid_labelled_measurements_before_structure_dedup':len(eligible),
      'duplicate_structure_records_removed':len(eligible)-int(final_df.shape[0]),'curated_unique_structures':int(final_df.shape[0]),
      'active_unique':int((final_df.label==1).sum()) if len(final_df) else 0,'inactive_unique':int((final_df.label==0).sum()) if len(final_df) else 0,
      'note':'Missing-field counts overlap; sequential exclusion counts are ordered and non-overlapping. IC50 grey zone omitted, not labelled inactive.'}
    return audit

def curate(rows):
    # Use only exact standard measurements on single-protein assays; discard duplicate/flagged records.
    keep=[]
    for r in rows:
        try: val=float(r['standard_value'])
        except (ValueError,TypeError): continue
        if not math.isfinite(val) or val<=0: continue
        if not r.get('canonical_smiles') or r.get('standard_relation')!='=' or r.get('assay_type')!='B':continue
        if r.get('target_organism')!='Homo sapiens' or r.get('potential_duplicate')==1:continue
        if r.get('data_validity_comment'):continue
        if val<=1000: label=1 # measured IC50 <= 1 uM
        elif val>=10000: label=0 # measured IC50 >= 10 uM
        else: continue # predeclared indifference band to reduce label ambiguity
        keep.append({**r,'ic50_nM':val,'label':label})
    df=pd.DataFrame(keep)
    if len(df):
        from src.chemistry.features import descriptors
        feats=df.canonical_smiles.map(descriptors)
        valid=feats.notna(); df=df.loc[valid].copy(); feats=feats.loc[valid]
        df['canonical_smiles']=feats.map(lambda x:x['canonical_smiles'])
        for key in ('formula','mw','logp','tpsa','hbd','hba','rotatable_bonds','fraction_csp3'):
            df[key]=feats.map(lambda x:x[key])
        # Exact canonical structure duplicates are kept only once, preventing cross-split leakage.
        df=df.sort_values('ic50_nM').drop_duplicates('canonical_smiles',keep='first').reset_index(drop=True)
    return df
