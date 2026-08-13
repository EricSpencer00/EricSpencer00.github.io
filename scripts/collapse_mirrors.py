#!/usr/bin/env python3
"""Turn the old Hugo URLs into redirects instead of second copies.

Every project page exists twice: at /projects/<slug>.html, and at the Hugo path
it had before the rewrite -- /projects/<year>/<slug>/ or /miscellaneous/<slug>/.
The mirrors already canonicalise to the real page, but they still serve a full
copy of it, so a crawler spends a fetch on each one and finds nothing new. On a
site Google is crawling as slowly as this one, that is 58 fetches that could
have gone to a page that is actually waiting to be indexed.

This replaces each mirror with a stub that redirects. The URL keeps working for
anyone holding an old link; the duplicate stops being served.

Idempotent: a file that is already a stub is left alone.

    python3 scripts/collapse_mirrors.py
    python3 scripts/collapse_mirrors.py --check
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://ericspencer.us"
MARKER = "<!-- redirect stub -->"

STUB = """<!doctype html><html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<link rel="canonical" href="{url}">
<meta http-equiv="refresh" content="0; url={path}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<meta name="theme-color" content="#faf7f2">
{marker}
<style>
body{{margin:0;background:#faf7f2;color:#191410;font:16px/1.7 "Plus Jakarta Sans",-apple-system,BlinkMacSystemFont,sans-serif}}
main{{max-width:34rem;margin:0 auto;padding:15vh 24px}}
a{{color:#6e1a19}}
</style>
</head><body><main>
<p>This page lives at <a href="{path}">{path}</a>.</p>
</main></body></html>
"""


def mirrors():
    yield from sorted(ROOT.glob("projects/20*/*/index.html"))
    yield from sorted(ROOT.glob("miscellaneous/*/index.html"))


def convert(path):
    text = path.read_text(encoding="utf-8", errors="replace")
    if MARKER in text:
        return "already-stub"
    m = re.search(r'<link rel="canonical" href="(' + re.escape(SITE) + r'/[^"]+)"', text)
    if not m:
        return "no-canonical"
    url = m.group(1)
    if url.rstrip("/") == SITE + "/" + str(path.parent.relative_to(ROOT)):
        return "self-canonical"  # not a mirror; it is the real page
    t = re.search(r"<title>(.*?)</title>", text, re.S)
    title = t.group(1).strip() if t else "Eric Spencer"
    path.write_text(
        STUB.format(title=title, url=url, path=url[len(SITE):], marker=MARKER),
        encoding="utf-8",
    )
    return "wrote"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    counts = {}
    for path in mirrors():
        if args.check:
            result = "would-write" if MARKER not in path.read_text(errors="replace") else "already-stub"
        else:
            result = convert(path)
        counts[result] = counts.get(result, 0) + 1
    print(", ".join(f"{v} {k}" for k, v in sorted(counts.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
