#!/usr/bin/env python3
"""Build the public-build directory and its stable portfolio aliases.

An app's source can be private, public, or split across repositories. The
portfolio should link to the thing a visitor can actually use, so this manifest
stores only public destinations. `/apps/<slug>/` is a durable entry path on
ericspencer.us; its noindex redirect hands canonical ownership to the product.

    python3 scripts/build_public_apps.py
    python3 scripts/build_public_apps.py --check
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "content" / "public-apps.json"
OUT = ROOT / "apps"
SITE = "https://ericspencer.us"


def load_apps() -> list[dict[str, str]]:
    apps = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if not isinstance(apps, list):
        raise ValueError("public-apps.json must contain a JSON array")

    slugs: set[str] = set()
    names: set[str] = set()
    urls: set[str] = set()
    for app in apps:
        for field in ("slug", "name", "url", "description"):
            if not isinstance(app.get(field), str) or not app[field].strip():
                raise ValueError(f"app is missing {field}: {app!r}")
        slug = app["slug"]
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
            raise ValueError(f"invalid app slug: {slug}")
        if not app["url"].startswith("https://"):
            raise ValueError(f"app destination must be public HTTPS: {app['url']}")
        if slug in slugs or app["name"].casefold() in names or app["url"] in urls:
            raise ValueError(f"duplicate app entry: {app!r}")
        slugs.add(slug)
        names.add(app["name"].casefold())
        urls.add(app["url"])
    ordered = sorted(apps, key=lambda app: app["name"].casefold())
    if apps != ordered:
        raise ValueError("public-apps.json must be sorted by app name")
    return ordered


def app_path(app: dict[str, str]) -> str:
    return f"/apps/{app['slug']}/"


def render_index() -> str:
    target = f"{SITE}/projects.html"
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Projects | Eric Spencer</title>
<meta name="robots" content="noindex, follow">
<link rel="canonical" href="{target}">
<meta http-equiv="refresh" content="0; url={target}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<!-- redirect stub -->
</head><body><p>See <a href="/projects.html">projects</a>.</p><script>location.replace({json.dumps(target)});</script></body></html>
"""


def render_redirect(app: dict[str, str]) -> str:
    target = html.escape(app["url"], quote=True)
    name = html.escape(app["name"])
    return f"""<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{name} | Eric Spencer</title><meta name="robots" content="noindex, follow">
<link rel="canonical" href="{target}"><meta http-equiv="refresh" content="0; url={target}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml"><!-- redirect stub -->
</head><body><p>Opening <a href="{target}">{name}</a>.</p><script>location.replace({json.dumps(app['url'])});</script></body></html>
"""


def expected_paths(apps: list[dict[str, str]]) -> dict[Path, str]:
    output = {OUT / "index.html": render_index()}
    for app in apps:
        output[OUT / app["slug"] / "index.html"] = render_redirect(app)
    return output


def stale_aliases(output: dict[Path, str]) -> list[Path]:
    """Find obsolete, generator-owned aliases without touching real content."""
    if not OUT.exists():
        return []
    stale = []
    for child in OUT.iterdir():
        page = child / "index.html"
        if not child.is_dir() or page in output or not page.exists():
            continue
        if "<!-- redirect stub -->" not in page.read_text(encoding="utf-8"):
            continue
        # A generated alias contains exactly one small redirect file. Refuse to
        # delete anything a person has added to the directory.
        if list(child.iterdir()) == [page]:
            stale.append(page)
    return stale


def is_current(apps: list[dict[str, str]]) -> bool:
    """Check generated aliases while allowing the SEO pass to enrich them."""
    index = OUT / "index.html"
    if not index.exists():
        return False
    if stale_aliases(expected_paths(apps)):
        return False
    index_text = index.read_text(encoding="utf-8")
    target = html.escape(f"{SITE}/projects.html", quote=True)
    if ("<!-- redirect stub -->" not in index_text
            or '<meta name="robots" content="noindex, follow">' not in index_text
            or f'<link rel="canonical" href="{target}">' not in index_text
            or f'content="0; url={target}"' not in index_text):
        return False

    for app in apps:
        page = OUT / app["slug"] / "index.html"
        if not page.exists():
            return False
        text = page.read_text(encoding="utf-8")
        target = html.escape(app["url"], quote=True)
        if ("<!-- redirect stub -->" not in text
                or '<meta name="robots" content="noindex, follow">' not in text
                or f'<link rel="canonical" href="{target}">' not in text
                or f'content="0; url={target}"' not in text):
            return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    apps = load_apps()
    output = expected_paths(apps)
    if args.check:
        if not is_current(apps):
            print("public app pages are stale; run python3 scripts/build_public_apps.py", file=sys.stderr)
            return 1
        print(f"public app pages are current ({len(apps)} builds)")
        return 0
    for stale in stale_aliases(output):
        stale.unlink()
        stale.parent.rmdir()
    for path, text in output.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    print(f"Built {len(apps)} public build paths -> apps/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
