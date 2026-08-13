#!/usr/bin/env python3
"""Write sitemap.xml from the pages that are actually published.

The list is derived the same way the link-preview cards are: one entry per
canonical URL, so the old Hugo mirrors never appear alongside the page they
redirect to. Pages carrying noindex are left out -- listing a URL and then
telling Google not to index it is a contradiction it reports as an error.

`lastmod` is the file's last commit date, not the day the build ran. A sitemap
where every page changed today tells a crawler nothing about which pages are
worth re-fetching.

`changefreq` and `priority` are omitted: Google ignores both.

    python3 scripts/build_sitemap.py
"""

import re
import subprocess
import sys
from pathlib import Path

from build_og_images import SITE, published_pages

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "sitemap.xml"

NOINDEX = re.compile(r'<meta[^>]+name="robots"[^>]+content="[^"]*noindex', re.I)
STUB = "<!-- redirect stub -->"


def last_commit(path):
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", str(path)],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout.strip()
        return out or None
    except subprocess.CalledProcessError:
        return None


def entries():
    for url, pages in sorted(published_pages().items()):
        # Redirect stubs are never the page a URL is about; they point at one.
        # They have to be dropped before the noindex check, or a noindexed page
        # would still get listed on the strength of a stub aimed at it.
        local = [p for p in pages
                 if STUB not in p.read_text(errors="replace")]
        if not local:
            # No page of its own in this tree: either it is served from another
            # repo, or only redirect stubs point at it. Either way it is real.
            yield url, None
            continue
        if all(NOINDEX.search(p.read_text(errors="replace")) for p in local):
            continue
        dates = sorted(filter(None, (last_commit(p) for p in local)))
        yield url, (dates[-1] if dates else None)


def main():
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    n = 0
    for url, lastmod in entries():
        lines.append("  <url>")
        lines.append(f"    <loc>{url}</loc>")
        if lastmod:
            lines.append(f"    <lastmod>{lastmod}</lastmod>")
        lines.append("  </url>")
        n += 1
    lines.append("</urlset>")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote sitemap.xml with {n} URLs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
