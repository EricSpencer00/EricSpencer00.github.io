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

The tree holds about twice as many .html files as the sitemap holds URLs, and
every part of that gap is deliberate: redirect stubs under projects/<year>/ and
miscellaneous/ share a canonical with the page they point at, and noindex pages
are left out. The run prints the count in each group, so a page that stops being
published moves a number here instead of going missing without a trace.

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

# Not part of the site at all, so not part of the count either.
ARCHIVE = ("/.git/", "/backup-site/", "/.claude/")


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


def audit(listed):
    """Account for every .html file in the tree, listed or not.

    Each file falls in exactly one group, and the groups add up to the file
    count, so the line can be read as a check rather than as a claim.
    """
    grouped = published_pages()
    in_tree = [p for p in ROOT.rglob("*.html")
               if not any(k in "/" + str(p.relative_to(ROOT)) for k in ARCHIVE)]
    files = {p for pages in grouped.values() for p in pages}
    # A canonical with no file of its own is served from another repo.
    elsewhere = sum(1 for pages in grouped.values() if not pages)
    here = len(grouped) - elsewhere
    print(f"  {len(in_tree)} .html files: {len(in_tree) - len(files)} are not "
          f"pages, {len(files) - here} are extra copies of a page already "
          f"listed, {here - (listed - elsewhere)} carry noindex, "
          f"{listed - elsewhere} are listed")
    print(f"  plus {elsewhere} pages served from another repo")


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
    audit(n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
