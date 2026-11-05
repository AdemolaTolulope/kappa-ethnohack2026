"""Fetch a separate, verified CPIC/ClinPGx evidence demonstration (not curcumin-linked)."""
from pathlib import Path
import json,time,requests
BASE='https://api.cpicpgx.org/v1'

def query(path,params):
    r=requests.get(f'{BASE}/{path}',params=params,timeout=30);r.raise_for_status();return r.json(),r.url

def fetch(out='data/raw/cpic_cyp2c19_clopidogrel.json'):
    # CPIC's public API is the source of curated allele-function and guideline records.
    requests_to_run=[
      ('gene',{'symbol':'eq.CYP2C19','select':'symbol,chr,genesequenceid,proteinsequenceid,chromosequenceid,mrnasequenceid,hgncid,ncbiid,ensemblid,clinpgxid'}),
      ('allele',{'genesymbol':'eq.CYP2C19','name':'eq.*2','select':'id,version,genesymbol,name,clinicalfunctionalstatus,citations,strength,findings,inferredfrequency,definitionid'}),
      ('drug',{'drugid':'eq.RxNorm:32968','select':'drugid,name,clinpgxid,rxnormid,drugbankid,atcid,version,guidelineid'}),
      ('pair',{'genesymbol':'eq.CYP2C19','drugid':'eq.RxNorm:32968','select':'pairid,genesymbol,drugid,guidelineid,usedforrecommendation,version,cpiclevel,clinpgxlevel,pgxtesting,citations,removed'}),
      ('guideline',{'id':'eq.100411','select':'id,version,name,url,genes,clinpgxid'}),
      ('recommendation',{'guidelineid':'eq.100411','drugid':'eq.RxNorm:32968','select':'id,guidelineid,drugid,implications,drugrecommendation,classification,phenotypes,lookupkey,population,comments,version'}),
    ]
    data={}; urls={}
    for resource,params in requests_to_run:
        data[resource],urls[resource]=query(resource,params);time.sleep(.55)
    # Store unmodified API payloads and explicit provenance; no fabricated variants or alleles.
    if not data['gene'] or not data['allele'] or not data['pair'] or not data['guideline']:
        raise RuntimeError('Required CPIC evidence record(s) missing; refusing to write partial demonstration.')
    result={'retrieval_date':'2026-11-05','source_api':'CPIC database API at https://api.cpicpgx.org/v1','license':'CC0 1.0; CPIC requests attribution, source URL, access date, version and a current-source caveat','request_urls':urls,'resources':data,
      'scope_note':'Separate canonical gene–drug pharmacogenomic evidence demonstration: CYP2C19–clopidogrel. It is not linked to Curcuma longa, curcumin, PTGS2 or the molecular activity model. Recommendations are published guideline records, not patient-specific advice.'}
    Path(out).parent.mkdir(parents=True,exist_ok=True);Path(out).write_text(json.dumps(result,indent=2));return result

if __name__=='__main__':
    x=fetch();print(json.dumps({k:len(v) for k,v in x['resources'].items()},indent=2))
