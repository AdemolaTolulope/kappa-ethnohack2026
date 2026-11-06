# Public repository (GitHub) release preparation checklist

**Executed 2026-11-06:** the repository was created empty by its owner and the local history was pushed to
[https://github.com/AdemolaTolulope/kappa-ethnohack2026](https://github.com/AdemolaTolulope/kappa-ethnohack2026) (default branch `main`, fast-forward only), then verified by an anonymous clone that passed the
tests and reproduced the metrics. The notes below are kept as the record of what was checked beforehand.
Before publishing, the workspace was a local git repository on branch `master`
with a linear history and **no remote, no credentials, and no push has occurred** (checked 2026-11-05:
`git remote -v` empty, no `gh` binary, no GitHub connector available in this environment). Publishing requires
your approval, the correct repository identity, and an authorised access route. This checklist is the sequence
to follow once you authorise it.

## 0. Pre-flight (already true in this workspace)

- [x] Local git history exists with meaningful commit messages (`git log --oneline`).
- [x] `.gitignore` excludes `__pycache__/`, `*.py[cod]`, `.venv/`, `.env`, `.DS_Store`.
- [x] `LICENSE` (MIT) present for the *code only*.
- [x] `CITATION.cff` present.
- [x] `requirements.txt` present.
- [x] No credentials or personal data: `grep -ri "api_key\|secret\|password\|token"` returns nothing; `.env.example` holds only `KAPPA_DATA_DIR=data`.
- [x] Third-party licences documented (`docs/provenance_register.md`, `submission/third_party_disclosures.md`).
- [x] AI-assisted development disclosed (`submission/third_party_disclosures.md`).
- [x] 22 tests pass; the pipeline reproduces the stored primary metrics.
- [x] Release bundle zip is **not tracked** (`submission/*.zip` in `.gitignore`), so the repository stays lean and
      the bundle is rebuilt from source instead of drifting out of date.

## 1. Decide what the public repo is for

Two defensible options — pick one before creating the remote:

1. **Full reproducibility repo** (recommended for judging): include `data/raw/*` caches, `models/*.joblib`,
   figures, rendered deck and screenshots (~13–30 MB). Maximum credibility, but you are redistributing ChEMBL
   records, which carry **CC BY-SA 3.0** obligations.
2. **Code-only repo**: exclude `data/raw/`, `models/` and keep a `data/README.md` describing how to re-fetch.
   Smaller and simpler legally, but a judge cannot verify numbers without network access and ~15 minutes.

If you choose option 1, add a `data/raw/LICENSE-NOTICE.md` stating that the ChEMBL extract is redistributed
under CC BY-SA 3.0 with attribution, and that KAPPA's MIT licence does not relicense it.

## 2. Repository hygiene before the first push

- [x] **Security scan executed 2026-11-05** over tracked files (`git grep`):
      - credentials: `git grep -nIiE "api[_-]?key|secret|password|access[_-]?token|bearer |BEGIN (RSA|OPENSSH|PRIVATE)|ghp_|sk-[A-Za-z0-9]{10}"`
        → only false positives (UniProt `secreted`/`secretory` biology text, and the audit sentences that describe
        this very scan). **No secrets.**
      - absolute paths: `git grep -n "/home/user\|/Users/\|C:\\Users"` → single hit, inside this checklist's
        own instruction line. **No machine-specific paths in code, data or notebooks.**
      - personal data: e-mail regex over tracked files → **zero hits**. `submission/team_contributions.md` is an
        empty template; no names, affiliations or affiliations-by-implication anywhere.
      - tracked artefacts: `models/ptgs2_rf.joblib` (16 MB) and `data/raw/chembl_ptgs2_ic50.jsonl` (3.9 MB) are
        the two largest; both are below GitHub's 100 MB per-file limit. 121 tracked files.
- [ ] Confirm the commit author identity you want in public history (`git config user.name/user.email`).
- [ ] Decide whether the rendered `presentation/rendered/*.png` (≈1 MB) belong in the repo or a release asset.
- [ ] Add a short `CONTRIBUTING.md` only if others will actually contribute; otherwise skip it rather than
      publishing an empty process document.
- [ ] Re-read `README.md` top to bottom: every claim must still match `results/reports/`.
- [ ] Verify no absolute local paths leaked into notebooks or docs (`grep -r "/home/user"`).

## 3. Actions that require your approval

- [ ] Create the remote repository (public), e.g. `kappa-ethnohack-2026`.
- [x] `git remote add origin <url>`; local `master` was renamed to `main` and pushed (`git push -u origin main`).
- [ ] Add repository description, topics (`natural-products`, `chembl`, `rdkit`, `pharmacogenomics`, `reproducibility`) and a social preview image if desired.
- [ ] Create a tag/release, e.g. `v0.1.0-ethnohack`, with the deck PDF and bundle zip attached as release assets.
- [ ] Double-check the public rendering of `README.md` (relative links must resolve on GitHub).
- [ ] After publishing, add the URL to `submission/devpost_description.md` and re-check the submission form.

## 4. Things that must NOT be published without a decision

- `models/ptgs2_rf.joblib` (16 MB) if you want a lean repo — it is reproducible from the pipeline.
- Any future `.env` with a deployment secret.
- Contributor names or affiliations that the individuals have not confirmed in writing.
- Claims of external validation, clinical utility or completed submission.

## 5. Post-publish verification

- [ ] Open the repo in a private/incognito window: does the README render, do images load, do links resolve?
- [ ] Clone into a clean directory and run `pytest -q` (expect 22 passed) and `python -m src.run_pipeline`.
- [ ] Check the licence badge wording does not imply the data are MIT-licensed.
- [ ] Record the commit SHA in the Devpost draft and in `docs/release_checklist.md`.
