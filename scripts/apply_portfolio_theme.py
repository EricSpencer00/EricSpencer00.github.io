#!/usr/bin/env python3
"""Attach the shared landing-page shell to public editorial pages.

The project writeups and several landing pages are hand-authored or generated
by separate scripts. This idempotent post-build pass gives them one stylesheet
and a body class without touching app UIs, redirect mirrors, or the archive.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEGACY_STYLESHEET = '<link rel="stylesheet" href="/assets/css/portfolio.css">'
STYLESHEET = '<link rel="stylesheet" href="/assets/css/portfolio.css?v=20260916">'
FONT_STYLESHEET = '<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap">'
SKIP = {".git", ".claude", "backup-site", "editor", "tests", "assets"}


def targets() -> list[Path]:
    paths = [
        ROOT / "404.html",
        ROOT / "projects" / "index.html",
        ROOT / "research" / "index.html",
        ROOT / "cv" / "index.html",
        ROOT / "blog" / "index.html",
        ROOT / "news" / "index.html",
    ]
    paths.extend(
        path
        for path in sorted((ROOT / "projects").glob("*/index.html"))
        if path.parent.name != "2026" and path.parent.name != "index"
    )
    return [path for path in paths if path.is_file()]


def is_redirect(text: str) -> bool:
    return "<!-- redirect stub -->" in text or "location.replace" in text


def add_body_class(text: str, body_class: str) -> str:
    pattern = re.compile(r"<body(?P<attrs>[^>]*)>", re.I)
    match = pattern.search(text)
    if not match:
        return text
    attrs = match.group("attrs")
    if re.search(r"\bclass\s*=", attrs, re.I):
        attrs = re.sub(
            r'\bclass\s*=\s*(["\'])(.*?)\1',
            lambda m: f'class={m.group(1)}{m.group(2)} {body_class}{m.group(1)}'
            if body_class not in m.group(2).split()
            else m.group(0),
            attrs,
            count=1,
        )
    else:
        attrs += f' class="{body_class}"'
    return text[: match.start()] + f"<body{attrs}>" + text[match.end() :]


def add_article_header(text: str) -> str:
    """Give every project writeup the same quiet masthead as the landing page."""
    if 'class="name"' in text or 'class="name-hero"' in text:
        return text
    marker = '<div class="wrap">'
    if marker not in text:
        return text
    header = '<p class="name">Eric Spencer</p>\n<p class="sub">projects</p>\n'
    return text.replace(marker, f"{marker}\n{header}", 1)


def add_page_header(text: str, label: str) -> str:
    """Give a standalone page the same masthead when its source lacks one."""
    if 'class="name"' in text or 'class="name-hero"' in text:
        return text
    marker = '<div class="wrap">'
    if marker not in text:
        return text
    header = '<p class="name">Eric Spencer</p>\n'
    if label:
        header += f'<p class="sub">{label}</p>\n'
    return text.replace(marker, f"{marker}\n{header}", 1)


def apply(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    if is_redirect(text):
        return "skipped-redirect"
    original = text
    body_class = "news-surface" if path == ROOT / "news" / "index.html" else (
        "portfolio-article"
        if path.parent.parent == ROOT / "projects" and path.parent.name != "2026"
        else "portfolio-page"
    )
    text = add_body_class(text, body_class)
    if body_class == "portfolio-article":
        text = add_article_header(text)
    elif path == ROOT / "cv" / "index.html":
        text = add_page_header(text, "")
        text = re.sub(r'<p class="sub">cv</p>\s*', '', text, count=1)
    stylesheet_pattern = re.compile(
        r'<link rel="stylesheet" href="/assets/css/portfolio\.css(?:\?v=[^"]+)?"\s*/?>'
    )
    stylesheet_seen = False

    def normalize_stylesheet(_match: re.Match[str]) -> str:
        nonlocal stylesheet_seen
        if stylesheet_seen:
            return ""
        stylesheet_seen = True
        return STYLESHEET

    text = stylesheet_pattern.sub(normalize_stylesheet, text)
    if not stylesheet_seen and "</head>" in text:
        text = text.replace("</head>", f"{STYLESHEET}\n</head>", 1)
    if "fonts.googleapis.com/css2?family=IBM+Plex+Mono" not in text and "</head>" in text:
        text = text.replace("</head>", f"{FONT_STYLESHEET}\n</head>", 1)
    if text == original:
        return "same"
    path.write_text(text, encoding="utf-8")
    return "wrote"


def main() -> int:
    counts: dict[str, int] = {}
    for path in targets():
        result = apply(path)
        counts[result] = counts.get(result, 0) + 1
    print(", ".join(f"{count} {result}" for result, count in sorted(counts.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
