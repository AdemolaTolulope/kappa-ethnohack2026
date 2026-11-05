# Data files and evidence boundaries

- `raw/chembl_ptgs2_ic50.jsonl`: cached ChEMBL REST activity response with source IDs retained.
- `raw/uniprot_ptgs2_P35354.json`: human PTGS2 protein identity record, not a variant-response association.
- `raw/pubchem_curcumin_CID969516.json`: PubChem property/structure cross-check for illustrative curcumin.
- `raw/wikidata_curcumin_taxon_check.json`: archived SPARQL response for P703 occurrence statement; community-maintained claim, not efficacy.
- `raw/cpic_cyp2c19_clopidogrel.json`: verified CPIC gene, *2 allele, drug, pair, guideline and recommendation API records; separate from the phytochemical pilot.
- `raw/clinvar_cyp2c19_star2.json`: NCBI ClinVar ESummary identity cross-reference for c.681G>A / rs4244285 / *2. Its germline classification is 'Likely benign; other' (evaluated 2018-08-07) for a not-specified trait; that is a disease-association label, not a drug-response classification and not a contradiction of CPIC's 'no function' allele call.
- `processed/ethnobotanical_claims.json`: one secondary-source use report with citation, missing locality/community context and efficacy limits.
- `processed/ptgs2_curated.csv`: executed assay dataset; one exact canonical structure representative per row.
- `processed/knowledge_graph.graphml`: source-bearing graph export; CPIC/ClinVar PGx nodes form a separate disconnected component.

Licensing and source conditions are resource-specific. See `../docs/provenance_register.md` and `../docs/data_provenance.md`; KAPPA code licensing does not relicense external data or grant cultural access/consent.
