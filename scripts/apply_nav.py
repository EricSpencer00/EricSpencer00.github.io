#!/usr/bin/env python3
"""
apply_nav.py — rewrite the <nav class="top"> block on every page from one
definition here.

The nav used to be hand-copied into each page, so it drifted: `cv` reached only
the homepage, and every page advertised a `blog` that had nothing published in
it. Runs after the generators (they rewrite whole pages), before the sitemap.
"""

from pathlib import Path
import re
import sys

from build_blog import load_posts

ROOT = Path(__file__).resolve().parent.parent

# Directories that are in git for reference but never published, plus the blog
# post template, which is a scaffold rather than a page.
SKIP_DIRS = {".git", ".claude", "backup-site", "node_modules", "assets", "tests"}
SKIP_FILES = {ROOT / "blog" / "_template.html"}

NAV_RE = re.compile(r'<nav class="top">.*?</nav>', re.DOTALL)

# A page whose whole body is a redirect stub has no header to hang a nav on.
REDIRECT_RE = re.compile(r'location\.replace|This page has moved|This page lives at')

# Search-console verification files are a single line of text served as .html.
VERIFICATION_RE = re.compile(r"google-site-verification", re.IGNORECASE)

# key, label, href, and the path prefix that makes this item the active one.
ITEMS = [
    ("index",    "index",    "/",               ()),
    ("research", "research", "/research.html",  ("research.html",)),
    ("projects", "projects", "/projects.html",  ("projects.html", "projects/")),
    ("blog",     "blog",     "/blog/",          ("blog/",)),
    ("cv",       "cv",       "/cv/",            ("cv/", "resume/")),
]

SEP = "&nbsp;&middot;&nbsp;"


def active_key(rel: str) -> str:
    """Which nav item this page sits under, by longest matching prefix."""
    best, best_len = "index", -1
    for key, _, _, prefixes in ITEMS:
        for prefix in prefixes:
            if rel.startswith(prefix) and len(prefix) > best_len:
                best, best_len = key, len(prefix)
    return best


def build_nav(current: str, keys: list[str], prefix: str, bracket: bool) -> str:
    """One nav block.

    `bracket` reproduces the terminal-style `[projects]` marker the 404 and the
    project article pages use; everywhere else the active item is marked with a
    class so it can be styled rather than punctuated.
    """
    parts = []
    for key, label, href, _ in ITEMS:
        if key not in keys:
            continue
        if key == current:
            text = f"[{label}]" if bracket else label
            cls = "" if bracket else ' class="active"'
            parts.append(f'<a href="{href}"{cls}>{text}</a>')
        else:
            parts.append(f'<a href="{href}">{label}</a>')
    return f'<nav class="top">{prefix}{f" {SEP} ".join(parts)}</nav>'


def pages():
    for path in sorted(ROOT.rglob("*.html")):
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        if path in SKIP_FILES:
            continue
        yield path


def main() -> None:
    keys = [key for key, *_ in ITEMS]
    if not load_posts():
        # Nothing published: a `blog` tab would lead to an empty list.
        keys.remove("blog")

    changed = 0
    skipped_redirects = 0
    for path in pages():
        rel = str(path.relative_to(ROOT))
        html = path.read_text(encoding="utf-8")
        match = NAV_RE.search(html)
        if not match:
            if REDIRECT_RE.search(html) or VERIFICATION_RE.search(html):
                skipped_redirects += 1
            else:
                print(f"warning: no <nav class=\"top\"> in {rel}", file=sys.stderr)
            continue

        old = match.group(0)
        # Keep whatever breadcrumb the page already carries (`~/projects`), and
        # keep its marker convention, so this stays a nav rewrite and not a
        # redesign of pages that deliberately look different.
        prefix_match = re.match(r'<nav class="top">(~/\S+\s*&nbsp;\s*)', old)
        prefix = prefix_match.group(1) if prefix_match else ""
        bracket = "[" in re.sub(r"<[^>]*>", "", old)

        new = build_nav(active_key(rel), keys, prefix, bracket)
        if new != old:
            path.write_text(html.replace(old, new, 1), encoding="utf-8")
            changed += 1

    print(f"apply_nav: rewrote {changed} page(s), "
          f"blog tab {'on' if 'blog' in keys else 'off'}, "
          f"skipped {skipped_redirects} redirect stub(s)")


if __name__ == "__main__":
    main()
