"""Recreate data-property and workflow figures from processed pilot dataset."""
import pandas as pd, matplotlib.pyplot as plt, numpy as np
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; df=pd.read_csv(ROOT/'data/processed/ptgs2_curated.csv'); out=ROOT/'results/figures'; out.mkdir(exist_ok=True,parents=True)
fig,axs=plt.subplots(1,3,figsize=(12,3.6))
for ax,k,title,color in zip(axs,['mw','logp','tpsa'],['Molecular weight (Da)','Calculated logP','Topological polar surface area'],['#53c99a','#76c5d7','#d6bd77']):
 ax.hist(df[k].dropna(),bins=32,color=color,alpha=.88,edgecolor='#10251d'); ax.set_title(title,fontsize=10); ax.set_ylabel('Structures'); ax.spines[['top','right']].set_visible(False)
fig.suptitle(f'Curated measured human PTGS2 ChEMBL structure set (n={len(df):,})',fontsize=12); fig.tight_layout(); fig.savefig(out/'chemical_properties.png',dpi=160); plt.close(fig)
fig,ax=plt.subplots(figsize=(8,3.3)); ax.axis('off'); names=['ChEMBL\nactivity','Quality filters\n+ labels','RDKit\nfeatures','Scaffold\nholdout','ML\nbenchmark','Evidence\nworkbench']; xs=np.linspace(.08,.92,len(names))
for i,(x,t) in enumerate(zip(xs,names)):
 ax.text(x,.52,t,ha='center',va='center',color='#e4f3eb',fontsize=9,bbox=dict(boxstyle='round,pad=.7',facecolor='#102a20',edgecolor='#4bb58e',linewidth=1.3))
 if i<len(xs)-1:ax.annotate('',xy=(xs[i+1]-.07,.52),xytext=(x+.07,.52),arrowprops=dict(arrowstyle='->',color='#86dcb7',lw=1.5))
ax.set_xlim(0,1);ax.set_ylim(0,1);fig.tight_layout();fig.savefig(out/'pipeline_workflow.png',dpi=160,transparent=True);plt.close(fig)
import json, networkx as nx
with open(ROOT/'results/reports/model_metrics.json') as f: metrics=json.load(f)
cm=np.array(metrics['primary_models']['Random forest']['confusion_matrix_tn_fp_fn_tp'])
fig,ax=plt.subplots(figsize=(4.2,3.8)); im=ax.imshow(cm,cmap='Greens'); ax.set_xticks([0,1],['Predicted weak','Predicted strong']); ax.set_yticks([0,1],['Observed weak','Observed strong']); ax.set_title('Random forest · scaffold test');
for i in range(2):
 for j in range(2):ax.text(j,i,str(cm[i,j]),ha='center',va='center',color='white' if cm[i,j]>cm.max()*.5 else '#133329',fontsize=14)
fig.colorbar(im,ax=ax,fraction=.045);fig.tight_layout();fig.savefig(out/'confusion_matrix.png',dpi=160);plt.close(fig)
G=nx.read_graphml(ROOT/'data/processed/knowledge_graph.graphml');focus=['plant:curcuma_longa','compound:curcumin','target:PTGS2']; keep=set(focus)
for n,d in G.nodes(data=True):
 if d.get('kind')=='compound' and n not in keep and G.has_edge(n,'target:PTGS2'):keep.add(n)
 if len(keep)>=10:break
H=G.subgraph(keep).copy();pos=nx.spring_layout(H,seed=11,k=.9)
fig,ax=plt.subplots(figsize=(9,5));cols=[{'plant':'#52d9a4','compound':'#73cede','target':'#dcc57d','prediction':'#df9c84'}.get(H.nodes[n].get('kind'),'#73cede') for n in H.nodes]
nx.draw_networkx_nodes(H,pos,node_color=cols,node_size=700,alpha=.93,ax=ax);labels={n:H.nodes[n].get('label',n).split(' ')[0][:19] for n in H.nodes};nx.draw_networkx_labels(H,pos,labels=labels,font_size=7,font_color='#e4f3eb',ax=ax)
for u,v,d in H.edges(data=True):nx.draw_networkx_edges(H,pos,edgelist=[(u,v)],edge_color='#82bba0',arrows=True,arrowsize=12,ax=ax,connectionstyle='arc3,rad=.08')
ax.set_axis_off();fig.patch.set_facecolor('#071412');ax.set_facecolor('#071412');fig.tight_layout();fig.savefig(out/'knowledge_graph.png',dpi=160,facecolor=fig.get_facecolor());plt.close(fig)
# A separate CPIC/ClinVar component, intentionally disconnected from the plant–assay pilot.
pgx=[n for n in G.nodes if str(n).startswith('pgx:')];H=G.subgraph(pgx).copy();pos=nx.spring_layout(H,seed=14,k=1.0,iterations=120)
kind_colors={'pharmacogene':'#52d9a4','sequence_variant':'#d6bd77','star_allele':'#73cede','drug':'#df9c84','clinical_guideline':'#b593dd','guideline_recommendation':'#e6a97b'}
fig,ax=plt.subplots(figsize=(9,4.8));cols=[kind_colors.get(H.nodes[n].get('kind'),'#73cede') for n in H.nodes]
nx.draw_networkx_nodes(H,pos,node_color=cols,node_size=1150,alpha=.95,ax=ax)
short={'pgx:gene:CYP2C19':'CYP2C19','pgx:variant:rs4244285':'rs4244285','pgx:allele:CYP2C19*2':'*2 · no function','pgx:drug:clopidogrel':'Clopidogrel','pgx:guideline:PA166251443':'CPIC guideline','pgx:recommendation:8609169':'Intermediate · ACS/PCI','pgx:recommendation:8609171':'Poor · ACS/PCI'}
nx.draw_networkx_labels(H,pos,labels={n:short.get(n,H.nodes[n].get('label',n)) for n in H.nodes},font_size=8,font_color='#e4f3eb',ax=ax)
for u,v,d in H.edges(data=True):nx.draw_networkx_edges(H,pos,edgelist=[(u,v)],edge_color='#82bba0',arrows=True,arrowsize=13,ax=ax,connectionstyle='arc3,rad=.08')
ax.set_axis_off();fig.patch.set_facecolor('#071412');ax.set_facecolor('#071412');fig.tight_layout();fig.savefig(out/'pharmacogenomics_graph.png',dpi=160,facecolor=fig.get_facecolor());plt.close(fig)
# Training-only scaffold-CV sensitivity; no compound-evidence composite ranking.
hp=metrics['hyperparameter_sensitivity_training_scaffold_cv']; labels=[f"leaf={x['parameters']['min_samples_leaf']} · {x['parameters']['max_features']}\n{ x['parameters']['n_estimators']} trees" for x in hp]
fig,ax=plt.subplots(figsize=(8,4));x=np.arange(len(hp));w=.24
for j,(key,label,color) in enumerate([('mean_roc_auc','ROC-AUC','#53c99a'),('mean_pr_auc','PR-AUC','#76c5d7'),('mean_balanced_accuracy','Balanced accuracy','#d6bd77')]):ax.bar(x+(j-1)*w,[z[key] for z in hp],width=w,label=label,color=color)
ax.set_xticks(x,labels,fontsize=8);ax.set_ylim(0,1);ax.set_ylabel('Mean across 3 training-only scaffold folds');ax.set_title('Random-forest hyperparameter sensitivity · not test-set tuning');ax.legend(fontsize=8);ax.spines[['top','right']].set_visible(False);fig.tight_layout();fig.savefig(out/'model_sensitivity.png',dpi=160);plt.close(fig)
# Duplicate-structure aggregation sensitivity (separate report; never replaces the primary analysis).
dup_path=Path('results/reports/duplicate_sensitivity.json')
if dup_path.exists():
    dup=json.loads(dup_path.read_text())['strategies']
    order=['lowest_ic50','median_ic50','exclude_conflicting']
    pretty={'lowest_ic50':'Lowest IC50\n(primary)','median_ic50':'Median IC50','exclude_conflicting':'Conflicts\nexcluded'}
    fig,axs=plt.subplots(1,2,figsize=(10,3.9))
    x=np.arange(len(order));w=.38
    hold=[dup[k]['holdout_metrics']['roc_auc'] for k in order]
    cv=[dup[k]['three_fold_scaffold_cv']['roc_auc']['mean'] for k in order]
    cv_sd=[dup[k]['three_fold_scaffold_cv']['roc_auc']['sd'] for k in order]
    axs[0].bar(x-w/2,hold,w,label='Scaffold holdout',color='#53c99a')
    axs[0].bar(x+w/2,cv,w,yerr=cv_sd,capsize=3,label='3-fold scaffold CV',color='#76c5d7')
    axs[0].axhline(.5,ls='--',c='#777',lw=1);axs[0].set_xticks(x,[pretty[k] for k in order],fontsize=8)
    axs[0].set_ylim(0,1);axs[0].set_ylabel('ROC-AUC');axs[0].set_title('Aggregation rule: ranking metrics',fontsize=10);axs[0].legend(fontsize=8)
    bal=[dup[k]['holdout_metrics']['balanced_accuracy_at_0_5'] for k in order]
    mcc=[dup[k]['holdout_metrics']['matthews_corrcoef_at_0_5'] for k in order]
    axs[1].bar(x-w/2,bal,w,label='Balanced accuracy',color='#d6bd77')
    axs[1].bar(x+w/2,mcc,w,label='MCC',color='#b593dd')
    axs[1].set_xticks(x,[pretty[k] for k in order],fontsize=8);axs[1].set_ylim(0,1)
    axs[1].set_title('Same runs: threshold-0.5 operating point',fontsize=10);axs[1].legend(fontsize=8)
    for a in axs:a.spines[['top','right']].set_visible(False)
    fig.tight_layout();fig.savefig(out/'duplicate_sensitivity.png',dpi=160);plt.close(fig)
# Remove the superseded composite-weight plot if this script is rerun.
(out/'ranking_sensitivity.png').unlink(missing_ok=True)
