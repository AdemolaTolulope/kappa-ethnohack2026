from fastapi.testclient import TestClient
from backend.main import app
client=TestClient(app)

def test_home_and_metrics():
    assert client.get('/').status_code==200
    d=client.get('/api/overview').json()
    assert d['records']==3164
    assert d['metrics']['primary_models']['Random forest']['roc_auc']>.5
    assert d['metrics']['external_validation'].startswith('Not available')

def test_predict_rejects_invalid_smiles():
    r=client.post('/api/predict',json={'smiles':'invalid smiles'})
    assert r.status_code==400

def test_structure_endpoint_returns_rdkit_svg():
    r=client.get('/api/structure',params={'smiles':'CCO'})
    assert r.status_code==200
    assert 'svg' in r.headers['content-type']
    assert '<svg' in r.text

def test_data_quality_endpoint_reports_actual_pipeline_counts():
    d=client.get('/api/data-quality').json()
    assert d['raw_records']==7482
    assert d['curated_unique_structures']==3164
    assert d['duplicate_structure_records_removed']==497

def test_genomic_context_is_provenance_limited():
    d=client.get('/api/genomic-context').json()
    assert d['accession']=='P35354'
    assert d['gene']=='PTGS2'
    assert 'no variant-response' in d['evidence_scope']

def test_cpic_phenotype_recommendations_filtered_to_intended_context():
    r=client.get('/api/pharmacogenomics')
    assert r.status_code==200
    d=r.json()
    assert d['pair']['genesymbol']=='CYP2C19'
    assert d['drug']['name'].lower()=='clopidogrel'
    assert len(d['recommendations'])==2
    assert all(x['population']=='CVI ACS PCI ' for x in d['recommendations'])
    assert d['clinvar']['record']['accession']=='VCV000016897'
    # ClinVar's cached germline label is a disease-association call for an unspecified trait,
    # never a drug-response classification; it must not overwrite CPIC allele function.
    assert d['clinvar']['record']['germline_classification']['description'].startswith('Likely benign')
    assert d['allele']['clinicalfunctionalstatus']=='No function'
    assert 'not a drug-metabolizer function' in d['clinvar']['scope_note']

def test_graph_scopes_are_separate():
    pilot=client.get('/api/graph',params={'scope':'pilot'}).json()
    pgx=client.get('/api/graph',params={'scope':'pharmacogenomics'}).json()
    assert all(not x['id'].startswith('pgx:') for x in pilot['nodes'])
    assert all(x['id'].startswith('pgx:') for x in pgx['nodes'])
    assert any(x['id']=='pgx:variant:rs4244285' for x in pgx['nodes'])

def test_out_of_domain_control_is_withheld_by_the_live_app():
    r=client.post('/api/predict',json={'smiles':'OC[C@H]1O[C@@](CO)(O[C@H]2O[C@H](CO)[C@@H](O)[C@H](O)[C@H]2O)[C@@H](O)[C@@H]1O'})
    assert r.status_code==200
    d=r.json()
    assert d['max_training_similarity'] < d['score']['applicability_domain']['threshold']
    assert d['in_domain'] is False
    assert d['score']['candidate_priority_score'] is None

def test_ethnobotany_endpoint_serves_validated_records_with_boundaries():
    d = client.get('/api/ethnobotany').json()
    assert d['coverage']['records'] == 1
    rec = d['records'][0]
    assert rec['compound_linkage'] == 'not asserted'
    assert rec['is_efficacy_evidence'] is False
    assert 'not efficacy' in d['evidence_boundary']

def test_frontend_withholds_probability_outside_reference_range():
    html = client.get('/').text
    assert 'Not rankable · probability withheld' in html
    assert 'd.in_domain' in html

def test_frontend_renders_ethnobotany_provenance_ids():
    html = client.get('/').text
    # provenance must be traceable in the UI, not only in the JSON payload
    assert 'api/ethnobotany' in html
    assert 'r.claim_id' in html
    assert 'r.taxon' in html
