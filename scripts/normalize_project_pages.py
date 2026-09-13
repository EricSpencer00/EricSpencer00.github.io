#!/usr/bin/env python3
"""Keep canonical project articles semantic and search-ready.

Project pages predate the current static build and were hand-authored with a
title-shaped H2. This normalizer upgrades that first heading to the page H1,
keeps the article title visible, and makes the full fraud notebook distinct
from the shorter fraud-predictor page.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = sorted(path for path in (ROOT / "projects").glob("*.html") if path.name != "index.html")
CSS = """h1.article-title{font-family:\"IBM Plex Mono\",monospace;font-size:clamp(23px,3vw,32px);font-weight:700;letter-spacing:-.04em;line-height:1.2;color:var(--ink);margin:24px 0 8px}\n"""
FIRST_HEADING = re.compile(r"(<p class=\"back\">.*?</p>\s*)<h2(?:\s[^>]*)?>(.*?)</h2>", re.S)


def replace_full_fraud_title(text: str) -> str:
    old = "Machine Learning Fraud Identifier"
    new = "Credit-Card Fraud Analysis: Full Notebook"
    text = text.replace(old, new)
    return text.replace(
        "Analyze different Machine Learning algorithms to identify fraud within a classified dataset",
        "Full credit-card fraud analysis notebook comparing machine-learning approaches on a classified dataset.",
    )


def normalize(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    # Repair the escaped attribute emitted by the initial normalizer release;
    # browsers treated it as a literal attribute name, not a CSS class.
    text = text.replace('class=\\"article-title\\"', 'class="article-title"')
    if path.name == "fraud-predictor-full.html":
        text = replace_full_fraud_title(text)
    if 'class="article-title"' not in text:
        text, count = FIRST_HEADING.subn(r'\1<h1 class="article-title">\2</h1>', text, count=1)
        if count != 1:
            raise ValueError(f"could not find article heading in {path.relative_to(ROOT)}")
    if CSS not in text:
        text = text.replace("</style>", CSS + "</style>", 1)
    return text


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    stale = []
    changed = 0
    for path in PAGES:
        text = path.read_text(encoding="utf-8")
        expected = normalize(path)
        if text != expected:
            stale.append(path.relative_to(ROOT))
            if not args.check:
                path.write_text(expected, encoding="utf-8")
                changed += 1
    if args.check and stale:
        print("project pages need normalization:\n" + "\n".join(map(str, stale)), file=sys.stderr)
        return 1
    print(f"normalized {changed} project pages" if not args.check else "project headings are current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
