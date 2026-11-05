from pathlib import Path
import json, pandas as pd, numpy as np, joblib, networkx as nx
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from src.chemistry.features import descriptors, feature_vector, fingerprint
from src.knowledge_graph.graph import build_graph, graph_payload
from src.prioritisation.rank import score_candidate
ROOT=Path(__file__).resolve().parents[1]
app=FastAPI(title='KAPPA Research Workbench',description='Evidence-aware natural-product research prototype')
app.add_middleware(CORSMiddleware,allow_origins=['*'],allow_methods=['*'],allow_headers=['*'])
from fastapi.staticfiles import StaticFiles
app.mount('/results',StaticFiles(directory=ROOT/'results'),name='results')
app.mount('/docs',StaticFiles(directory=ROOT/'docs'),name='project-docs')

def data():
 p=ROOT/'data/processed/ptgs2_curated.csv'
 return pd.read_csv(p) if p.exists() else pd.DataFrame()
def model():
 p=ROOT/'models/ptgs2_rf.joblib'
 return joblib.load(p) if p.exists() else None
@app.get('/',response_class=HTMLResponse)
def home():return (ROOT/'frontend/index.html').read_text()
@app.get('/api/overview')
def overview():
 d=data(); report=json.loads((ROOT/'results/reports/model_metrics.json').read_text()) if (ROOT/'results/reports/model_metrics.json').exists() else {}
 return {'project':'KAPPA','records':len(d),'active':int((d.label==1).sum()) if len(d) else 0,'inactive':int((d.label==0).sum()) if len(d) else 0,'metrics':report,'plant':'Curcuma longa L.','compound':'Curcumin','target':'Human PTGS2 / COX-2','source':'ChEMBL REST target CHEMBL230'}
@app.get('/api/compounds')
def compounds(q:str=''):
 d=data()
 if q: d=d[d.canonical_smiles.str.contains(q,case=False,na=False)|d.molecule_chembl_id.str.contains(q,case=False,na=False)]
 return d.head(300).astype(object).where(pd.notna(d.head(300)),None).to_dict(orient='records')
@app.get('/api/structure')
def structure(smiles:str):
 from rdkit.Chem.Draw import rdMolDraw2D
 from rdkit import Chem
 mol=Chem.MolFromSmiles(smiles)
 if mol is None: raise HTTPException(400,'Invalid SMILES string')
 drawer=rdMolDraw2D.MolDraw2DSVG(440,260)
 drawer.drawOptions().clearBackground=False
 drawer.DrawMolecule(mol); drawer.FinishDrawing()
 return Response(content=drawer.GetDrawingText(),media_type='image/svg+xml')

@app.get('/api/graph')
def graph(scope:str='pilot'):
 d=data(); unique=d.drop_duplicates('molecule_chembl_id').head(35)
 rows=[{'chembl_id':r.molecule_chembl_id,'name':r.molecule_chembl_id,'smiles':r.canonical_smiles,'activity_id':int(r.activity_id),'ic50_nM':float(r.ic50_nM)} for r in unique.itertuples()]
 pgx_path=ROOT/'data/raw/cpic_cyp2c19_clopidogrel.json';pgx=json.loads(pgx_path.read_text()) if pgx_path.exists() else None
 use_path=ROOT/'data/processed/ethnobotanical_claims.json';claims=json.loads(use_path.read_text()).get('records',[]) if use_path.exists() else []
 g=build_graph(rows,pgx,claims[0] if claims else None)
 if scope=='pharmacogenomics': nodes=[n for n,d in g.nodes(data=True) if str(n).startswith('pgx:')]
 elif scope=='all': nodes=list(g.nodes)
 else: nodes=[n for n in g.nodes if not str(n).startswith('pgx:')]
 return graph_payload(g.subgraph(nodes).copy())
@app.post('/api/predict')
def predict(payload:dict):
 smi=payload.get('smiles',''); d=descriptors(smi)
 if d is None:raise HTTPException(400,'Invalid SMILES string')
 bundle=model(); data_df=data()
 if bundle is None or data_df.empty:raise HTTPException(503,'Model unavailable; run python -m src.run_pipeline')
 m=bundle['model']; training_smiles=bundle['training_smiles']
 x=feature_vector(smi).reshape(1,-1); p=float(m.predict_proba(x)[0,1]); train=np.vstack([fingerprint(s) for s in training_smiles]); query=fingerprint(smi)
 sims=(train@query)/(np.maximum((train.sum(1)+query.sum()-train@query),1))
 mx=float(sims.max()); threshold=float(bundle.get('ad_threshold',1.0)); in_domain=mx>=threshold
 train_df=data_df[data_df.canonical_smiles.isin(training_smiles)].copy(); order=np.argsort(sims)[::-1][:3]
 neighbors=[{'chembl_id':str(train_df.iloc[int(i)].molecule_chembl_id),'activity_id':int(train_df.iloc[int(i)].activity_id),'ic50_nM':float(train_df.iloc[int(i)].ic50_nM),'label':'active' if int(train_df.iloc[int(i)].label)==1 else 'inactive','tanimoto':float(sims[i])} for i in order]
 matches=data_df[data_df.canonical_smiles==d['canonical_smiles']]
 exact=not matches.empty
 if exact:
  r=matches.iloc[0]
  bio={'status':'exact canonical-structure match in cached ChEMBL PTGS2 subset','chembl_id':str(r.molecule_chembl_id),'activity_id':int(r.activity_id),'assay_chembl_id':str(r.assay_chembl_id),'document_chembl_id':str(r.document_chembl_id),'ic50_nM':float(r.ic50_nM),'operational_band':'active' if int(r.label)==1 else 'inactive','interpretation':'One curated representative record; inspect original assay/document before drawing broader conclusions.'}
  identity={'status':'exact canonical structure matched to ChEMBL','chembl_id':str(r.molecule_chembl_id),'confidence':'database-structure match, not authentication of a physical sample'}
 else:
  bio=None; identity=None
 pubchem_match=False
 try:
  pc=json.loads((ROOT/'data/raw/pubchem_curcumin_CID969516.json').read_text())['PropertyTable']['Properties'][0]
  from src.chemistry.features import descriptors as _desc
  pubchem_match=_desc(pc.get('SMILES',''))['canonical_smiles']==d['canonical_smiles']
 except Exception: pass
 if pubchem_match:
  identity={'status':'structure matched to cached PubChem CID 969516 property record','pubchem_cid':969516,'confidence':'database-structure match; not physical sample authentication'}
 plant_context=None
 if pubchem_match:
  plant_context={'status':'plant-level context only; not linked as evidence that the compound mediates this reported use','plant':'Curcuma longa L.','occurrence_source':'Wikidata Q312266 P703 Q42562','reported_use_claim_id':'VELAYUDHAN2012-T1-COUGH-COLD','reported_use':'Secondary-source report: cough/cold practice; this is not compound-specific evidence or efficacy.'}
 assessment=score_candidate(p,mx,threshold,identity,bio,None,plant_context)
 return {'properties':d,'probability_active':p,'max_training_similarity':mx,'applicability_threshold':threshold,'in_domain':in_domain,'exact_training_match':exact,'nearest_training_examples':neighbors,'score':assessment,'target':'PTGS2 human biochemical assay','warning':'Model output is an uncalibrated activity-band estimate, not mechanism, therapeutic benefit or patient-specific prediction.' + (' Exact training-set structure match: retrospective score, not prospective validation.' if exact else '')}
@app.get('/api/pharmacogenomics')
def pharmacogenomics():
 p=ROOT/'data/raw/cpic_cyp2c19_clopidogrel.json'
 if not p.exists(): raise HTTPException(404,'CPIC demonstration record not cached')
 x=json.loads(p.read_text());r=x['resources'];
 recs=[z for z in r['recommendation'] if z.get('population')=='CVI ACS PCI ' and z.get('phenotypes',{}).get('CYP2C19') in ('Intermediate Metabolizer','Poor Metabolizer')]
 cv_path=ROOT/'data/raw/clinvar_cyp2c19_star2.json';cv=json.loads(cv_path.read_text()) if cv_path.exists() else None
 return {'retrieval_date':x['retrieval_date'],'license':x['license'],'scope_note':x['scope_note'],'gene':r['gene'][0],'allele':r['allele'][0],'drug':r['drug'][0],'pair':r['pair'][0],'guideline':r['guideline'][0],'recommendations':recs,'sources':x['request_urls'],'clinvar':cv}

@app.get('/api/genomic-context')
def genomic_context():
 p=ROOT/'data/raw/uniprot_ptgs2_P35354.json'
 if not p.exists(): raise HTTPException(404,'UniProt target context not cached')
 j=json.loads(p.read_text())
 genes=j.get('genes',[]); gene=genes[0].get('geneName',{}).get('value') if genes else None
 protein=j.get('proteinDescription',{}).get('recommendedName',{}).get('fullName',{}).get('value')
 return {'accession':j.get('primaryAccession'),'gene':gene,'protein_name':protein,'organism':j.get('organism',{}).get('scientificName'),'taxon_id':j.get('organism',{}).get('taxonId'),'retrieved':'2026-11-05','source':'UniProt REST API','source_url':'https://rest.uniprot.org/uniprotkb/P35354.json','evidence_scope':'Curated gene/protein identity only; no variant-response association loaded.'}

@app.get('/api/data-quality')
def data_quality():
 p=ROOT/'results/reports/data_quality.json'
 return json.loads(p.read_text()) if p.exists() else {}

@app.get('/api/metrics')
def metrics():
 p=ROOT/'results/reports/model_metrics.json'
 return json.loads(p.read_text()) if p.exists() else {}
@app.get('/api/export')
def export():return FileResponse(ROOT/'data/processed/ptgs2_curated.csv',filename='kappa_chembl_ptgs2.csv')
