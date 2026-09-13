#!/usr/bin/env python3
"""Build the public project catalog from its reviewed manifest.

The catalog deliberately lists public artifacts, not every repository the
account happens to own. A project can link to a live app, paper, writeup, or
public source repository. Private repository URLs never enter the manifest.

    python3 scripts/build_projects.py
    python3 scripts/build_projects.py --check
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "content" / "public-projects.json"
SELECTED = ROOT / "content" / "selected.txt"
OUTPUT = ROOT / "projects.html"
SITE = "https://ericspencer.us"
PAGE_DESCRIPTION = (
    "Selected software, formal-methods research, LLM tools, and live apps by "
    "Eric Spencer, plus a complete catalog of public work."
)


def key(value: str) -> str:
    """Use a conservative key to prevent duplicate catalog rows."""
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def external(url: str) -> bool:
    return url.startswith(("https://", "http://"))


def valid_url(url: str) -> bool:
    """Allow only public web locations or site-root-relative locations."""
    return external(url) or (url.startswith("/") and not url.startswith("//"))


def absolute_url(url: str) -> str:
    return url if external(url) else SITE + url


def load_projects() -> list[dict[str, str]]:
    projects = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if not isinstance(projects, list):
        raise ValueError("public-projects.json must contain a JSON array")

    seen: set[str] = set()
    seen_urls: set[str] = set()
    names: list[str] = []
    for project in projects:
        for field in ("name", "url", "description"):
            if not isinstance(project.get(field), str) or not project[field].strip():
                raise ValueError(f"project is missing {field}: {project!r}")
        project["language"] = str(project.get("language", "")).strip()
        name_key = key(project["name"])
        if name_key in seen:
            raise ValueError(f"duplicate catalog project: {project['name']}")
        seen.add(name_key)
        names.append(project["name"])
        if not valid_url(project["url"]):
            raise ValueError(f"project URL must be https://, http://, or root-relative: {project['url']}")
        if project["url"] in seen_urls:
            raise ValueError(f"duplicate catalog destination: {project['url']}")
        seen_urls.add(project["url"])
    if names != sorted(names, key=str.casefold):
        raise ValueError("public-projects.json must be sorted A–Z by project name")
    return sorted(projects, key=lambda item: item["name"].casefold())


def load_selected() -> list[dict[str, str]]:
    """Load the smaller editorial set used for the homepage's lead projects."""
    projects: list[dict[str, str]] = []
    seen: set[str] = set()
    for line_number, raw_line in enumerate(SELECTED.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("|", 2)
        if len(parts) != 3 or not all(part.strip() for part in parts):
            raise ValueError(f"selected.txt line {line_number} must be name|url|description")
        name, url, description = (part.strip() for part in parts)
        name_key = key(name)
        if name_key in seen:
            raise ValueError(f"duplicate selected project: {name}")
        if not valid_url(url):
            raise ValueError(f"selected project URL must be https:// or root-relative: {url}")
        seen.add(name_key)
        projects.append({"name": name, "url": url, "description": description})
    if not projects:
        raise ValueError("selected.txt must contain at least one project")
    return projects


def render_row(project: dict[str, str]) -> str:
    url = html.escape(project["url"], quote=True)
    name = html.escape(project["name"])
    description = html.escape(project["description"])
    attrs = ' target="_blank" rel="noopener"' if external(project["url"]) else ""
    return (
        '<li class="project">'
        f'<a class="project-name" href="{url}"{attrs}>{name}</a>'
        f'<span class="project-description">{description}</span>'
        "</li>"
    )


def render(projects: list[dict[str, str]], selected: list[dict[str, str]]) -> str:
    rows = "\n".join(render_row(project) for project in projects)
    selected_rows = "\n".join(render_row(project) for project in selected)
    selected_items = [
        {
            "@type": "ListItem",
            "position": position,
            "item": {
                "@type": "CreativeWork",
                "name": project["name"],
                "url": absolute_url(project["url"]),
                "description": project["description"],
            },
        }
        for position, project in enumerate(selected, 1)
    ]
    structured_data = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": "Projects & Public Work",
            "url": f"{SITE}/projects.html",
            "description": PAGE_DESCRIPTION,
            "author": {"@type": "Person", "name": "Eric Spencer", "url": f"{SITE}/"},
            "hasPart": {
                "@type": "ItemList",
                "name": "Selected work",
                "numberOfItems": len(selected),
                "itemListElement": selected_items,
            },
        },
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Projects &amp; Public Work | Eric Spencer</title>
<meta name="description" content="{PAGE_DESCRIPTION}">
<meta name="author" content="Eric Spencer">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
<link rel="canonical" href="https://ericspencer.us/projects.html">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta name="theme-color" content="#faf7f2">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline' 'wasm-unsafe-eval' https://esm.run; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https://api.github.com https://huggingface.co; object-src 'self'; base-uri 'self'; form-action 'self'">
<meta property="og:type" content="website">
<meta property="og:title" content="Projects &amp; Public Work | Eric Spencer">
<meta property="og:description" content="{PAGE_DESCRIPTION}">
<meta property="og:url" content="https://ericspencer.us/projects.html">
<meta property="og:image" content="https://ericspencer.us/assets/og/projects.jpg">
<meta property="og:image:alt" content="Projects &amp; Public Work | Eric Spencer">
<meta property="og:site_name" content="Eric Spencer">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Projects &amp; Public Work | Eric Spencer">
<meta name="twitter:description" content="{PAGE_DESCRIPTION}">
<meta name="twitter:image" content="https://ericspencer.us/assets/og/projects.jpg">
<script type="application/ld+json">
{structured_data}
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap">
<style>
:root{{--paper:#faf7f2;--ink:#16120f;--accent:#5f000b;--dim:#625d57;--rule:#d6d0c8;--soft:#f0ebe4}}
*{{box-sizing:border-box}}
html{{scroll-behavior:smooth}}
body{{margin:0;background:var(--paper);color:var(--ink);font-family:"Plus Jakarta Sans",system-ui,sans-serif;font-size:16px;line-height:1.6}}
.wrap{{max-width:960px;margin:0 auto;padding:56px 24px 96px}}
.name{{margin:0;font-size:clamp(2.25rem,5vw,3.5rem);letter-spacing:-.045em;line-height:1.05}}
nav{{margin:16px 0 0;font-size:.9rem;color:var(--dim)}}
nav a{{color:inherit;text-decoration:none;padding:2px}} nav a:hover,nav a[aria-current="page"]{{color:var(--ink)}} nav a[aria-current="page"]{{font-weight:700}}
hr{{border:0;border-top:1px solid var(--rule);margin:28px 0}}
main{{max-width:860px}} h1{{margin:0;font-size:clamp(1.7rem,3vw,2.35rem);letter-spacing:-.035em;line-height:1.15}}
.intro,.section-intro{{max-width:68ch;color:var(--dim);margin:12px 0 24px}}
h2{{font-size:1.15rem;letter-spacing:-.02em;margin:34px 0 10px;line-height:1.25}}
.selected-list{{margin-bottom:28px}}
.project-list{{list-style:none;padding:0;margin:0;border-top:1px solid var(--rule)}}
.project{{display:grid;grid-template-columns:minmax(13rem,.8fr) minmax(0,2fr);gap:16px;align-items:baseline;padding:12px 0;border-bottom:1px solid var(--rule)}}
.project-name{{font-weight:700;color:var(--ink);text-decoration:none;overflow-wrap:anywhere}} .project-name:hover{{color:var(--accent);text-decoration:underline;text-underline-offset:3px}}
.project-description{{color:var(--dim);overflow-wrap:anywhere}} footer{{margin-top:60px;color:var(--dim);font-size:.85rem}}
@media (max-width:680px){{.wrap{{padding:36px 18px 72px}}.project{{grid-template-columns:1fr;gap:3px;padding:14px 0}}}}
</style>
</head>
<body>
<div class="wrap">
<p class="name">Eric Spencer</p>
<nav aria-label="Primary"><a href="/">index</a> · <a href="/research.html">publications</a> · <a href="/projects.html" aria-current="page">projects</a> · <a href="/cv/">cv</a></nav>
<hr>
<main>
<h1>Projects &amp; Public Work</h1>
<p class="intro">{PAGE_DESCRIPTION}</p>
<section aria-labelledby="selected-work">
<h2 id="selected-work">Selected work</h2>
<ol id="selected-project-list" class="project-list selected-list">{selected_rows}</ol>
</section>
<section aria-labelledby="all-projects">
<h2 id="all-projects">Complete project list</h2>
<p class="section-intro">The full public catalog: research artifacts, applications, experiments, coursework, and source repositories.</p>
<ol id="project-list" class="project-list">{rows}</ol>
</section>
</main>
<footer>© 2026 Eric Spencer · Chicago, IL · <a href="mailto:eric@ericspencer.us">eric@ericspencer.us</a></footer>
</div>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail when projects.html is stale")
    args = parser.parse_args()
    projects = load_projects()
    selected = load_selected()
    output = render(projects, selected)
    if args.check:
        if not OUTPUT.exists():
            print("projects.html is stale; run python3 scripts/build_projects.py", file=sys.stderr)
            return 1
        # apply_og_tags.py and seo_tags.py intentionally enrich the generated
        # head later in the release pipeline. Check the manifest-owned body
        # instead of requiring the whole document to remain byte-identical.
        expected_rows = "\n".join(render_row(project) for project in projects)
        expected_selected_rows = "\n".join(render_row(project) for project in selected)
        current = OUTPUT.read_text(encoding="utf-8")
        selected_match = re.search(
            r'<ol id="selected-project-list" class="project-list selected-list">(.*?)</ol>',
            current,
            re.S,
        )
        match = re.search(r'<ol id="project-list" class="project-list">(.*?)</ol>', current, re.S)
        forbidden = (
            'Projects A–Z', 'source repository is never disclosed',
            'catalog-tools',
            'project-filter', 'project-count',
        )
        if (not selected_match or selected_match.group(1) != expected_selected_rows
                or not match or match.group(1) != expected_rows
                or any(text in current for text in forbidden)):
            print("projects.html is stale; run python3 scripts/build_projects.py", file=sys.stderr)
            return 1
        print("projects.html is current")
        return 0
    OUTPUT.write_text(output, encoding="utf-8")
    print(f"Built {len(selected)} selected + {len(projects)} public projects -> projects.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
