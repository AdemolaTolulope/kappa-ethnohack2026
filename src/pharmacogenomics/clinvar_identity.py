"""Refresh the ClinVar molecular-identity cross-reference only; not a response annotation."""
from datetime import date
from pathlib import Path
import json
import requests

URL='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi'
CLINVAR_UID='16897'  # VCV000016897; verified CYP2C19 c.681G>A record

def fetch(out='data/raw/clinvar_cyp2c19_star2.json'):
    r=requests.get(URL,params={'db':'clinvar','id':CLINVAR_UID,'retmode':'json'},headers={'User-Agent':'KAPPA research prototype (provenance contact via repository)'},timeout=30)
    r.raise_for_status();payload=r.json()['result'][CLINVAR_UID]
    assert payload.get('accession')=='VCV000016897', 'Unexpected ClinVar record; refuse to relabel.'
    variants=payload.get('variation_set',[])
    variant=next((v for v in variants if v.get('cdna_change')=='c.681G>A' and 'CYP2C19*2' in v.get('aliases',[])),None)
    assert variant is not None, 'Expected CYP2C19 c.681G>A / *2 identity not present.'
    assert any(x.get('db_source')=='dbSNP' and x.get('db_id')=='4244285' for x in variant.get('variation_xrefs',[])), 'Expected rs4244285 cross-reference not present.'
    result={'source':'NCBI ClinVar E-utilities ESummary','request_url':r.url,'retrieval_date':date.today().isoformat(),
      'scope_note':'Molecular identity cross-reference only. The record identifies NM_000769.4(CYP2C19):c.681G>A and lists dbSNP rs4244285 and CYP2C19*2 aliases. Its germline classification is \'Likely benign; other\' (last evaluated 2018-08-07) for traits recorded as \'not specified\' / \'not provided\'; that is a Mendelian disease-association classification, not a drug-metabolizer function call. It is therefore neither a response classification nor a contradiction of CPIC\'s \'no function\' allele assignment. Drug recommendations are sourced separately from CPIC and remain phenotype- and indication-conditioned.',
      'record':payload}
    p=Path(out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__=='__main__':
    x=fetch();print(x['record']['accession'],x['record']['title'],x['retrieval_date'])
