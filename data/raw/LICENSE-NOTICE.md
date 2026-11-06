# Licence notice for the cached source records in this directory

These files are **cached copies of third-party data**, not KAPPA data. KAPPA's MIT licence (see the repository
root `LICENSE`) applies to KAPPA's own code and documentation only. It does **not** relicense anything here.

| File | Source | Retrieved | Terms that apply |
|---|---|---|---|
| `chembl_ptgs2_ic50.jsonl` | ChEMBL REST API, target `CHEMBL230` (human PTGS2) | 2026-11-05 | ChEMBL data are released under **CC BY-SA 3.0**. Attribution to ChEMBL/EMBL-EBI is required, and derivative distributions of these records must carry the same licence. Re-check the current ChEMBL terms before any redistribution. |
| `cpic_cyp2c19_clopidogrel.json` | `https://api.cpicpgx.org/v1` (pair 110091, guideline 100411) | 2026-11-05 | CPIC curated content is **CC0 1.0**; CPIC asks for attribution, guideline version and access date, and warns that guidance may change. |
| `clinvar_cyp2c19_star2.json` | NCBI E-utilities ESummary, VCV000016897 | 2026-11-05 | NCBI public-domain-style terms; used for variant identity cross-reference only. |
| `uniprot_ptgs2_P35354.json` | UniProt REST, `P35354` | 2026-11-05 | **CC BY 4.0**, attribution required. |
| `pubchem_curcumin_CID969516.json` | PubChem, CID 969516 | 2026-11-05 | PubChem terms; small identity record used for illustration. |
| `wikidata_curcumin_taxon_check.json` | Wikidata Q312266 / Q42562 (P703) | 2026-11-05 | **CC0**. |

If these caches are published in a public repository, the CC BY-SA 3.0 obligation on the ChEMBL extract travels
with it: state the licence and the source alongside the file, do not imply that MIT covers it, and keep the
attribution visible. The alternative is to publish a code-only repository and let users re-fetch with
`python -m src.run_pipeline` (internet required on first run).

Full register, including rights caveats for the ethnobotanical article and the interpretive limits of each
source: `docs/provenance_register.md`, `docs/data_provenance.md`, `submission/third_party_disclosures.md`.
