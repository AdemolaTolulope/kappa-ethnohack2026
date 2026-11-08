# Demo video — what was produced, and what is still needed

## The file

`results/video/KAPPA_demo.mp4` — **1920×1080, H.264 + AAC, 27.9 MB, 5:35** (well under the 10-minute cap).
Silent-screen fixtures are not used: every frame is a screenshot of the running app captured by
`scripts/capture_video_frames.py`, and each scene is held for the length of its narration clip by
`scripts/build_demo_video.py`.

| Time | Scene |
|---|---|
| 0:00 | Title — evidence-separated phyto-pharmacogenomics |
| 0:14 | Overview: what the pilot does and does not claim (7,482 → 3,164; 0.782/0.940 at 82.6% prevalence) |
| 1:00 | Plant & knowledge: Wikidata occurrence vs a 2012 secondary report; fail-closed record validation |
| 1:48 | Compound explorer: measured assays only, pre-declared filters, grey band omitted |
| 2:23 | **Prioritisation: sucrose → "Not rankable · probability withheld"** (0.193 < 0.3236) |
| 3:12 | Prioritisation: curcumin → 0.150, in-domain, flagged as exact training match (retrospective) |
| 3:49 | Evidence graph: plant & assay pilot, typed edges with provenance |
| 4:19 | Evidence graph: disconnected CPIC CYP2C19–clopidogrel component, no patient genotype |
| 4:55 | Methods, provenance, the withdrawn 0.832 metrics, 22 tests, closing card |

Narration text: `submission/video_narration.md` (the recorded script is the same content, spoken in nine
segments). Claims in the audio match `results/reports/model_metrics.json`; no clinical, efficacy or external-
validation claim is made anywhere in it.

## Integrity checks performed

- Full decode with ffmpeg: no errors (`-v error -i … -f null -`).
- Audio present and not silent: mean −22.8 dB, peak −4.5 dB.
- Frames visually inspected at 0:06, 0:55, 1:40, 2:40, 3:35, 5:00, 5:30.
- Container duration 5:35 < 10:00 limit.

## Hosting status (read this before pasting a link)

- Uploaded as a **GitHub release asset**:
  `https://github.com/AdemolaTolulope/kappa-ethnohack2026/releases/download/v0.1.0-ethnohack/KAPPA_demo.mp4`
  The API reports the asset as `state: uploaded` (27.9 MB). **Caveat:** fetching that URL from this sandbox
  returned HTTP 504 twice, so playback is **unverified from here** — the same sandbox also 504s on ordinary
  GitHub blob pages while `raw.githubusercontent.com` works, which points at egress, not at the asset. Click it
  in your own browser before submitting; if it does not download, use YouTube below.
- **Recommended for the Devpost field:** upload the mp4 to **YouTube as Unlisted** (or Loom/Vimeo) — Devpost
  embeds only those providers, so a GitHub link will not show a player on the project page.
- No account was created on your behalf and no third-party upload service was used (0x0.st has disabled
  anonymous uploads; catbox/litterbox rejected the uploads from this environment).
