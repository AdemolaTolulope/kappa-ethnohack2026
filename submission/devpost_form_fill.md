# Devpost form — copy-paste pack (EthnoHack 2026, submission 1283318)

Everything below is ready to paste into the fields you have open. Character limits are checked against the real
limits, and every link is an **absolute public URL** (Devpost does not resolve relative paths).

**Deadline: Sunday 8 November 2026, 10:00 Athens time (EET, UTC+2) = 09:00 Lagos (WAT, UTC+1) = 08:00 UTC.**

---

## Step 1 — Project overview

**Project name** (54 / 60 characters):

```
KAPPA — Knowledge-guided AI for Phyto-Pharmacogenomics
```

**Elevator pitch** (189 / 200 characters):

```
A research workbench that keeps plant occurrence, ethnobotany, measured PTGS2 assays, model estimates and PGx evidence separate — and refuses to rank molecules outside its empirical domain.
```

**Thumbnail:** upload `submission/thumbnail.png` (1800×1200, exactly 3:2, 119 KB).

---

## Step 2 — Project details

### Project story (paste as Markdown)

Devpost now uses its standard template. Paste **the entire contents of `submission/devpost_story.md`** — it is
written to those exact headings: *Inspiration · What it does · How we built it · Challenges we ran into ·
Accomplishments that we're proud of · What we learned · What's next for KAPPA*, with data attribution and an
explicit limitations subsection folded in so nothing on the checklist is missing. Every link in it is absolute and
was curl-checked to return 200.

### Built with (paste as tags)

```
python, rdkit, scikit-learn, pandas, numpy, fastapi, networkx, matplotlib, javascript, html5, css3, pytest, chembl, rdkit-morgan-fingerprints, bemis-murcko-scaffolds, cpic, clinvar, uniprot, wikidata, joblib, uvicorn, git, github
```

### "Try it out" links

| Label | URL |
|---|---|
| Source code (public) | `https://github.com/AdemolaTolulope/kappa-ethnohack2026` |
| Slide deck — 10 slides, PDF | `https://github.com/AdemolaTolulope/kappa-ethnohack2026/blob/main/presentation/rendered/KAPPA_pitch_deck.pdf` |
| Scientific integrity audit | `https://github.com/AdemolaTolulope/kappa-ethnohack2026/blob/main/docs/scientific_integrity_audit.md` |
| Validation report | `https://github.com/AdemolaTolulope/kappa-ethnohack2026/blob/main/docs/validation_report.md` |

> The 16 MB reproducibility zip is intentionally **not** committed (it is `.gitignore`d and rebuilt from source),
> so it is uploaded in **Additional info** below rather than linked. Do not add a URL that 404s. If you want a
> hosted download, attach the zip as a GitHub **release asset** and use that URL.

### Image gallery — six 3:2 files are ready

All six are **1800×1200 (exactly 3:2), PNG, 145 KB – 890 KB** (limit 5 MB), captioned in-frame. Local copies are in
`results/gallery/`; the same files are in your Google Drive as `KAPPA_gallery_1…6_*.png`.

| Upload order | File | Caption for the Devpost field |
|---|---|---|
| 1 | `results/gallery/g1_model_comparison.png` | Scaffold-held-out benchmark: Random Forest ROC-AUC 0.782 vs logistic 0.703 at 82.6% test prevalence |
| 2 | `results/gallery/g2_refusal.png` | The refusal rule in code: sucrose similarity 0.193 < 0.3236 → "Not rankable · probability withheld" |
| 3 | `results/gallery/g3_in_domain.png` | In-domain: curcumin 15.0% uncalibrated, flagged as an exact training match (retrospective) |
| 4 | `results/gallery/g4_duplicates.png` | Duplicate-structure sensitivity: coverage stable, threshold-0.5 operating point not |
| 5 | `results/gallery/g5_pgx.png` | Disconnected PGx component: verified CPIC CYP2C19–clopidogrel guideline, no patient genotype |
| 6 | `results/gallery/g6_ethnobotany.png` | Provenance-labelled ethnobotany: one attributed 2012 report with limitations and coverage statement |

### Video demo link

A narrated 5:35 demo has been produced: `results/video/KAPPA_demo.mp4` (1920×1080, 27.9 MB). Chapters, the
production method and the integrity checks are in [`video_notes.md`](video_notes.md).

- Repo-hosted copy (release asset): `https://github.com/AdemolaTolulope/kappa-ethnohack2026/releases/download/v0.1.0-ethnohack/KAPPA_demo.mp4`
- Release page: `https://github.com/AdemolaTolulope/kappa-ethnohack2026/releases/tag/v0.1.0-ethnohack`

**For the Devpost field, use YouTube Unlisted** (or Loom/Vimeo) so it embeds with a player:
1. youtube.com → Create → Upload video → select `results/video/KAPPA_demo.mp4`
2. Title: `KAPPA — evidence-separated phyto-pharmacogenomics (EthnoHack 2026 demo)`; Visibility: **Unlisted**
3. Paste the `https://youtu.be/…` link into the Devpost video field and open it in an incognito window to confirm
   it plays without signing in.

## Step 3 — Additional info (judges only)

**Upload this file:** `submission/KAPPA_ethnohack2026_bundle.zip` — 138 files, 15.7 MB (limit 35 MB).
It is also in your Google Drive as `KAPPA_ethnohack2026_bundle.zip` if you are uploading from another device,
and attached to the GitHub release. It contains
the cached source data, the trained model, the pipeline, tests, figures, the rendered deck and the run instructions.

Judge-facing note to paste into the "additional info" text field, if the form offers one:

```
Everything is reproducible offline from the uploaded bundle:
  pip install -r requirements.txt
  python -m src.run_pipeline      # ~40 s, regenerates data, model, metrics, figures, graph
  pytest -q                       # 22 passed
  uvicorn backend.main:app --port 8000
The same two commands pass in a fresh clone of the public repository (verified 2026-11-06: 22 passed, metrics
reproduced to 1.1e-16). Primary result: Random Forest scaffold holdout ROC-AUC 0.781897, PR-AUC 0.939647,
balanced accuracy 0.637210 at 82.62% test prevalence. Out-of-domain molecules deliberately return
candidate_priority_score = null. No external validation, no calibration, no clinical claims.
```

---

## Step 4 — Before you press Submit

- [ ] **Challenge track** selected — "Natural Products for Drug Discovery".
- [ ] **Team:** you (`@ademmanlincoln07`) + `@temiladedeborah35` are added; **two e-mail invites are still
      "Invite sent, unconfirmed"** (`surprisefaith480@gmail.com`, `olorundunsinpeter@gmail.com`). They must accept and
      confirm their own accounts, and the final roster must be **2–5 members**. Do not list anyone who has not
      accepted, and do not invent contribution statements — fill `submission/team_contributions.md` only with what
      each person actually confirms.
- [ ] **Eligibility/registration:** the public event page listed registration as closed (2026-10-31) and its
      eligibility wording differs from the rules page. Keep the organizers' written confirmation; the Devpost form
      accepting your draft does not settle eligibility.
- [ ] **Video URL** present and public, ≤ 10 minutes, and the link plays in an incognito window.
- [ ] **GitHub link** opens in incognito: https://github.com/AdemolaTolulope/kappa-ethnohack2026
- [ ] Deck link opens: 10 slides, PDF.
- [ ] Story contains: problem, solution, technologies, data + attribution, results, limitations, future work.
- [ ] No sentence presents computational output as established medical evidence.
- [ ] Screenshot everything after submitting (confirmation page + timestamp).

## Clock

| Zone | Deadline |
|---|---|
| Athens (EET, UTC+2) | Sun 8 Nov 2026, **10:00** |
| Lagos (WAT, UTC+1) | Sun 8 Nov 2026, **09:00** |
| UTC | Sun 8 Nov 2026, **08:00** |
