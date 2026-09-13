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


def render_row(app: dict[str, str]) -> str:
    return (
        '<li class="app">'
        f'<a href="{html.escape(app_path(app), quote=True)}">{html.escape(app["name"])}</a>'
        f'<span>{html.escape(app["description"])}</span>'
        '</li>'
    )


def render_index(apps: list[dict[str, str]]) -> str:
    rows = "\n".join(render_row(app) for app in apps)
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Public Builds | Eric Spencer</title>
<meta name="description" content="{len(apps)} public apps, tools, and interactive builds by Eric Spencer.">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
<link rel="canonical" href="{SITE}/apps/">
<meta property="og:type" content="website">
<meta property="og:title" content="Public Builds | Eric Spencer">
<meta property="og:description" content="{len(apps)} public apps, tools, and interactive builds.">
<meta property="og:url" content="{SITE}/apps/">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="Public Builds | Eric Spencer">
<meta name="twitter:description" content="{len(apps)} public apps, tools, and interactive builds.">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap">
<style>
:root{{--paper:#faf7f2;--ink:#16120f;--accent:#5f000b;--dim:#625d57;--rule:#d6d0c8}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.6 "Plus Jakarta Sans",system-ui,sans-serif}}
.wrap{{max-width:920px;margin:0 auto;padding:56px 24px 96px}} .name{{margin:0;font-size:clamp(2.25rem,5vw,3.5rem);letter-spacing:-.045em;line-height:1.05}}
nav{{margin:16px 0 0;font-size:.9rem;color:var(--dim)}} nav a{{color:inherit;text-decoration:none;padding:2px}} nav a:hover,nav a.active{{color:var(--ink)}} nav a.active{{font-weight:700}}
hr{{border:0;border-top:1px solid var(--rule);margin:28px 0}} h1{{margin:0;font-size:clamp(1.7rem,3vw,2.35rem);letter-spacing:-.035em;line-height:1.15}}
.intro{{max-width:65ch;color:var(--dim);margin:12px 0 28px}} .app-list{{list-style:none;padding:0;margin:0;border-top:1px solid var(--rule)}}
.app{{display:grid;grid-template-columns:minmax(13rem,.8fr) minmax(0,1.8fr);gap:16px;padding:14px 0;border-bottom:1px solid var(--rule)}} .app a{{font-weight:700;color:var(--ink);text-decoration:none;overflow-wrap:anywhere}} .app a:hover{{color:var(--accent);text-decoration:underline;text-underline-offset:3px}} .app span{{color:var(--dim);overflow-wrap:anywhere}}
footer{{margin-top:56px;color:var(--dim);font-size:.85rem}} a:focus-visible{{outline:3px solid color-mix(in srgb,var(--accent) 40%,transparent);outline-offset:3px}}
@media(max-width:620px){{.wrap{{padding:36px 18px 72px}}.app{{grid-template-columns:1fr;gap:3px;padding:15px 0}}}}
</style></head><body><div class="wrap">
<p class="name">Eric Spencer</p>
<nav aria-label="Primary"><a href="/">index</a> · <a href="/research.html">research</a> · <a href="/projects.html">projects</a> · <a href="/apps/" class="active" aria-current="page">apps</a> · <a href="/cv/">cv</a></nav>
<hr><main><h1>Public builds</h1>
<p class="intro">{len(apps)} public apps, tools, and interactive builds. Each path starts here and opens the public build; source code is not required to be public.</p>
<ul class="app-list">{rows}</ul>
</main><footer>© 2026 Eric Spencer · Chicago, IL · <a href="mailto:eric@ericspencer.us">eric@ericspencer.us</a></footer>
</div></body></html>
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
    output = {OUT / "index.html": render_index(apps)}
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
    """Check generated content while allowing the SEO pass to enrich the hub."""
    index = OUT / "index.html"
    if not index.exists():
        return False
    if stale_aliases(expected_paths(apps)):
        return False
    match = re.search(r'<ul class="app-list">(.*?)</ul>', index.read_text(encoding="utf-8"), re.S)
    expected_rows = "\n".join(render_row(app) for app in apps)
    if not match or match.group(1) != expected_rows:
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
