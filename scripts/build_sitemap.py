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

The walk covers every directory, projects/ and miscellaneous/ and the year
mirrors included. The sitemap is much shorter than the file count because most
of those files are not pages a crawler should fetch. The script prints the
accounting on every run, so the gap stays checkable:

  redirect stub  a Hugo mirror such as /projects/2025/gitkey/ that points at
                 /projects/gitkey.html. The target is listed; the stub is not.
  noindex        404, the resume, and retired project pages.
  off-site       /stem-player/, whose canonical is stemacle.com.
  not a page     the post template, the tests, the Search Console token.

    python3 scripts/build_sitemap.py
"""

import re
import subprocess
import sys
from pathlib import Path

from build_og_images import SITE, SKIP, published_pages

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


def entries(dropped):
    for url, pages in sorted(published_pages().items()):
        # Redirect stubs are never the page a URL is about; they point at one.
        # They have to be dropped before the noindex check, or a noindexed page
        # would still get listed on the strength of a stub aimed at it.
        local = [p for p in pages
                 if STUB not in p.read_text(errors="replace")]
        dropped["redirect stub"] += len(pages) - len(local)
        if not local:
            # No page of its own in this tree: either it is served from another
            # repo, or only redirect stubs point at it. Either way it is real.
            yield url, None
            continue
        if all(NOINDEX.search(p.read_text(errors="replace")) for p in local):
            dropped["noindex"] += len(local)
            continue
        dropped["mirror of a listed page"] += len(local) - 1
        dropped["listed"] += 1
        dates = sorted(filter(None, (last_commit(p) for p in local)))
        yield url, (dates[-1] if dates else None)


def unpublished():
    """The HTML files published_pages() never offers, and why.

    Counted here rather than inferred, so the printed accounting adds up to the
    number of files on disk instead of to an assumption about them.
    """
    out = {"not a page": 0, "off-site canonical": 0}
    for path in ROOT.rglob("*.html"):
        rel = "/" + str(path.relative_to(ROOT))
        if "/backup-site/" in rel or "/.git/" in rel:
            continue
        if any(k in rel for k in SKIP):
            out["not a page"] += 1
            continue
        m = re.search(r'<link rel="canonical" href="([^"]+)"',
                      path.read_text(errors="replace"))
        if m and not m.group(1).startswith(SITE):
            out["off-site canonical"] += 1
        elif m and "YOUR-SLUG" in m.group(1):
            out["not a page"] += 1
    return out


def main():
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    dropped = dict.fromkeys(
        ("listed", "redirect stub", "noindex", "mirror of a listed page"), 0)
    n = 0
    for url, lastmod in entries(dropped):
        lines.append("  <url>")
        lines.append(f"    <loc>{url}</loc>")
        if lastmod:
            lines.append(f"    <lastmod>{lastmod}</lastmod>")
        lines.append("  </url>")
        n += 1
    lines.append("</urlset>")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote sitemap.xml with {n} URLs")

    dropped.update(unpublished())
    total = sum(dropped.values())
    for reason, count in sorted(dropped.items(), key=lambda kv: -kv[1]):
        print(f"  {count:4}  {reason}")
    print(f"  {total:4}  HTML files outside backup-site/")
    # The rest of the URLs are pages GitHub Pages serves from their own repos,
    # so they have no file here to count.
    print(f"  {n - dropped['listed']:4}  URLs served from another repo")
    return 0


if __name__ == "__main__":
    sys.exit(main())
