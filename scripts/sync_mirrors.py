#!/usr/bin/env python3
"""Keep every old Hugo URL a redirect to the one real page.

A project article can be reachable at three paths: /projects/<slug>.html,
/projects/<year>/<slug>/ and sometimes /miscellaneous/<slug>/. Only the first
is the page. The others are redirect stubs that point at it.

The stubs used to be hand-copied, so they drifted: projects/2026/aeo-queries/
still served a whole earlier draft of the article under its own URL. This
script rebuilds a stub from its canonical page whenever the two disagree, and
reports a mirror that is not on the list at all -- a hand-copy nobody
registered -- instead of guessing where it should point.

The list is scripts/mirrors.txt, one `mirror path | canonical URL path` per
line. Add a line when you add a project; the script will not invent one.

Idempotent, and it leaves a correct stub untouched, so the link-preview tags
apply_og_tags.py writes into the stubs survive a run.

    python3 scripts/sync_mirrors.py
    python3 scripts/sync_mirrors.py --check   # report, change nothing, exit 1 on drift
"""

import argparse
import re
import sys
from pathlib import Path

from build_og_images import EXTERNAL, SITE

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = Path(__file__).resolve().parent / "mirrors.txt"
MARKER = "<!-- redirect stub -->"

# Pages GitHub Pages serves out of their own repos. Their HTML is not in this
# tree, so a mirror pointing at one has nothing here to check against.
OFFSITE = {url[len(SITE):] for url in EXTERNAL}

STUB = """<!doctype html><html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<link rel="canonical" href="{site}{path}">
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


def listed():
    """Yield (mirror path, canonical URL path) from the manifest."""
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            mirror, canonical = (p.strip() for p in line.split("|", 1))
            yield ROOT / mirror, canonical


def on_disk():
    yield from sorted(ROOT.glob("projects/20*/*/index.html"))
    yield from sorted(ROOT.glob("miscellaneous/*/index.html"))


def canonical_file(path):
    """The file that serves a canonical URL path, or None if it is offsite."""
    if path in OFFSITE:
        return None
    rel = path.lstrip("/")
    return ROOT / (rel + "index.html" if rel.endswith("/") else rel)


def title_of(text):
    m = re.search(r"<title>(.*?)</title>", text, re.S)
    return m.group(1).strip() if m else "Eric Spencer"


def sub(pattern, replacement, text):
    """re.sub, and say whether it changed anything."""
    new, n = re.subn(pattern, lambda _: replacement, text, count=1)
    return new, bool(n) and new != text


def sync(mirror, canonical, title, write):
    """Bring one mirror in line with its canonical page. Returns a verdict."""
    text = mirror.read_text(encoding="utf-8", errors="replace")

    if MARKER not in text:
        if write:
            mirror.write_text(
                STUB.format(title=title, site=SITE, path=canonical, marker=MARKER),
                encoding="utf-8",
            )
        return "rebuilt (second copy of the article)"

    # Already a stub. Patch only the fields that drifted, so the link-preview
    # tags apply_og_tags.py wrote into it stay where they are.
    fixed = []
    for name, pattern, replacement in (
        ("title", r"<title>.*?</title>", f"<title>{title}</title>"),
        (
            "canonical",
            r'<link rel="canonical" href="[^"]*">',
            f'<link rel="canonical" href="{SITE}{canonical}">',
        ),
        (
            "refresh",
            r'<meta http-equiv="refresh" content="[^"]*">',
            f'<meta http-equiv="refresh" content="0; url={canonical}">',
        ),
        (
            "link",
            r'<a href="[^"]*">[^<]*</a>',
            f'<a href="{canonical}">{canonical}</a>',
        ),
    ):
        text, changed = sub(pattern, replacement, text)
        if changed:
            fixed.append(name)
    if not fixed:
        return None
    if write:
        mirror.write_text(text, encoding="utf-8")
    return "fixed " + ", ".join(fixed)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report only; exit 1 on drift")
    args = ap.parse_args()

    problems, drifted = [], []
    known = set()

    for mirror, canonical in listed():
        rel = mirror.relative_to(ROOT)
        known.add(mirror)
        if not mirror.exists():
            problems.append(f"{rel}: listed but not in the tree")
            continue
        source = canonical_file(canonical)
        if source is None:
            title = title_of(mirror.read_text(encoding="utf-8", errors="replace"))
        elif not source.exists():
            problems.append(f"{rel}: points at {canonical}, which is not in the tree")
            continue
        else:
            title = title_of(source.read_text(encoding="utf-8", errors="replace"))
        verdict = sync(mirror, canonical, title, write=not args.check)
        if verdict:
            drifted.append(f"{rel}: {verdict}")

    for mirror in on_disk():
        if mirror not in known:
            problems.append(
                f"{mirror.relative_to(ROOT)}: not in {MANIFEST.name}; add a line for it"
            )

    for line in drifted + problems:
        print(line)
    if not drifted and not problems:
        print(f"{len(known)} mirrors, all redirecting to their canonical page")
    elif not args.check and not problems:
        print(f"{len(drifted)} rewritten")
    return 1 if problems or (args.check and drifted) else 0


if __name__ == "__main__":
    sys.exit(main())
