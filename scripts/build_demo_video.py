"""Assemble the narrated demo video from captured frames + narration clips.

Inputs (not tracked — they are regenerated):
    results/video_frames/*.png      from scripts/capture_video_frames.py, plus the two title/closing cards
    results/video_audio/s*.mp3      narration, one clip per scene
Output (not tracked):
    results/video/KAPPA_demo.mp4    1920x1080 H.264 + AAC, ~28 MB, ~5.6 min

Requires ffmpeg; this script uses the binary shipped by `imageio-ffmpeg` (pip install imageio-ffmpeg), so no
system-level ffmpeg install is needed.

Each scene is a still frame held for the length of its narration clip, with short fades and a lower-third
label. Nothing is animated or simulated: the frames are screenshots of the running app, and the narration
describes only behaviour that the screenshots show.
"""
from __future__ import annotations

import os
import re
import subprocess
import tempfile
from pathlib import Path

FRAMES = Path("results/video_frames")
AUDIO = Path("results/video_audio")
OUT = Path("results/video/KAPPA_demo.mp4")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# (narration clip, frame, lower-third label)
SCENES = [
    ("s1", "00_title.png", ""),
    ("s2", "01_overview.png", "Overview · what the pilot does and does not claim"),
    ("s3", "03_ethnobotany.png", "Plant & knowledge · occurrence is not traditional use"),
    ("s4", "04_compounds.png", "Compound explorer · measured assays only"),
    ("s5", "05_rank_sucrose.png", "Prioritisation · sucrose is not rankable"),
    ("s6", "06_rank_curcumin.png", "Prioritisation · in-domain, flagged retrospective"),
    ("s7", "07_graph_pilot.png", "Evidence graph · plant & assay pilot"),
    ("s8", "08_graph_pgx.png", "Evidence graph · independent PGx component"),
    ("s9", "12_closing.png", ""),
]


def ffmpeg() -> str:
    import imageio_ffmpeg

    return imageio_ffmpeg.get_ffmpeg_exe()


def duration(path: Path, ff: str) -> float:
    err = subprocess.run([ff, "-i", str(path)], capture_output=True, text=True).stderr
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", err)
    if not m:
        raise RuntimeError(f"cannot read duration of {path}")
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))


def main() -> int:
    ff = ffmpeg()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="kappaseg"))
    parts = []
    for i, (clip, frame, label) in enumerate(SCENES):
        audio = AUDIO / f"{clip}.mp3"
        if not audio.exists() or not (FRAMES / frame).exists():
            print(f"missing input for scene {clip}: {frame} / {audio.name}")
            return 1
        d = duration(audio, ff) + 0.35
        vf = f"scale=1920:1080,format=yuv420p,fade=t=in:st=0:d=0.25,fade=t=out:st={d - 0.28:.2f}:d=0.25"
        if label:
            safe = label.replace(":", r"\:").replace("'", "")
            vf += (
                ",drawbox=x=54:y=988:w=1812:h=58:color=0x071412@0.72:t=fill"
                f",drawtext=fontfile={FONT}:text='{safe}':x=74:y=1004:fontsize=27:fontcolor=0x52D9A4"
            )
        out = tmp / f"seg{i:02d}.mp4"
        subprocess.run(
            [ff, "-y", "-loop", "1", "-framerate", "25", "-i", str(FRAMES / frame), "-i", str(audio),
             "-t", f"{d:.2f}", "-vf", vf, "-map", "0:v", "-map", "1:a",
             "-c:v", "libx264", "-preset", "ultrafast", "-tune", "stillimage", "-crf", "23",
             "-pix_fmt", "yuv420p", "-threads", "2",
             "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-ac", "2", "-shortest", str(out)],
            check=True, capture_output=True,
        )
        parts.append(out)
        print(f"scene {clip}: {d:.1f}s")

    listing = tmp / "concat.txt"
    listing.write_text("".join(f"file '{p}'\n" for p in parts))
    subprocess.run([ff, "-y", "-f", "concat", "-safe", "0", "-i", str(listing),
                    "-c", "copy", "-movflags", "+faststart", str(OUT)], check=True, capture_output=True)
    print(f"wrote {OUT} ({os.path.getsize(OUT) / 1048576:.1f} MB, {duration(OUT, ff) / 60:.2f} min)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
