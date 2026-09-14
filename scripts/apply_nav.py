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
SKIP_DIRS = {".git", ".claude", "backup-site", "editor", "node_modules", "assets", "tests"}
SKIP_FILES = {ROOT / "blog" / "_template.html"}
OWN_NAV_PAGES = {ROOT / "news" / "index.html", ROOT / "projects.html"}
LIVE_PROJECTS = {"1rm", "stem-player", "ulam-spiral", "ulam-spiral-b12"}

NAV_RE = re.compile(r'<nav class="top"[^>]*>.*?</nav>', re.DOTALL)

# A page whose whole body is a redirect stub has no header to hang a nav on.
REDIRECT_RE = re.compile(r'location\.replace|This page has moved|This page lives at|<!-- redirect stub -->')

# Search-console verification files are a single line of text served as .html.
VERIFICATION_RE = re.compile(r"google-site-verification", re.IGNORECASE)

# key, label, href, and the path prefix that makes this item the active one.
ITEMS = [
    ("index",    "index",    "/",               ()),
    ("research", "publications", "/research.html",  ("research.html",)),
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


def build_nav(current: str, keys: list[str]) -> str:
    """One nav block.

    The public pages share the landing page's quiet text navigation. Active
    state is a class, not a breadcrumb or terminal-style punctuation.
    """
    parts = []
    for key, label, href, _ in ITEMS:
        if key not in keys:
            continue
        if key == current:
            text = label
            cls = ' class="active"'
            parts.append(f'<a href="{href}"{cls}>{text}</a>')
        else:
            parts.append(f'<a href="{href}">{label}</a>')
    links = f" {SEP} ".join(parts)
    return f'<nav class="top">{links}</nav>'


def pages():
    for path in sorted(ROOT.rglob("*.html")):
        relative = path.relative_to(ROOT)
        if any(part in SKIP_DIRS for part in relative.parts):
            continue
        # These are source trees for live builds, not editorial project pages.
        # Their public route mirrors are updated separately and retain their
        # product-specific navigation.
        if len(relative.parts) > 2 and relative.parts[0] == "projects" and relative.parts[1] in LIVE_PROJECTS:
            continue
        # The catalog and public-build hub own labelled navigation with their
        # active state. News deliberately offers a single back link to its
        # chronological origin on the home page.
        if path in OWN_NAV_PAGES:
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
        new = build_nav(active_key(rel), keys)
        if new != old:
            path.write_text(html.replace(old, new, 1), encoding="utf-8")
            changed += 1

    print(f"apply_nav: rewrote {changed} page(s), "
          f"blog tab {'on' if 'blog' in keys else 'off'}, "
          f"skipped {skipped_redirects} redirect stub(s)")


if __name__ == "__main__":
    main()
