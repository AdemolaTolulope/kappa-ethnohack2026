"""Provenance-checked ethnobotanical records.

Scope, stated once and enforced in code: a record here documents a *reported practice in a named
source*. It is not evidence of efficacy, not evidence of safety, and not evidence that any specific
compound mediates the reported use. Those are different claims, and this module refuses to blur them.

The package validates the cached record file, exposes a small query surface, and fails loudly if a
record is missing provenance, cites no source, or asserts a compound-level link without evidence.
"""
from __future__ import annotations

import json
from pathlib import Path

REQUIRED_TOP_LEVEL = ('retrieval_date', 'records')
REQUIRED_RECORD_FIELDS = ('claim_id', 'taxon', 'claim_type', 'reported_indication_as_published',
                          'evidence_status', 'source', 'limitations')
REQUIRED_SOURCE_FIELDS = ('authors', 'year', 'title', 'journal')

DEFAULT_PATH = 'data/processed/ethnobotanical_claims.json'


class ClaimValidationError(ValueError):
    """Raised when a cached ethnobotanical record lacks the provenance this project requires."""


def _citation(source):
    authors = source.get('authors') or []
    first = authors[0] if authors else 'Unknown author'
    return f"{first} et al. ({source.get('year')}), {source.get('journal')}"


def load_claims(path=DEFAULT_PATH):
    """Load and validate the cached records. Raises ClaimValidationError on any missing requirement."""
    p = Path(path)
    if not p.exists():
        raise ClaimValidationError(f'ethnobotanical record file not found: {p}')
    payload = json.loads(p.read_text())
    missing = [k for k in REQUIRED_TOP_LEVEL if k not in payload]
    if missing:
        raise ClaimValidationError(f'missing top-level fields: {missing}')
    records = payload['records']
    if not isinstance(records, list) or not records:
        raise ClaimValidationError('no ethnobotanical records present')
    seen = set()
    for rec in records:
        absent = [k for k in REQUIRED_RECORD_FIELDS if not rec.get(k)]
        if absent:
            raise ClaimValidationError(f"{rec.get('claim_id', '<unnamed>')}: missing fields {absent}")
        if rec['claim_id'] in seen:
            raise ClaimValidationError(f"duplicate claim_id {rec['claim_id']}")
        seen.add(rec['claim_id'])
        src_absent = [k for k in REQUIRED_SOURCE_FIELDS if not rec['source'].get(k)]
        if src_absent:
            raise ClaimValidationError(f"{rec['claim_id']}: source missing {src_absent}")
        if not rec['source'].get('url') and not rec['source'].get('doi'):
            raise ClaimValidationError(f"{rec['claim_id']}: source has neither URL nor DOI")
        if not isinstance(rec['limitations'], list) or not rec['limitations']:
            raise ClaimValidationError(f"{rec['claim_id']}: limitations must be a non-empty list")
        # A plant-level report must never be silently attached to a specific compound.
        if rec.get('compound_linkage') not in (None, 'not asserted'):
            raise ClaimValidationError(
                f"{rec['claim_id']}: compound_linkage must be absent or 'not asserted' "
                f"(got {rec['compound_linkage']!r}); this project has no evidence for such a link")
    return payload


def summarise(record):
    """Return the record's evidence identity: what kind of statement it is, and what it is not."""
    return {
        'claim_id': record['claim_id'],
        'taxon': record['taxon'],
        'evidence_class': 'documented traditional-use report (secondary source)',
        'claim_type_as_published': record['claim_type'],
        'reported_indication_as_published': record['reported_indication_as_published'],
        'reported_material_and_preparation': record.get('reported_material_and_preparation'),
        'context_as_published': record.get('source_geographic_context'),
        'citation': _citation(record['source']),
        'source_url_or_doi': record['source'].get('url') or record['source'].get('doi'),
        'source_year': record['source'].get('year'),
        'evidence_status': record['evidence_status'],
        'compound_linkage': record.get('compound_linkage', 'not asserted'),
        'limitations': list(record['limitations']),
        'is_efficacy_evidence': False,
        'is_safety_evidence': False,
        'is_compound_specific_evidence': False,
        'is_clinical_evidence': False,
        'interpretation': ('A reported practice in a secondary source. It does not demonstrate efficacy, '
                           'safety, a mechanism, or that any constituent compound is responsible.'),
    }


def claims_for_taxon(taxon, path=DEFAULT_PATH):
    payload = load_claims(path)
    return [summarise(r) for r in payload['records']
            if r['taxon'].split()[0].lower() == taxon.split()[0].lower()]


def coverage_note(path=DEFAULT_PATH):
    """Honest coverage statement, used by the API and the UI so the limit travels with the data."""
    try:
        payload = load_claims(path)
        n = len(payload['records'])
        taxa = sorted({r['taxon'] for r in payload['records']})
        sources = sorted({_citation(r['source']) for r in payload['records']})
        return {'records': n, 'taxa': taxa, 'sources': sources,
                'status': 'limited demonstration corpus — not a systematic ethnobotanical survey',
                'retrieval_date': payload.get('retrieval_date')}
    except ClaimValidationError as exc:
        return {'records': 0, 'status': f'unavailable: {exc}', 'taxa': [], 'sources': []}


if __name__ == '__main__':
    payload = load_claims()
    print(json.dumps(coverage_note(), indent=2))
    for rec in payload['records']:
        print(json.dumps(summarise(rec), indent=2))
