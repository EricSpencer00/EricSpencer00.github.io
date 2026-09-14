#!/usr/bin/env python3
"""Keep canonical project articles semantic and search-ready.

Project pages predate the current static build and were hand-authored with a
title-shaped H2. This normalizer upgrades that first heading to the page H1,
keeps the article title visible, and makes the full fraud notebook distinct
from the shorter fraud-predictor page. It also repairs the few legacy pages
whose interactive markup was wrapped in paragraphs or contained unescaped
HTML-looking text.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = sorted(
    path for path in (ROOT / "projects").glob("*/index.html")
    if path.parent.name != "2026"
)
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


def repair_legacy_markup(path: Path, text: str) -> str:
    # Archived ChatGPT transcripts sometimes wrapped a block-level div in a
    # paragraph. HTML parsers repair that differently, so keep the transcript
    # text but make the structure valid for every project page.
    text = re.sub(r"<p>\s*(<div\b[^>]*>)", r"\1", text)
    text = re.sub(r"(</div>)\s*</p>", r"\1", text)
    if path.name == "one-rep-max.html":
        text = text.replace(
            '<p><div style="margin: 1em 0;">',
            '<div class="one-rep-max-controls" style="margin: 1em 0;"><p>',
        )
        controls = '<div class="one-rep-max-controls" style="margin: 1em 0;">'
        if controls + '<p>' not in text:
            text = text.replace(controls, controls + '<p>', 1)
        text = text.replace('</button> </div></p>', '</button></p></div>')
        text = text.replace('</button> </div>', '</button></p></div>')
        text = text.replace('<p><div id="result"', '<div id="result"')
        text = text.replace('style="margin-top: 1em; font-weight: bold;"></div></p>',
                            'style="margin-top: 1em; font-weight: bold;"></div>')
        text = text.replace('</script></p>', '</script>')
    elif path.name == "skeuomorphism.html":
        text = text.replace('<p><div class="skeuomorphic-wrapper">',
                            '<div class="skeuomorphic-wrapper">')
        text = text.replace('</div> </div></p>', '</div> </div>')
        text = re.sub(
            r'(<svg\b.*?title="Sign Language Interpreter".*?</a>)</p>',
            r'\1',
            text,
            count=1,
            flags=re.S,
        )
        text = text.replace('<span> <rect x="135" y="485" width="130" height="70" class="clickable-area" /> </span>',
                            '<g> <rect x="135" y="485" width="130" height="70" class="clickable-area" /> </g>')
        text = re.sub(r'<p><!-- (?:Networking|Health|Games|Web|Personal).*?</p>',
                      lambda match: match.group(0)[3:-4] + '\n', text, flags=re.S)
        text = text.replace('<p><style>', '<style>').replace('</style></p>', '</style>')
        text = text.replace('<p><script>', '<script>').replace('</script></p>', '</script>')
    elif path.name == "llmjammer.html":
        text = re.sub(
            r'<p>A future version could strip the code of spacing and tabbing,.*?</p>\n',
            '<p>A future version could minify the obfuscated code, but that experiment is not part of the package.</p>\n',
            text,
            count=1,
            flags=re.S,
        )
        text = re.sub(r'<p>!function\(n\)\{.*?</p>\n', '', text, count=1, flags=re.S)
    return text


def normalize(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    text = repair_legacy_markup(path, text)
    # Repair the escaped attribute emitted by the initial normalizer release;
    # browsers treated it as a literal attribute name, not a CSS class.
    text = text.replace('class=\\"article-title\\"', 'class="article-title"')
    if path.name == "fraud-predictor-full.html":
        text = replace_full_fraud_title(text)
    if 'class="article-title"' not in text and not re.search(r"<h1\b", text, re.I):
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
