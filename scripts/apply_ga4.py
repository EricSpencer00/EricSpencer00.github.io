#!/usr/bin/env python3
"""Add the production Google tag to every public HTML page.

The page generators rebuild several complete ``<head>`` blocks during each
deployment, so the analytics tag belongs at the end of the build rather than
in individual source pages. The operation is idempotent and skips archives,
tests, editor material, and legacy redirect stubs.

    python3 scripts/apply_ga4.py
    python3 scripts/apply_ga4.py --check
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MEASUREMENT_ID = "G-30FQRTZWJ8"
MARKER = f"googletagmanager.com/gtag/js?id={MEASUREMENT_ID}"
TAG = f'''<script async src="https://www.googletagmanager.com/gtag/js?id={MEASUREMENT_ID}"></script>
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){{dataLayer.push(arguments);}}
gtag('js', new Date());
gtag('config', '{MEASUREMENT_ID}');
</script>
'''
SKIP_DIRS = {".git", "ai4fm", "backup-site", "tests", "editor"}


def pages():
    for path in sorted(ROOT.rglob("*.html")):
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        yield path


def apply(path: Path, check: bool) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    if MARKER in text:
        return "same"
    if "<!-- redirect stub -->" in text:
        return "redirect-skipped"
    if "</head>" not in text:
        return "no-head"
    if check:
        return "would-write"
    path.write_text(text.replace("</head>", TAG + "</head>", 1), encoding="utf-8")
    return "wrote"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    counts: dict[str, int] = {}
    for path in pages():
        result = apply(path, args.check)
        counts[result] = counts.get(result, 0) + 1

    print(", ".join(f"{count} {kind}" for kind, count in sorted(counts.items())))
    return 1 if args.check and counts.get("would-write") else 0


if __name__ == "__main__":
    sys.exit(main())
