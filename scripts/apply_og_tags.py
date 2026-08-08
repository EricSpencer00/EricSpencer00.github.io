#!/usr/bin/env python3
"""Point every published page at its own link-preview card.

Rewrites the og:image / twitter:image block in each page's <head> so it names
the card that build_og_images.py made for that page, and upgrades the Twitter
card type to summary_large_image -- the difference between a thumbnail the size
of a favicon and a preview someone can actually read.

Idempotent: run it after every card rebuild.

    python3 scripts/apply_og_tags.py
    python3 scripts/apply_og_tags.py --check   # report, change nothing
"""

import argparse
import html
import re
import sys
from pathlib import Path

from build_og_images import OUT, SITE, published_pages, slug_for

ROOT = Path(__file__).resolve().parent.parent
CARD_W, CARD_H = 1200, 630

# Tags this script owns. Everything matching is stripped and rewritten, so a
# page never ends up with two competing og:image values.
OWNED = re.compile(
    r'^[ \t]*<meta[^>]+(?:property|name)="'
    r'(?:og:image(?::\w+)?|twitter:(?:card|image(?::\w+)?)|linkedin:image)"[^>]*>\n?',
    re.M,
)


def block(slug, alt):
    url = f"{SITE}/assets/og/{slug}.jpg"
    return (
        f'<meta property="og:image" content="{url}">\n'
        f'<meta property="og:image:type" content="image/jpeg">\n'
        f'<meta property="og:image:width" content="{CARD_W}">\n'
        f'<meta property="og:image:height" content="{CARD_H}">\n'
        f'<meta property="og:image:alt" content="{alt}">\n'
        f'<meta name="twitter:card" content="summary_large_image">\n'
        f'<meta name="twitter:image" content="{url}">\n'
        f'<meta name="twitter:image:alt" content="{alt}">\n'
        f'<meta property="linkedin:image" content="{url}">\n'
    )


def meta_value(head, key):
    m = re.search(
        rf'<meta[^>]+(?:property|name)="{re.escape(key)}"[^>]+content="([^"]*)"', head
    )
    return m.group(1) if m else None


def apply(path, slug):
    text = path.read_text(encoding="utf-8", errors="replace")
    head, sep, body = text.partition("</head>")
    if not sep:
        return "no-head"

    title = meta_value(head, "og:title") or ""
    if not title:
        m = re.search(r"<title>(.*?)</title>", head, re.S)
        title = html.escape(m.group(1).strip()) if m else "Eric Spencer"
    alt = f"{title} — ericspencer.us"

    new_head = OWNED.sub("", head)

    # A large card with no title or description renders as a bare image in
    # Twitter and Slack. Backfill from the Open Graph values.
    added = ""
    for tw, og in (("twitter:title", "og:title"), ("twitter:description", "og:description")):
        if not meta_value(new_head, tw):
            val = meta_value(new_head, og)
            if val:
                added += f'<meta name="{tw}" content="{val}">\n'

    # Anchor the block after og:url when there is one, so the Open Graph tags
    # stay together; otherwise after the canonical link.
    anchor = re.search(r'^[ \t]*<meta[^>]+property="og:url"[^>]*>\n', new_head, re.M)
    if not anchor:
        anchor = re.search(r"^[ \t]*<link rel=\"canonical\"[^>]*>\n", new_head, re.M)
    insert = block(slug, alt) + added
    if anchor:
        at = anchor.end()
        new_head = new_head[:at] + insert + new_head[at:]
    else:
        new_head = new_head.rstrip("\n") + "\n" + insert

    updated = new_head + sep + body
    if updated == text:
        return "same"
    path.write_text(updated, encoding="utf-8")
    return "wrote"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    counts = {}
    missing = []
    for url, pages in sorted(published_pages().items()):
        slug = slug_for(url)
        if not (OUT / f"{slug}.jpg").exists():
            # No card -- usually a page that is not live yet. Leave its tags
            # alone rather than pointing them at an image that does not exist.
            missing.append(url)
            continue
        for path in pages:
            result = "would-write" if args.check else apply(path, slug)
            counts[result] = counts.get(result, 0) + 1

    print(", ".join(f"{v} {k}" for k, v in sorted(counts.items())))
    for url in missing:
        print(f"  no card, skipped: {url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
