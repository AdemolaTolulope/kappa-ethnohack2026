"""Evidence profile for research triage. Never collapse unrelated evidence into one score."""

def score_candidate(model_probability=None, max_similarity=None, applicability_threshold=None,
                    chemical_identity=None, observed_bioactivity=None,
                    pharmacogenomic_evidence=None, ethnobotanical_evidence=None):
    """Return separated evidence axes and a model-only score when inside the empirical AD.

    Similarity is an applicability diagnostic, not a positive activity feature. Identity,
    ethnobotanical occurrence and PGx relevance are context, not activity labels. Missing
    evidence is explicit and never imputed as zero or treated as negative biology.
    """
    in_domain=(max_similarity is not None and applicability_threshold is not None and max_similarity>=applicability_threshold)
    missing=[]
    if chemical_identity is None: missing.append('No source-backed chemical identifier match')
    if observed_bioactivity is None: missing.append('No exact-structure measured PTGS2 record found in the cached subset')
    if pharmacogenomic_evidence is None: missing.append('No candidate-linked pharmacogenomic association; separate CYP2C19-clopidogrel demo is unrelated')
    if ethnobotanical_evidence is None: missing.append('No plant/use provenance linked to this submitted structure')
    elif ethnobotanical_evidence.get('status','').startswith('plant-level'): missing.append('Ethnobotanical record is plant-level only, not compound-specific evidence')
    return {
      'candidate_priority_score':float(model_probability) if model_probability is not None and in_domain else None,
      'score_basis':'Uncalibrated model probability only; never a clinical or efficacy score. No composite evidence weights.',
      'model_prediction':{'probability_active_uncalibrated':None if model_probability is None else float(model_probability),
                          'rankable_within_empirical_domain':bool(in_domain)},
      'applicability_domain':{'max_training_tanimoto':None if max_similarity is None else float(max_similarity),
                              'threshold':None if applicability_threshold is None else float(applicability_threshold),
                              'status':'within empirical reference range' if in_domain else 'outside empirical reference range or unavailable',
                              'interpretation':'Relative similarity diagnostic, not a validated confidence guarantee.'},
      'chemical_identity':chemical_identity or {'status':'structure syntax validated only; named identity unconfirmed'},
      'observed_bioactivity':observed_bioactivity or {'status':'not found in loaded subset; not evidence of inactivity'},
      'pharmacogenomic_evidence':pharmacogenomic_evidence or {'status':'not linked to candidate','note':'The separate CYP2C19-clopidogrel guideline demo must not be connected to curcumin or PTGS2.'},
      'ethnobotanical_evidence':ethnobotanical_evidence or {'status':'not linked to submitted structure'},
      'missing_evidence':missing,
      'uncertainty_and_limitations':['Model probabilities are not calibrated.','Single-target ChEMBL biochemical endpoint; no clinical response inference.',
          'Assay heterogeneity and literature selection bias remain.','No experimental validation performed.']
    }
