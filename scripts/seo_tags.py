#!/usr/bin/env python3
"""Head hygiene that every published page needs and no generator owns.

Three things, applied to every page that is not an archive:

  favicon       Google draws the site's icon next to its result. Without a
                <link rel="icon"> and a file behind it there is a blank square.
  robots        The default snippet and image-preview limits are conservative;
                max-image-preview:large is what turns the link card into a
                readable preview in search.
  schema image  The Person/Article `image` used to point at
                /ericspencer-site-backup/, a path this repo does not build.
                Each page is pointed at its own link-preview card instead.

Idempotent: run it after the generators and after apply_og_tags.py.

    python3 scripts/seo_tags.py
    python3 scripts/seo_tags.py --check   # report, change nothing
"""

import argparse
import re
import sys
from pathlib import Path

from build_og_images import SITE, published_pages

ROOT = Path(__file__).resolve().parent.parent
DEAD_IMAGE = f"{SITE}/ericspencer-site-backup/images/avatar.jpeg"
FALLBACK_IMAGE = f"{SITE}/assets/og/home.jpg"

ICONS = (
    '<link rel="icon" href="/favicon.svg" type="image/svg+xml">\n'
    '<link rel="icon" href="/favicon.ico" sizes="32x32">\n'
    '<link rel="apple-touch-icon" href="/apple-touch-icon.png">\n'
    '<meta name="theme-color" content="#faf7f2">\n'
)
ICON_MARKER = 'rel="icon" href="/favicon.svg"'

ROBOTS = '<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">'


def og_image(head):
    m = re.search(r'<meta[^>]+property="og:image"[^>]+content="([^"]+)"', head)
    return m.group(1) if m else None


def apply(path):
    text = path.read_text(encoding="utf-8", errors="replace")
    head, sep, body = text.partition("</head>")
    if not sep:
        return "no-head"
    original = text

    # The structured-data image should be the page's own card when it has one.
    if DEAD_IMAGE in head:
        head = head.replace(DEAD_IMAGE, og_image(head) or FALLBACK_IMAGE)

    if ICON_MARKER not in head:
        anchor = re.search(r'^[ \t]*<link rel="canonical"[^>]*>\n', head, re.M)
        if anchor:
            at = anchor.end()
            head = head[:at] + ICONS + head[at:]
        else:
            m = re.search(r"</title>\n", head)
            at = m.end() if m else len(head)
            head = head[:at] + ICONS + head[at:]

    # Only widen the previews on pages that already opt into indexing. A page
    # carrying noindex is meant to stay out, and this must not undo that.
    head = re.sub(
        r'<meta name="robots" content="index,\s*follow">', ROBOTS, head
    )

    updated = head + sep + body
    if updated == original:
        return "same"
    path.write_text(updated, encoding="utf-8")
    return "wrote"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    counts = {}
    for pages in published_pages().values():
        for path in pages:
            result = "would-write" if args.check else apply(path)
            counts[result] = counts.get(result, 0) + 1
    print(", ".join(f"{v} {k}" for k, v in sorted(counts.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
