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


def first_title(head):
    m = re.search(r"<title>(.*?)</title>", head, re.S)
    return html.escape(re.sub(r"\s+", " ", m.group(1)).strip()) if m else "Eric Spencer"


def canonical_url(head):
    m = re.search(r'<link rel="canonical" href="([^"]+)"', head)
    return m.group(1) if m else None


def apply(path, slug, write=True, include_card=True):
    text = path.read_text(encoding="utf-8", errors="replace")
    head, sep, body = text.partition("</head>")
    if not sep:
        return "no-head"

    title = meta_value(head, "og:title") or first_title(head)
    description = meta_value(head, "og:description") or meta_value(head, "description")
    canonical = canonical_url(head)
    alt = f"{title} — ericspencer.us"

    # Preserve an authored image when this page has no generated card. Social
    # title/description/URL metadata still belongs on every public page.
    new_head = OWNED.sub("", head) if include_card else head

    # Every indexable page gets a complete social identity, even when its
    # original template only supplied a title, description, and canonical.
    missing_og = ""
    if not meta_value(new_head, "og:title"):
        missing_og += f'<meta property="og:title" content="{title}">\n'
    if description and not meta_value(new_head, "og:description"):
        missing_og += f'<meta property="og:description" content="{description}">\n'
    if canonical and not meta_value(new_head, "og:url"):
        missing_og += f'<meta property="og:url" content="{canonical}">\n'

    # A large card with no title or description renders as a bare image in
    # Twitter and Slack. Backfill from the Open Graph values.
    added = ""
    for tw, value in (("twitter:title", title), ("twitter:description", description)):
        if not meta_value(new_head, tw):
            if value:
                added += f'<meta name="{tw}" content="{value}">\n'

    # Anchor the block after og:url when there is one, so the Open Graph tags
    # stay together; otherwise after the canonical link.
    anchor = re.search(r'^[ \t]*<meta[^>]+property="og:url"[^>]*>\n', new_head, re.M)
    if not anchor:
        anchor = re.search(r"^[ \t]*<link rel=\"canonical\"[^>]*>\n", new_head, re.M)
    if not anchor:
        anchor = re.search(r'^[ \t]*<meta[^>]+property="og:title"[^>]*>\n', new_head, re.M)
    image_tags = block(slug, alt) if include_card else ""
    insert = missing_og + image_tags + added
    if anchor:
        at = anchor.end()
        new_head = new_head[:at] + insert + new_head[at:]
    else:
        new_head = new_head.rstrip("\n") + "\n" + insert

    updated = new_head + sep + body
    if updated == text:
        return "same"
    if not write:
        return "would-write"
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
        include_card = (OUT / f"{slug}.jpg").exists()
        if not include_card:
            missing.append(url)
        for path in pages:
            result = apply(path, slug, write=not args.check, include_card=include_card)
            counts[result] = counts.get(result, 0) + 1

    print(", ".join(f"{v} {k}" for k, v in sorted(counts.items())))
    for url in missing:
        print(f"  no card, metadata only: {url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
