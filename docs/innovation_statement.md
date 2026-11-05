# KAPPA — problem statement and innovation statement

## 1. The problem, stated narrowly enough to be testable

A researcher who wants to know whether a medicinal plant is worth experimental follow-up must assemble, by
hand, at least six different kinds of statement:

1. the plant is *this* taxon (**occurrence**);
2. a use is documented in a *specific* source (**traditional-use report**);
3. these compounds occur in it (**phytochemistry**);
4. this structure is *that* molecule (**chemical identity**);
5. this molecule was measured against a target, with an assay method and a value (**measured activity**);
6. this gene/drug pair has curated clinical guidance (**pharmacogenomic evidence**).

Each statement has a different truth condition, a different licence, and a different failure mode. The
practical consequence, documented in the resources themselves, is that evidence is often joined without
recording *which kind* of statement a link is: LOTUS exists because structure–organism links were missing and
references were too poorly standardised to trace [@rutz2022lotus]; occurrence-oriented resources need explicit
downstream work to handle "bias, redundancy, and evidential heterogeneity" before prioritisation
[@compoundcentric2026]; NPASS deliberately labels similarity-estimated activity differently from measured
activity [@zhao2023npass]; and literature-mined natural-product graphs acknowledge extraction error and
conflicting edges [@taneja2022npkg].

That is the problem KAPPA addresses: **not a shortage of data, but the absence of an operational contract
that keeps evidence types separate while still producing a usable prioritisation**.

## 2. What KAPPA does about it

KAPPA is a runnable research workbench that (a) keeps eight evidence classes separate in code, API and UI,
(b) attaches source and qualification to each, (c) produces exactly one quantitative prioritisation signal —
an uncalibrated activity-band estimate — and only where an empirical similarity reference says the molecule is
not too far from the training chemistry, and (d) states what is missing rather than scoring around it.

| Evidence class | KAPPA mechanism | Never used as |
|---|---|---|
| Botanical occurrence | Wikidata P703 triple with source and date | proof of use |
| Documented traditional use | one attributed secondary-source record with its limits | efficacy |
| Phytochemical occurrence | the compound's identity, described as identity | measured presence in a product |
| Measured biochemical activity | ChEMBL activity/assay/document IDs, operational band | efficacy or selectivity |
| Computational activity estimate | uncalibrated Random Forest probability + applicability status | measured activity |
| Target identity | UniProt/ChEMBL identifiers | target–disease evidence |
| Genetic association | (deliberately absent for curcumin/PTGS2) | pharmacogenomic guidance |
| PGx guideline evidence | separate, verified CPIC CYP2C19–clopidogrel demo | curcumin evidence |

## 3. Innovation statement (defensible form)

> KAPPA's contribution is an **evidence-type contract with an explicit refusal rule**: a scaffold-aware,
> provenance-carrying workbench in which botanical, chemical, assay, model and pharmacogenomic statements
> cannot be silently merged, and in which the only quantitative prioritisation output is withheld when the
> query leaves the empirically referenced chemical space.

Three mechanisms carry that contribution, each demonstrable in seconds:

1. **No blended score, enforced.** The former equal-weight composite was deleted; `/api/predict` returns
   `candidate_priority_score: null` for an out-of-reference molecule (sucrose, max Tanimoto 0.193 < 0.3236),
   and a regression test asserts the withholding.
2. **Difficulty is reported, not hidden.** Scaffold-group holdout (2,462/702, no shared scaffold), training-only
   CV, an internal document-held-out and a temporal-held-out stress test, and a duplicate-aggregation
   sensitivity analysis that shows ranking metrics are moderately stable (ROC 0.774–0.825) while the
   threshold-0.5 operating point is not (balanced accuracy 0.637–0.729).
3. **Pharmacogenomics that refuses to overreach.** A verified CPIC CYP2C19–clopidogrel demonstration is kept in
   a *disconnected* graph component, with phenotype/ACS-PCI-conditioned wording, and ClinVar's
   "Likely benign; other" germline label explained as a disease-association call rather than a
   metaboliser-function call.

## 4. What is deliberately claimed *not* to be novel

- Integrating plant occurrence, chemistry and ChEMBL bioactivity is **not** new: see the 2026 compound-centric
  framework, NPASS, IMPPAT and LOTUS [@compoundcentric2026; @zhao2023npass; @vivekananth2023imppat2; @rutz2022lotus].
- Scaffold-based splitting, Morgan fingerprints and random forests are standard practice [@wu2018moleculenet].
- Natural-product knowledge graphs exist and are far larger than KAPPA's demonstration graph [@taneja2022npkg].
- KAPPA does **not** claim first-in-field status for any of these.

## 5. Falsifiable success criteria for the next iteration

| Criterion | How it would be tested | Current state |
|---|---|---|
| Transportability | Score a genuinely independent PTGS2 assay dataset with no shared publications or structures | Not done; internal stress tests only (ROC 0.724 / 0.602) |
| Probability usefulness | Calibration fitted in training folds; report Brier/ECE on holdout | Not done; uncalibrated (Brier 0.128, ECE 0.120) |
| Aggregation robustness | Paired comparison of the three rules on a common structure subset | Partially done; unpaired comparison only |
| Evidence-contract usefulness | Time-to-answer a defined researcher question versus manual database work | Not measured; would need a small user study |
| Ethnobotanical scope | More than one attributed record from more than one source | One record only |

## 6. One-sentence version

*KAPPA turns a familiar "plant → compound → target" story into an auditable chain in which each link declares
what kind of evidence it is, and the model's number disappears when the chemistry leaves the space it was
measured in.*
