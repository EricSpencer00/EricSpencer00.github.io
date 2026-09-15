#!/usr/bin/env python3
"""Refresh committed news previews from their original PDFs.

Requires Poppler (pdftoppm) and Pillow. Run locally, not during site deployment.
"""
import json
from pathlib import Path
import subprocess
import tempfile
from urllib.request import urlopen

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent


def main():
    history = json.loads((ROOT / "content/news-history.json").read_text())
    records = history["entries"] + list(history["updates"].values())
    with tempfile.TemporaryDirectory(prefix="news-previews-") as scratch:
        for record in records:
            attachment = record.get("attachment")
            if not attachment:
                continue
            stem = Path(attachment["image"]).stem
            pdf = Path(scratch) / f"{stem}.pdf"
            with urlopen(attachment["url"], timeout=60) as response:
                pdf.write_bytes(response.read())
            prefix = Path(scratch) / stem
            subprocess.run([
                "pdftoppm", "-f", "1", "-singlefile", "-scale-to", "1200",
                "-png", str(pdf), str(prefix),
            ], check=True)
            with Image.open(prefix.with_suffix(".png")) as image:
                if image.size != (attachment["width"], attachment["height"]):
                    raise ValueError(f"Update preview dimensions in news-history.json for {stem}")
                target = ROOT / attachment["image"].lstrip("/")
                target.parent.mkdir(parents=True, exist_ok=True)
                image.convert("RGB").save(target, quality=85)
                print(target.relative_to(ROOT))


if __name__ == "__main__":
    main()
