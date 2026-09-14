#!/usr/bin/env python3
"""Keep the old root .html hub URLs as noindex redirects.

GitHub Pages cannot emit a server-side redirect from a checked-in static file,
so these compatibility files use a meta refresh, an inline fallback, and an
ordinary link. The clean directory route owns the canonical metadata.
"""

from __future__ import annotations

import argparse
import html
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://ericspencer.us"

HUBS = {
    ROOT / "projects.html": ("Projects | Eric Spencer", "/projects/"),
    ROOT / "research.html": ("Publications | Eric Spencer", "/research/"),
}


def redirect(title: str, path: str) -> str:
    safe_title = html.escape(title)
    safe_path = html.escape(path, quote=True)
    target = f"{SITE}{path}"
    safe_target = html.escape(target, quote=True)
    return f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{safe_title}</title>
<meta name="robots" content="noindex, follow">
<link rel="canonical" href="{safe_target}">
<meta http-equiv="refresh" content="0; url={safe_path}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<!-- redirect stub -->
</head><body><main>
<p>This page lives at <a href="{safe_path}">{safe_path}</a>.</p>
<script>location.replace({target!r});</script>
</main></body></html>
'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    stale = []
    for path, (title, target) in HUBS.items():
        actual = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
        safe_target = html.escape(f"{SITE}{target}", quote=True)
        current = (
            "<!-- redirect stub -->" in actual
            and '<meta name="robots" content="noindex, follow">' in actual
            and f'<link rel="canonical" href="{safe_target}">' in actual
            and f'<meta http-equiv="refresh" content="0; url={target}">' in actual
        )
        if not current:
            stale.append(path)
            if not args.check:
                path.write_text(redirect(title, target), encoding="utf-8")
    if stale and args.check:
        print(
            "legacy hub redirects are stale:\n"
            + "\n".join(str(p.relative_to(ROOT)) for p in stale),
            file=sys.stderr,
        )
        return 1
    action = "need updating" if args.check else "updated"
    print(f"{len(stale)} legacy hub redirect(s) {action}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
