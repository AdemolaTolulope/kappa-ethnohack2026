from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pathlib import Path
P=Path(__file__).resolve().parents[1]; r=Presentation();r.slide_width=Inches(13.333);r.slide_height=Inches(7.5)
BG=RGBColor(7,20,18); PANEL=RGBColor(14,33,28); MINT=RGBColor(82,217,164); CYAN=RGBColor(115,206,220); WHITE=RGBColor(232,245,239); MUTED=RGBColor(151,177,164); GOLD=RGBColor(220,197,125)
def shape(slide,x,y,w,h,color,rounded=False):
 s=slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h));s.fill.solid();s.fill.fore_color.rgb=color;s.line.fill.background();return s
def text(slide,x,y,w,h,txt,size=16,color=WHITE,bold=False,font='Aptos',align=None):
 box=slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h));tf=box.text_frame;tf.clear();tf.word_wrap=True
 for i,line in enumerate(txt.split('\n')):
  p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.text=line;p.font.name=font;p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=color;p.space_after=Pt(6)
  if align is not None:p.alignment=align
 return box
def base(num,title,kicker='KAPPA · ETHNOHACK 2026'):
 s=r.slides.add_slide(r.slide_layouts[6]);s.background.fill.solid();s.background.fill.fore_color.rgb=BG
 shape(s,.42,.38,.06,.4,MINT);text(s,.65,.36,8,.26,kicker.upper(),9,MINT,True);text(s,.65,.76,12,.56,title,26,WHITE,True)
 shape(s,.55,7.13,12.25,.012,RGBColor(35,61,51));text(s,.65,7.18,10,.18,'Research prototype · computational hypotheses only · 05 NOV 2026',8,MUTED);text(s,12.0,7.16,.6,.18,f'{num:02d}/10',8,MUTED,align=PP_ALIGN.RIGHT)
 return s
# 1
s=base(1,'Make the evidence chain visible.','KAPPA · KNOWLEDGE-GUIDED PHYTO-PHARMACOGENOMIC ASSESSMENT')
text(s,.8,1.8,7.1,1.35,'KAPPA',48,MINT,True);text(s,.85,3.0,7.2,.85,'From medicinal plant context to testable molecular hypotheses.',25,WHITE,True);text(s,.85,4.25,6.6,.85,'An evidence-aware research workbench for natural-product discovery—not a treatment recommender.',16,MUTED)
shape(s,8.65,1.65,3.8,3.9,PANEL,True)
for i,(a,b) in enumerate([('PLANT','Curcuma longa'),('MOLECULE','Curcumin'),('BIOACTIVITY','Human PTGS2'),('MODEL','Scaffold-held-out ML')]):
 y=2.0+i*.8;text(s,9.0,y,1.2,.22,a,9,MINT,True);text(s,9.0,y+.22,2.9,.35,b,15,WHITE,True)
text(s,.85,6.25,7,.3,'ETHNOHACK 2026 · NATURAL PRODUCTS FOR DRUG DISCOVERY',12,GOLD,True)
#2
s=base(2,'The challenge is disconnected evidence.')
text(s,.8,1.65,5.2,.8,'Botanical records, compound structures, target assays and human genetics live in different systems—with different identifiers, evidence standards and reuse rules.',18,WHITE)
for i,(a,b) in enumerate([('Occurrence','Where botanical evidence appears'),('Chemistry','What structure the identifier means'),('Bioactivity','Which assay measured what'),('Pharmacogenomics','What variants may or may not support')]):
 x=6.45+(i%2)*3.0;y=1.65+(i//2)*1.55;shape(s,x,y,2.7,1.18,PANEL,True);text(s,x+.18,y+.14,2.3,.25,a,13,MINT,True);text(s,x+.18,y+.48,2.25,.52,b,11,MUTED)
text(s,.85,5.2,10.5,.58,'A plant occurrence is not a medicinal-use claim. A biochemical activity is not clinical efficacy.',20,GOLD,True)
text(s,.85,6.0,11,.48,'KAPPA makes those boundaries explicit while creating a reproducible path between datasets.',15,WHITE)
#3
s=base(3,'Reproducible hand-offs, not another mega-database.')
text(s,.85,1.55,5.3,1.1,'LOTUS, IMPPAT, ChEMBL, Open Targets and NP-KG already provide valuable data and integration capabilities.',18,WHITE)
text(s,.85,3.0,5.3,1.25,'KAPPA’s bounded contribution: connect a traceable occurrence context to a measured target-specific dataset, a scaffold-aware baseline, an applicability check, and evidence-tiered interpretation.',16,MUTED)
shape(s,6.65,1.5,5.7,4.45,PANEL,True)
for i,(n,t) in enumerate([('01','Live, attributable assay acquisition'),('02','RDKit features + duplicate controls'),('03','Scaffold-held-out RF vs baseline'),('04','Evidence-separated graph + applicability gate'),('05','Interactive research workbench')]):
 y=1.85+i*.77;text(s,7.0,y,.5,.3,n,12,MINT,True);text(s,7.65,y,4.2,.42,t,14,WHITE,True)
text(s,.85,5.9,10,.5,'Integration/reproducibility work—not a claim to be the first AI, knowledge graph or medicinal-plant database.',12,GOLD)
#4
s=base(4,'One pipeline. Provenance at every hand-off.')
labels=[('ChEMBL','7,482 target IC50 rows'),('Curate','3,164 structures'),('RDKit','7 descriptors + 512 bits'),('Split','Stratified scaffold groups'),('Benchmark','RF + logistic'),('Explore','API + graph + UI')]
for i,(a,b) in enumerate(labels):
 x=.55+i*2.1;shape(s,x,2.0,1.78,1.52,PANEL,True);text(s,x+.11,2.2,1.58,.3,a,13.5,MINT,True);text(s,x+.13,2.7,1.48,.57,b,11,WHITE)
 if i<5:text(s,x+1.81,2.55,.28,.3,'→',17,CYAN,True)
text(s,.9,4.3,11.4,.45,'Observed assay records  →  computed molecular features  →  held-out predictions',18,WHITE,True)
text(s,.9,5.05,11.1,.8,'Wikidata occurrence and one secondary ethnobotanical report are distinct plant-level evidence. A verified CYP2C19–clopidogrel guideline is a disconnected PGx demo; no link to curcumin/PTGS2.',15,MUTED)
#5
s=base(5,'Real data. Narrow, predeclared labels.')
for i,(n,v,sub) in enumerate([('RAW RECORDS','7,482','ChEMBL CHEMBL230 · human PTGS2'),('CURATED','3,164','canonical structures · duplicate-collapsed'),('ACTIVE BAND','2,505','IC50 ≤ 1 µM'),('INACTIVE BAND','659','IC50 ≥ 10 µM')]):
 x=.75+i*3.05;shape(s,x,1.65,2.75,1.3,PANEL,True);text(s,x+.2,1.85,2.4,.25,n,10,MINT,True);text(s,x+.2,2.1,2.3,.4,v,24,WHITE,True);text(s,x+.2,2.56,2.4,.28,sub,9,MUTED)
s.shapes.add_picture(str(P/'results/figures/chemical_properties.png'), Inches(.65), Inches(3.3), width=Inches(6.15));shape(s,7.2,3.35,5.2,2.6,PANEL,True);text(s,7.55,3.65,4.45,.35,'STRICT FILTERS',14,MINT,True);text(s,7.55,4.15,4.35,1.35,'Exact standard relation · nM units · single-protein assay · Homo sapiens · no duplicate/validity flags.\n\n1–10 µM grey band omitted—not relabelled inactive.',14,WHITE)
#6
s=base(6,'A genuine benchmark—with a visible caveat.')
s.shapes.add_picture(str(P/'results/figures/model_comparison.png'), Inches(.65), Inches(1.45), width=Inches(6.3))
for i,(a,b) in enumerate([('Random Forest','ROC-AUC 0.782 · PR-AUC 0.940'),('Logistic baseline','ROC-AUC 0.703 · PR-AUC 0.907'),('3-fold scaffold CV','Mean ROC 0.810 · PR 0.935')]):
 y=1.8+i*1.1;shape(s,7.1,y,5.2,.84,PANEL,True);text(s,7.4,y+.1,1.7,.25,a,12,MINT,True);text(s,9.0,y+.1,3,.43,b,13,WHITE,True)
text(s,7.2,5.35,5.05,.95,'Test prevalence 82.6% (PR baseline); balanced accuracy 0.637. Strong imbalance; internal data only, not external validation.\n\nAn earlier 0.832/0.966 pair is withdrawn: 7 protocols fail to reproduce it.',12,GOLD,True)
#7
s=base(7,'A graph that distinguishes identifiers from inference.')
s.shapes.add_picture(str(P/'results/figures/pharmacogenomics_graph.png'), Inches(.65), Inches(1.55), width=Inches(6.2))
text(s,6.9,1.8,5.2,.58,'Pharmacogenomic example: verified, contextual, separate.',18,WHITE,True)
text(s,6.9,2.6,5.0,1.9,'CYP2C19 *2 and clopidogrel are tied to CPIC guideline 100411 (CPIC A / ClinPGx 1A), with phenotype- and ACS/PCI-conditioned records only.\n\nNo patient genotype and no link to curcumin or PTGS2. ClinVar supplies variant identity only: its “Likely benign; other” label covers an unspecified disease trait, not drug-metabolizer function.',14,MUTED)
text(s,6.9,5.5,5.05,.4,'Missing evidence ≠ negative biology.',16,GOLD,True)
#8
s=base(8,'No composite ranking. Keep the prediction in scope.')
s.shapes.add_picture(str(P/'results/figures/duplicate_sensitivity.png'), Inches(.55), Inches(1.5), width=Inches(6.7))
shape(s,7.35,1.65,5.0,2.0,PANEL,True);text(s,7.7,1.95,4.3,.35,'CURCUMIN · RETROSPECTIVE',14,MINT,True);text(s,7.7,2.45,4.3,.72,'Exact training-structure overlap\nUncalibrated model-only output',18,WHITE,True)
text(s,7.45,4.15,4.85,1.05,'Applicability cutoff 0.324 is a training-only similarity diagnostic—not a calibrated confidence guarantee. No evidence-axis average.',14,WHITE)
text(s,.65,4.55,2.0,.3,'NOT CLAIMED',11,MINT,True)
text(s,.65,4.9,6.4,1.5,'• No blended evidence score or evidence-axis weighting\n• No calibrated probability and no validated domain boundary\n• No external, prospective, wet-lab or clinical validation\n• No individual treatment or pharmacogenomic prediction',13,MUTED)
text(s,7.45,5.5,4.85,.95,'Duplicate rule matters: 32 structures conflict. ROC 0.774–0.825, balanced accuracy 0.637–0.729 — ranking stable, threshold operating point not. Hyperparameter and time/document tests are internal ChEMBL, not external validation.',11.5,GOLD,True)
#9
s=base(9,'A working workbench—not a screenshot.')
s.shapes.add_picture(str(P/'frontend/screenshot.png') if (P/'frontend/screenshot.png').exists() else str(P/'results/figures/pipeline_workflow.png'), Inches(.7), Inches(1.5), width=Inches(5.9))
for i,(a,b) in enumerate([('Explore','Measured structures and descriptors'),('Inspect','Activity bands, assays and source IDs'),('Predict','SMILES + similarity + overlap flag'),('Traverse','Typed graph with evidence notes'),('Export','Curated CSV and reproducible metrics')]):
 y=1.55+i*.86;text(s,7.0,y,1.25,.28,a,12,MINT,True);text(s,8.4,y,3.9,.42,b,13,WHITE)
text(s,.85,6.15,11,.3,'Live demo: plant context → compound table → model card → graph → methods/provenance.',12,GOLD)
#10
s=base(10,'Useful now. Clear about what comes next.')
shape(s,.75,1.6,5.7,3.9,PANEL,True);text(s,1.05,1.92,4.8,.35,'DELIVERED',15,MINT,True);text(s,1.05,2.5,4.8,2.6,'Working API + UI (local)\n3,164-record data pipeline\nScaffold benchmark + 21 tests\nOut-of-domain refusal + ethnobotany validator\nEvidence graph + audit docs\n10-slide deck + rendered PDF',15,WHITE)
shape(s,6.9,1.6,5.7,3.9,PANEL,True);text(s,7.2,1.92,4.8,.35,'NEXT VALIDATION',15,CYAN,True);text(s,7.2,2.55,4.8,2.4,'Primary-source ethnobotanical evidence + permission\nIndependent assay/database evaluation\nClinical PGx update + indication checks\nProbability calibration and domain review\nProspective experimental follow-up',16,WHITE)
text(s,1.05,6.15,11.0,.35,'KAPPA turns fragmented evidence into a traceable research question—not a therapeutic promise.',17,GOLD,True)
r.save(P/'presentation/KAPPA_pitch_deck.pptx')
