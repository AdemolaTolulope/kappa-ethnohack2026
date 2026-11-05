from pathlib import Path
import pandas as pd, json, networkx as nx
from src.data_pipeline import fetch,curate,audit_dataset
from src.ml.train import train_model
from src.knowledge_graph.graph import build_graph

def main():
 raw_path=Path('data/raw/chembl_ptgs2_ic50.jsonl')
 if raw_path.exists(): rows=[json.loads(x) for x in raw_path.read_text().splitlines() if x.strip()]; total=len(rows)
 else: rows,total=fetch()
 df=curate(rows)
 audit=audit_dataset(rows,df)
 Path('results/reports').mkdir(parents=True,exist_ok=True)
 Path('results/tables').mkdir(parents=True,exist_ok=True)
 Path('results/reports/data_quality.json').write_text(json.dumps(audit,indent=2))
 pd.DataFrame([{'measure':k,'count':v} for k,v in audit['sequential_exclusion_counts'].items()]).to_csv('results/tables/filter_counts.csv',index=False)
 if len(df)<30:raise RuntimeError(f'Not enough reliable labelled measurements ({len(df)}).')
 df.to_csv('data/processed/ptgs2_curated.csv',index=False)
 report,df,model,X,tr,te=train_model(df)
 sample=df.drop_duplicates('molecule_chembl_id').head(60)
 compounds=[{'chembl_id':r.molecule_chembl_id,'name':r.molecule_chembl_id,'smiles':r.canonical_smiles,'activity_id':int(r.activity_id),'ic50_nM':float(r.ic50_nM)} for r in sample.itertuples()]
 pgx_path=Path('data/raw/cpic_cyp2c19_clopidogrel.json'); pgx=json.loads(pgx_path.read_text()) if pgx_path.exists() else None
 use_path=Path('data/processed/ethnobotanical_claims.json'); claims=json.loads(use_path.read_text()).get('records',[]) if use_path.exists() else []
 g=build_graph(compounds,pgx,claims[0] if claims else None)
 for _,attrs in list(g.nodes(data=True))+[(None,a) for _,_,a in g.edges(data=True)]:
  for k,v in list(attrs.items()):
   if v is None: attrs.pop(k)
   elif not isinstance(v,(str,int,float,bool)): attrs[k]=json.dumps(v,ensure_ascii=False)
 Path('data/processed/knowledge_graph.graphml').parent.mkdir(parents=True,exist_ok=True); nx.write_graphml(g,'data/processed/knowledge_graph.graphml')
 report['retrieved_activity_count_total']=total; report['raw_record_count']=len(rows)
 Path('results/reports/model_metrics.json').write_text(json.dumps(report,indent=2))
 print(json.dumps({'raw_records':len(rows),'curated_records':len(df),'active':int(df.label.sum()),'inactive':int((df.label==0).sum()),'metrics':report['primary_models']},indent=2))
if __name__=='__main__':main()
