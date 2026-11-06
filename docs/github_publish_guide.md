# Publishing KAPPA to a new public GitHub repository

Status: **not executed.** No git remote, no credential and no GitHub integration exist in this environment
(`git remote -v` is empty; the GitHub connector reports `unsupported`). Nothing has been pushed, force-pushed,
or rewritten. This document is the exact, ordered procedure for the repo owner to run, plus what to verify
afterwards.

## 0. What is being published

- Branch `master`, linear history, newest commit `88f6791`.
- 130 tracked files, ~16 MB working tree plus a 16 MB model artefact; largest file 16 MB
  (`models/ptgs2_rf.joblib`), well under GitHub's 100 MB per-file limit.
- A full-history copy is exported next to this repository as `kappa_history.bundle`
  (`git bundle create ../kappa_history.bundle --all`) — clone it, or push from the live working copy.

## 1. Create the repository

Recommended name and metadata (any of these can be changed):

- name: `kappa-ethnohack2026`
- description: `Evidence-separated natural-product research workbench: curated ChEMBL PTGS2 data, scaffold-held-out ML, provenance-enforced ethnobotany, and a disconnected CPIC pharmacogenomics demo`
- topics: `natural-products`, `chembl`, `rdkit`, `pharmacogenomics`, `reproducibility`, `scikit-learn`, `fastapi`
- visibility: public (required by the rules), **no** README/gitignore/licence template — the repo already has all
  three and a template would create a conflicting initial commit.

Either through the web UI (New repository → the fields above → Create) or:

```bash
gh repo create kappa-ethnohack2026 --public \
  --description "Evidence-separated natural-product research workbench" \
  --source . --remote origin
```

## 2. Push the existing history (no rewrite)

From the repository root, with an account that owns the new repo:

```bash
git remote add origin git@github.com:<owner>/kappa-ethnohack2026.git   # or the HTTPS URL
git remote -v                       # confirm the target before pushing
git push -u origin master           # fast-forward only; never add --force
```

If the organisation's default branch must be `main`, rename before the first push (`git branch -m master main`)
and push `main`; do not delete or overwrite `master` afterwards.

## 3. Licence obligation that must be settled first

`data/raw/` contains ChEMBL records under **CC BY-SA 3.0**. Two defensible options:

1. **Reproducibility repo (recommended for judging):** publish the caches, keep `data/raw/LICENSE-NOTICE.md` in
   place, and make the README's attribution section visible. Accept that the ChEMBL extract keeps CC BY-SA 3.0.
2. **Code-only repo:** `git rm -r --cached data/raw models` before the first push (keep them locally), add a
   `data/README.md` telling users to run `python -m src.run_pipeline` once with internet access. Smaller and
   legally simpler, but a judge must spend ~15 minutes to reproduce numbers.

Do not describe KAPPA's MIT licence as covering the data. It does not.

## 4. Verify the push against the remote

```bash
git ls-remote origin                       # commit SHAs must match local `git rev-parse HEAD`
git log --oneline -3 origin/master         # newest commit present on the remote
```

Then clone into a clean directory and re-run the release checks there:

```bash
git clone git@github.com:<owner>/kappa-ethnohack2026.git /tmp/kappa_verify
cd /tmp/kappa_verify && pytest -q          # expect 22 passed
python -m src.run_pipeline                 # expect 7,482 raw → 3,164 curated; metrics match results/reports/
```

Record the published URL and the commit SHA in `docs/release_checklist.md`, `submission/devpost_description.md`
and the Devpost form.

## 5. Security and identity checklist (already satisfied locally, 2026-11-05/06)

| Check | Command | Result |
|---|---|---|
| Secrets | `git grep -nIiE "api[_-]?key\|secret\|password\|access[_-]?token\|bearer \|BEGIN (RSA\|OPENSSH\|PRIVATE)\|ghp_\|sk-[A-Za-z0-9]{10}"` | only false positives (UniProt `secreted`/`secretory` text; audit sentences describing the scan) |
| Local paths | `git grep -n "/home/user\|/Users/\|C:\\\\Users"` | one hit, inside the checklist's own instruction line |
| Personal data | e-mail regex over tracked files | zero hits; `submission/team_contributions.md` is an empty template |
| Runtime network calls | code review + `grep` for `requests.` in `backend/` | none; the API serves cached files only |
| Tracked artefacts | `git ls-files -z \| xargs -0 du -h \| sort -rh \| head` | 16 MB model, 3.9 MB ChEMBL cache, rest < 1 MB |
| Bundle zip tracked? | `git status --short` / `.gitignore` | no — `submission/*.zip` is ignored and rebuilt on demand |

Never paste a token into a file inside the repository, into a commit message, or into chat. If credentials are
needed for an automated step, use an existing credential helper or a short-lived deploy key that is revoked
afterwards.

## 6. Optional post-publish polish

- Tag `v0.1.0-ethnohack` and attach `presentation/rendered/KAPPA_pitch_deck.pdf` as a release asset.
- GitHub Pages cannot serve the API (it is a Python service); a static demo is not equivalent, so do not imply
  a hosted app.
- Keep the release bundle as a release asset rather than a committed file.
