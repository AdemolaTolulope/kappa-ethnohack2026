"""Provenance-bearing graph: plant use, occurrence, measured activity and separate PGx demo stay distinct."""
import networkx as nx

def build_graph(compounds,pgx_evidence=None,ethnobotanical_claim=None):
    g=nx.MultiDiGraph()
    g.add_node('plant:curcuma_longa',kind='plant',label='Curcuma longa L. (Wikidata Q42562)',source='Wikidata taxon Q42562; checked 2026-11-05')
    g.add_node('compound:curcumin',kind='compound',label='Curcumin (Wikidata Q312266)',source='PubChem CID 969516; ChEMBL structure cross-reference; Wikidata Q312266')
    g.add_edge('plant:curcuma_longa','compound:curcumin',relation='stated_in_taxon',evidence='Wikidata P703 (found in taxon) Q312266 → Q42562; referenced community-maintained claim. Occurrence is not efficacy.',source='Wikidata Q312266; live SPARQL check 2026-11-05')
    g.add_node('target:PTGS2',kind='target',label='PTGS2 / COX-2',source='UniProt P35354; ChEMBL CHEMBL230')
    g.add_node('task:chembl_model',kind='prediction',label='PTGS2 activity model',source='KAPPA scaffold benchmark; uncalibrated inference')
    g.add_edge('compound:curcumin','target:PTGS2',relation='model_score_only',evidence='In-silico activity-band score; exact training structure overlap; not a measured compound-target claim.',source='KAPPA ML; retrospective')
    if ethnobotanical_claim:
        claim=ethnobotanical_claim
        uid='use:'+claim['claim_id'];g.add_node(uid,kind='traditional_use_report',label=claim['reported_indication_as_published'],source=claim['source']['authors'][0]+' et al. ('+str(claim['source']['year'])+')',claim_id=claim['claim_id'],preparation=claim['reported_material_and_preparation'],context=claim['source_geographic_context'],evidence_status=claim['evidence_status'])
        g.add_edge('plant:curcuma_longa',uid,relation='reported_use_in_secondary_source',evidence='Literature report only; underlying source and locality are described with limits in data/processed/ethnobotanical_claims.json. Not efficacy.',source=claim['source']['url'])
    for c in compounds[:60]:
        node='compound:'+str(c['chembl_id']);g.add_node(node,kind='compound',label=c['name'],smiles=c['smiles'],source='ChEMBL')
        g.add_edge(node,'target:PTGS2',relation='measured_activity',evidence=f"ChEMBL activity {c['activity_id']}; IC50 {c['ic50_nM']} nM",source='ChEMBL',activity_id=c['activity_id'])
    # Independent clinical PGx example: it is deliberately a disconnected component from the phytochemical pilot.
    if pgx_evidence:
        resources=pgx_evidence['resources'];gene=resources['gene'][0];allele=resources['allele'][0];drug=resources['drug'][0];pair=resources['pair'][0];guideline=resources['guideline'][0]
        gn='pgx:gene:CYP2C19';an='pgx:allele:CYP2C19*2';dn='pgx:drug:clopidogrel';gd='pgx:guideline:'+str(guideline['clinpgxid'])
        g.add_node(gn,kind='pharmacogene',label='CYP2C19',source='CPIC API gene record; HGNC '+str(gene.get('hgncid')))
        g.add_node(an,kind='star_allele',label='CYP2C19 *2',source='CPIC API allele record; version '+str(allele.get('version')),function=allele.get('clinicalfunctionalstatus'))
        clinvar_path=__import__('pathlib').Path(__file__).resolve().parents[2]/'data/raw/clinvar_cyp2c19_star2.json'
        if clinvar_path.exists():
            cv=__import__('json').loads(clinvar_path.read_text()); v=cv['record']['variation_set'][0]
            dbsnp=next((x['db_id'] for x in v.get('variation_xrefs',[]) if x.get('db_source')=='dbSNP'),None)
            if dbsnp:
                vn='pgx:variant:rs'+str(dbsnp);g.add_node(vn,kind='sequence_variant',label='rs'+str(dbsnp)+' · '+v.get('cdna_change',''),source='NCBI ClinVar '+cv['record']['accession'],url='https://www.ncbi.nlm.nih.gov/clinvar/'+cv['record']['accession']+'/',germline_classification=(cv['record'].get('germline_classification') or {}).get('description'),germline_last_evaluated=(cv['record'].get('germline_classification') or {}).get('last_evaluated'),note='Molecular identity cross-reference only; ClinVar germline classification concerns a not-specified disease trait, not CYP2C19 drug-metabolizer function.')
                g.add_edge(gn,vn,relation='variant_in_gene',evidence=cv['scope_note'],source=cv['request_url'])
                g.add_edge(vn,an,relation='listed_as_star_allele_alias',evidence='ClinVar variant aliases include CYP2C19*2; this is nomenclature/identity cross-reference, not a response classification.',source='NCBI ClinVar '+cv['record']['accession'])
        g.add_node(dn,kind='drug',label='Clopidogrel',source='CPIC API drug record; '+str(drug.get('drugid')))
        g.add_node(gd,kind='clinical_guideline',label=guideline.get('name'),source='CPIC guideline '+str(guideline.get('clinpgxid')),url=guideline.get('url'),version=str(guideline.get('version')))
        g.add_edge(gn,an,relation='curated_star_allele_function',evidence='CPIC assigns *2 no function; an allele alone is not a diplotype/phenotype.',source='CPIC API allele record; citations '+','.join(allele.get('citations',[])))
        g.add_edge(gn,dn,relation='curated_gene_drug_pair',evidence=f"CPIC level {pair.get('cpiclevel')}; ClinPGx level {pair.get('clinpgxlevel')}; pair {pair.get('pairid')}; citation PMID {','.join(pair.get('citations',[]))}",source='CPIC API')
        g.add_edge(dn,gd,relation='covered_by_guideline',evidence='Published CYP2C19–clopidogrel pharmacogenomic guideline; not linked to curcumin/PTGS2.',source='CPIC API')
        for rec in resources['recommendation']: 
            phenotype=rec.get('phenotypes',{}).get('CYP2C19')
            if phenotype not in ('Intermediate Metabolizer','Poor Metabolizer') or rec.get('population')!='CVI ACS PCI ':continue
            rn='pgx:recommendation:'+str(rec['id']);g.add_node(rn,kind='guideline_recommendation',label=phenotype+' · '+str(rec.get('classification')),source='CPIC recommendation record '+str(rec['id']),recommendation=rec.get('drugrecommendation'),population_context=rec.get('population'),context_note=rec.get('comments'),implication=rec.get('implications',{}).get('CYP2C19'))
            g.add_edge(gd,rn,relation='contains_guideline_recommendation',evidence=rec.get('drugrecommendation',''),source='CPIC API; '+str(guideline.get('url')))
            g.add_edge(gn,rn,relation='phenotype_conditioned_association',evidence=f"CYP2C19 {phenotype}; context {rec.get('population')}; not a patient-specific call.",source='CPIC guideline recommendation')
    return g

def graph_payload(g):
    # Edge topology keys must stay authoritative: provenance is emitted as `source_reference`
    # so that `source`/`target` always remain node ids for clients.
    edges=[]
    for u,v,d in g.edges(data=True):
        attrs=dict(d);ref=attrs.pop('source',None)
        edges.append({'source':u,'target':v,**attrs,'source_reference':ref})
    return {'nodes':[{'id':n,**d} for n,d in g.nodes(data=True)],'edges':edges}
