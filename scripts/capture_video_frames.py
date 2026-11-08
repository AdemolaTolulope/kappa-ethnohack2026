"""Capture the demo-video frames from the running app (1920x1080 PNGs).

Usage:
    uvicorn backend.main:app --host 0.0.0.0 --port 8000     # in another shell
    python scripts/capture_video_frames.py

Writes results/video_frames/*.png, which scripts/build_demo_video.py turns into the narrated mp4.
Every frame is a real screenshot of the running application — nothing is mocked or composited.
"""
from __future__ import annotations

import sys
from pathlib import Path

BASE = "http://127.0.0.1:8000"
OUT = Path("results/video_frames")
SUCROSE = "OC[C@H]1O[C@@](CO)(O[C@H]2O[C@H](CO)[C@@H](O)[C@H](O)[C@H]2O)[C@@H](O)[C@@H]1O"


def main() -> int:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("playwright is not installed: pip install playwright && playwright install chromium", file=sys.stderr)
        return 1
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
        page.goto(BASE, wait_until="networkidle", timeout=60_000)
        page.wait_for_timeout(1500)
        page.screenshot(path=str(OUT / "01_overview.png"))

        page.click('.nav[data-page="ethnobotany"]')
        page.wait_for_timeout(2500)
        page.screenshot(path=str(OUT / "03_ethnobotany.png"))

        page.click('.nav[data-page="compounds"]')
        page.wait_for_timeout(2500)
        page.screenshot(path=str(OUT / "04_compounds.png"))

        page.click('.nav[data-page="rank"]')
        page.wait_for_selector("#rankSmiles", timeout=20_000)
        page.fill("#rankSmiles", SUCROSE)
        page.click('button:has-text("Assess candidate")')
        page.wait_for_selector(".blocked", timeout=30_000)   # the refusal panel must actually render
        page.wait_for_timeout(1200)
        page.screenshot(path=str(OUT / "05_rank_sucrose.png"))

        page.click('button:has-text("Use curcumin-like input")')
        page.click('button:has-text("Assess candidate")')
        page.wait_for_timeout(2500)
        page.screenshot(path=str(OUT / "06_rank_curcumin.png"))

        page.click('.nav[data-page="graph"]')
        page.wait_for_timeout(3000)
        page.screenshot(path=str(OUT / "07_graph_pilot.png"))
        page.select_option("#graphScope", "pharmacogenomics")
        page.wait_for_timeout(3000)
        page.screenshot(path=str(OUT / "08_graph_pgx.png"))

        page.click('.nav[data-page="genomics"]')
        page.wait_for_timeout(3000)
        page.screenshot(path=str(OUT / "09_genomics.png"))
        page.click('.nav[data-page="ml"]')
        page.wait_for_timeout(3000)
        page.screenshot(path=str(OUT / "10_ml.png"))
        page.click('.nav[data-page="methods"]')
        page.wait_for_timeout(2500)
        page.screenshot(path=str(OUT / "11_methods.png"))
        browser.close()
    print(f"frames written to {OUT}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
