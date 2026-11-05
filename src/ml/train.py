"""Auditable scaffold ML, calibration diagnostics and domain-shift evaluation."""
from pathlib import Path
import json, joblib
import numpy as np, pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (roc_auc_score,average_precision_score,precision_score,recall_score,f1_score,
    confusion_matrix,balanced_accuracy_score,brier_score_loss,log_loss,matthews_corrcoef)
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from src.chemistry.features import feature_vector, fingerprint, scaffold


def stratified_group_holdout(y,groups,n_splits=5,seed=17,fold=0):
    """Fixed stratified group holdout; no group can occur on both sides."""
    cv=StratifiedGroupKFold(n_splits=n_splits,shuffle=True,random_state=seed)
    return list(cv.split(np.zeros(len(y)),y,groups))[fold]

def random_forest(seed=17,n_estimators=350,min_samples_leaf=2,max_features='sqrt'):
    return RandomForestClassifier(n_estimators=n_estimators,min_samples_leaf=min_samples_leaf,
        class_weight='balanced',max_features=max_features,random_state=seed,n_jobs=-1)
def logistic(seed=17):
    return make_pipeline(SimpleImputer(),StandardScaler(),LogisticRegression(max_iter=2000,class_weight='balanced',C=.1,random_state=seed))
def eval_metrics(y,pred_prob):
    pred=(pred_prob>=.5).astype(int)
    return {'roc_auc':float(roc_auc_score(y,pred_prob)),'pr_auc':float(average_precision_score(y,pred_prob)),
        'precision_at_0_5':float(precision_score(y,pred,zero_division=0)),
        'recall_at_0_5':float(recall_score(y,pred,zero_division=0)),
        'f1_at_0_5':float(f1_score(y,pred,zero_division=0)),
        'balanced_accuracy_at_0_5':float(balanced_accuracy_score(y,pred)),
        'matthews_corrcoef_at_0_5':float(matthews_corrcoef(y,pred)),
        'confusion_matrix_tn_fp_fn_tp':confusion_matrix(y,pred,labels=[0,1]).tolist(),
        'brier_score_uncalibrated':float(brier_score_loss(y,pred_prob)),
        'log_loss_uncalibrated':float(log_loss(y,pred_prob,labels=[0,1])),
        'mean_predicted_probability':float(np.mean(pred_prob)),
        'observed_prevalence':float(np.mean(y))}
def tanimoto_matrix_max(query_fp,ref_fp):
    # Bit vectors in {0,1}; matrix multiplication gives intersection counts.
    q=np.asarray(query_fp,dtype=np.int32); r=np.asarray(ref_fp,dtype=np.int32)
    inter=q@r.T; denom=q.sum(1)[:,None]+r.sum(1)[None,:]-inter
    return (inter/np.maximum(denom,1)).max(axis=1)
def expected_calibration_error(y,p,n_bins=10):
    edges=np.linspace(0,1,n_bins+1); out=0.0; bins=[]
    for i in range(n_bins):
        mask=(p>=edges[i]) & ((p<edges[i+1]) if i<n_bins-1 else (p<=edges[i+1]))
        if mask.any():
            conf=float(p[mask].mean()); obs=float(y[mask].mean()); weight=float(mask.mean())
            out+=weight*abs(conf-obs);bins.append({'lower':float(edges[i]),'upper':float(edges[i+1]),'n':int(mask.sum()),'mean_probability':conf,'observed_rate':obs})
    return float(out),bins

def fit_eval(model,Xtr,ytr,Xte,yte):
    model.fit(Xtr,ytr); p=model.predict_proba(Xte)[:,1]
    return model,p,eval_metrics(yte,p)

def train_model(df, model_dir='models', result_dir='results/reports'):
    if len(df)<50 or df.label.nunique()!=2: raise ValueError(f'Need >=50 curated records and both labels; got {len(df)}')
    df=df.copy().reset_index(drop=True); df['scaffold']=df.canonical_smiles.map(scaffold)
    X=np.vstack(df.canonical_smiles.map(feature_vector)); y=df.label.to_numpy(); groups=df.scaffold.to_numpy(); documents=df.document_chembl_id.fillna('document_missing').astype(str).to_numpy()
    tr,te=stratified_group_holdout(y,groups,5,17,0)
    assert not (set(groups[tr]) & set(groups[te])), 'Scaffold leakage across primary holdout'
    assert not (set(df.iloc[tr].canonical_smiles) & set(df.iloc[te].canonical_smiles)), 'Exact-structure leakage'
    primary_models={'Random forest':random_forest(),'Logistic regression':logistic()}
    reports={}; fitted={}; test_probs={}
    for name,estimator in primary_models.items():
        fitted[name],test_probs[name],reports[name]=fit_eval(estimator,X[tr],y[tr],X[te],y[te])

    # Training-only stratified scaffold CV: same folds for RF and logistic regression.
    cv_splits=list(StratifiedGroupKFold(3,shuffle=True,random_state=29).split(X[tr],y[tr],groups[tr]))
    cv_report={name:[] for name in primary_models}; oof_similarity=[]
    fp=X[:,7:].astype(np.uint8)
    for fold,(a,b) in enumerate(cv_splits):
        ta,tb=tr[a],tr[b]
        for name,estimator in [('Random forest',random_forest(seed=29+fold)),('Logistic regression',logistic(seed=29+fold))]:
            m=estimator; m.fit(X[ta],y[ta]); pp=m.predict_proba(X[tb])[:,1]
            cv_report[name].append(eval_metrics(y[tb],pp))
        oof_similarity.extend(tanimoto_matrix_max(fp[tb],fp[ta]).tolist())
    ad_threshold=float(np.quantile(oof_similarity,.05))
    test_similarity=tanimoto_matrix_max(fp[te],fp[tr])

    # Hyperparameter sensitivity is measured only by training-partition scaffold CV.
    hp_grid=[{'n_estimators':200,'min_samples_leaf':1,'max_features':'sqrt'},
             {'n_estimators':350,'min_samples_leaf':2,'max_features':'sqrt'},
             {'n_estimators':350,'min_samples_leaf':5,'max_features':'sqrt'},
             {'n_estimators':500,'min_samples_leaf':5,'max_features':'log2'}]
    hp_results=[]
    for params in hp_grid:
        fold_metrics=[]
        for fold,(a,b) in enumerate(cv_splits):
            m=random_forest(seed=47+fold,**params);m.fit(X[tr[a]],y[tr[a]])
            pp=m.predict_proba(X[tr[b]])[:,1]; fold_metrics.append(eval_metrics(y[tr[b]],pp))
        hp_results.append({'parameters':params,'fold_metrics':fold_metrics,
          'mean_roc_auc':float(np.mean([z['roc_auc'] for z in fold_metrics])),
          'sd_roc_auc':float(np.std([z['roc_auc'] for z in fold_metrics],ddof=1)),
          'mean_pr_auc':float(np.mean([z['pr_auc'] for z in fold_metrics])),
          'mean_balanced_accuracy':float(np.mean([z['balanced_accuracy_at_0_5'] for z in fold_metrics]))})

    # Publication-disjoint stress test; additionally remove every training scaffold present in its test fold.
    doc_tr0,doc_te=stratified_group_holdout(y,documents,5,37,0)
    test_scaffolds=set(groups[doc_te]); doc_tr=np.asarray([i for i in doc_tr0 if groups[i] not in test_scaffolds])
    doc_holdout={'test_n':int(len(doc_te)),'test_document_count':int(len(set(documents[doc_te]))),
      'train_n_after_removing_shared_scaffolds':int(len(doc_tr)),
      'shared_scaffold_groups_removed_from_train':int(len(set(groups[doc_tr0])&test_scaffolds)),
      'scaffold_overlap_after_filter':int(len(set(groups[doc_tr])&set(groups[doc_te]))),
      'interpretation':'Internal ChEMBL publication-held-out stress test with scaffold-disjoint train/test. Not external database validation.'}
    if len(doc_tr)>=50 and len(np.unique(y[doc_tr]))==2 and len(np.unique(y[doc_te]))==2:
        dm=random_forest(seed=71);dm.fit(X[doc_tr],y[doc_tr]);dp=dm.predict_proba(X[doc_te])[:,1];doc_holdout['random_forest']=eval_metrics(y[doc_te],dp)
    else:doc_holdout['status']='insufficient class support; not scored'

    # Forward-in-time, same-database stress test; avoid scaffold overlap and make date/record caveat explicit.
    years=pd.to_numeric(df.document_year,errors='coerce').to_numpy(); temporal_test=np.where(years>=2019)[0]; temporal_old=np.where((years<2019)&np.isfinite(years))[0]
    temporal_train=np.asarray([i for i in temporal_old if groups[i] not in set(groups[temporal_test])])
    temporal={'cutoff':'2019-01-01; test publication year >= 2019, train < 2019',
      'test_n':int(len(temporal_test)),'train_n_after_scaffold_exclusion':int(len(temporal_train)),
      'missing_year_excluded':int(np.sum(~np.isfinite(years))),
      'shared_scaffold_groups_removed_from_train':int(len(set(groups[temporal_old])&set(groups[temporal_test]))),
      'scaffold_overlap_after_filter':int(len(set(groups[temporal_train])&set(groups[temporal_test]))),
      'interpretation':'Temporal stress test within ChEMBL, additionally scaffold-disjoint; not external validation. Canonical duplicate collapse retains one representative record chosen by lowest IC50, so publication year may not be first report.'}
    if len(temporal_train)>=50 and len(temporal_test)>=30 and len(np.unique(y[temporal_train]))==2 and len(np.unique(y[temporal_test]))==2:
        tm=random_forest(seed=83);tm.fit(X[temporal_train],y[temporal_train]);tp=tm.predict_proba(X[temporal_test])[:,1];temporal['random_forest']=eval_metrics(y[temporal_test],tp)
    else:temporal['status']='insufficient size/class support; not scored'

    # Uncalibrated probabilities are audited, not post-hoc calibrated on the test set.
    prevalence=float(y[tr].mean()); calibration={}
    for name,p in test_probs.items():
        ece,bins=expected_calibration_error(y[te],p)
        calibration[name]={'expected_calibration_error_10_equal_width_bins':ece,'reliability_bins':bins,
          'brier_skill_vs_train_prevalence_constant':float(1-brier_score_loss(y[te],p)/max(brier_score_loss(y[te],np.full(len(te),prevalence)),1e-12)),
          'note':'Brier/log-loss/ECE are descriptive on held-out data; no probability calibration was fitted.'}
    base_brier=float(brier_score_loss(y[te],np.full(len(te),prevalence)))
    base_logloss=float(log_loss(y[te],np.full(len(te),prevalence),labels=[0,1]))
    calibration['prevalence_baseline']={'train_prevalence':prevalence,'test_brier':base_brier,'test_log_loss':base_logloss}

    # Permutation importance (global model reliance) on primary holdout; never mechanistic proof.
    rng=np.random.default_rng(31); groups_to_test={k:[i] for i,k in enumerate(['MW','LogP','TPSA','HBD','HBA','Rotatable bonds','Fraction Csp3'])}
    groups_to_test['Morgan fingerprint block (512 bits)']=list(range(7,X.shape[1]));perm_importance={};best=fitted['Random forest']
    for name,cols in groups_to_test.items():
        drops=[]
        for _ in range(5):
            xp=X[te].copy();order=rng.permutation(len(te));xp[:,cols]=xp[order][:,cols]
            drops.append(float(reports['Random forest']['roc_auc']-roc_auc_score(y[te],best.predict_proba(xp)[:,1])))
        perm_importance[name]={'mean_roc_auc_drop':float(np.mean(drops)),'sd':float(np.std(drops))}

    model_bundle={'model':best,'training_smiles':df.iloc[tr].canonical_smiles.tolist(),
      'ad_threshold':ad_threshold,'ad_threshold_method':'5th percentile of max Morgan r2 Tanimoto similarities for training-only 3-fold scaffold out-of-fold molecules against their fold training set',
      'features':'7 RDKit descriptors + 512-bit Morgan radius-2 fingerprint','target':'ChEMBL CHEMBL230 human PTGS2','seed':17}
    Path(model_dir).mkdir(parents=True,exist_ok=True);joblib.dump(model_bundle,Path(model_dir)/'ptgs2_rf.joblib')
    report={'task':'Human PTGS2 biochemical IC50 activity-band classification','endpoint':'IC50 ≤ 1,000 nM vs ≥10,000 nM; grey zone omitted',
      'source':'ChEMBL REST API, target CHEMBL230','n_records':len(df),'n_active':int(y.sum()),'n_inactive':int((y==0).sum()),'overall_active_prevalence':float(y.mean()),
      'n_scaffolds':int(len(set(groups))),'train_n':len(tr),'test_n':len(te),'train_active_prevalence':prevalence,'test_active_prevalence':float(y[te].mean()),
      'test_scaffolds':int(len(set(groups[te]))),'split':'first fixed fold of StratifiedGroupKFold(n_splits=5, shuffle=True, seed=17), groups=Bemis-Murcko scaffold; exact canonical structures deduplicated before split',
      'seed':17,'scaffold_group_overlap':int(len(set(groups[tr])&set(groups[te]))),'cross_validation_training_scaffold_group':cv_report,
      'hyperparameter_sensitivity_training_scaffold_cv':hp_results,'primary_models':reports,
      'publication_and_scaffold_disjoint_stress_test':doc_holdout,'temporal_and_scaffold_disjoint_stress_test':temporal,
      'calibration_diagnostics':calibration,'ad_diagnostics':{'method':model_bundle['ad_threshold_method'],'threshold':ad_threshold,
        'holdout_test_below_threshold_fraction':float(np.mean(test_similarity<ad_threshold)),
        'test_max_similarity_quantiles':{str(q):float(np.quantile(test_similarity,q)) for q in [0,.05,.25,.5,.75,1]},
        'warning':'A relative similarity diagnostic, not a calibrated probability of correctness or validated domain boundary.'},
      'global_grouped_permutation_importance':perm_importance,
      'best_model':'Random Forest as prespecified primary; no test-set model selection. Hyperparameter sensitivity reported on training-only CV.',
      'external_validation':'Not available/performed. Publication- and temporal-held-out analyses are internal ChEMBL stress tests, not external validation.'}
    Path(result_dir).mkdir(parents=True,exist_ok=True);Path(result_dir,'model_metrics.json').write_text(json.dumps(report,indent=2))
    _figures(y,te,test_probs,reports,perm_importance,calibration,base_brier)
    return report,df,best,X,tr,te

def _figures(y,te,test_probs,reports,perm_importance,calibration,base_brier):
    import matplotlib.pyplot as plt
    from sklearn.metrics import roc_curve,precision_recall_curve
    from sklearn.calibration import calibration_curve
    Path('results/figures').mkdir(parents=True,exist_ok=True)
    fig,axs=plt.subplots(1,2,figsize=(9,3.8))
    for name,p in test_probs.items():
        fpr,tpr,_=roc_curve(y[te],p);prec,rec,_=precision_recall_curve(y[te],p)
        axs[0].plot(fpr,tpr,label=f"{name} (AUC={reports[name]['roc_auc']:.3f})");axs[1].plot(rec,prec,label=f"{name} (AP={reports[name]['pr_auc']:.3f})")
    axs[0].plot([0,1],[0,1],ls='--',c='#777',lw=1);axs[0].set(xlabel='False positive rate',ylabel='True positive rate',title='ROC · stratified scaffold holdout')
    axs[1].axhline(float(np.mean(y[te])),ls='--',c='#777',lw=1,label=f"Test prevalence {np.mean(y[te]):.2f}");axs[1].set(xlabel='Recall',ylabel='Precision',title='Precision–recall')
    for ax in axs:ax.legend(fontsize=7);ax.spines[['top','right']].set_visible(False)
    fig.tight_layout();fig.savefig('results/figures/roc_pr_curves.png',dpi=160);plt.close(fig)
    fig,axs=plt.subplots(1,2,figsize=(9,3.8))
    for name,p in test_probs.items():
        prob_true,prob_pred=calibration_curve(y[te],p,n_bins=10,strategy='uniform');axs[0].plot(prob_pred,prob_true,'o-',label=name)
        axs[1].hist(p,bins=np.linspace(0,1,11),alpha=.55,label=name)
    axs[0].plot([0,1],[0,1],ls='--',c='#777');axs[0].set(xlabel='Mean predicted probability',ylabel='Observed positive frequency',title='Reliability (uncalibrated)');axs[1].set(xlabel='Predicted probability',ylabel='Molecules',title='Prediction distribution')
    for ax in axs:ax.legend(fontsize=7);ax.spines[['top','right']].set_visible(False)
    fig.tight_layout();fig.savefig('results/figures/calibration_diagnostics.png',dpi=160);plt.close(fig)
    imp=sorted(perm_importance.items(),key=lambda x:x[1]['mean_roc_auc_drop']);fig,ax=plt.subplots(figsize=(7,4))
    ax.barh([x[0] for x in imp],[x[1]['mean_roc_auc_drop'] for x in imp],color='#4fc99a');ax.axvline(0,c='#777',lw=1);ax.set_xlabel('Decrease in scaffold-test ROC-AUC after permutation');ax.set_title('Grouped permutation importance · descriptive only');fig.tight_layout();fig.savefig('results/figures/feature_importance.png',dpi=160);plt.close(fig)
    names=list(reports);fig,ax=plt.subplots(figsize=(7,4));vals=[reports[n]['roc_auc'] for n in names]
    ax.bar(names,vals,color=['#0b8767','#6880a5']);ax.axhline(.5,c='#777',ls='--',lw=1);ax.set_ylim(0,1);ax.set_ylabel('Scaffold test ROC-AUC');ax.set_title('Measured human PTGS2 IC50 classification')
    for i,v in enumerate(vals):ax.text(i,v+.025,f'{v:.3f}',ha='center')
    fig.tight_layout();fig.savefig('results/figures/model_comparison.png',dpi=160);plt.close(fig)
    cms=reports['Random forest']['confusion_matrix_tn_fp_fn_tp'];cm=np.asarray(cms)
    fig,ax=plt.subplots(figsize=(4.2,3.8));im=ax.imshow(cm,cmap='Greens');ax.set_xticks([0,1],['Predicted weak','Predicted strong']);ax.set_yticks([0,1],['Observed weak','Observed strong']);ax.set_title('RF · stratified scaffold test')
    for i in range(2):
      for j in range(2):ax.text(j,i,str(cm[i,j]),ha='center',va='center',color='white' if cm[i,j]>cm.max()*.5 else '#133329',fontsize=14)
    fig.colorbar(im,ax=ax,fraction=.045);fig.tight_layout();fig.savefig('results/figures/confusion_matrix.png',dpi=160);plt.close(fig)
