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
PRIORITIES = ROOT / "content" / "project-priorities.json"
PUBLIC_APPS = ROOT / "content" / "public-apps.json"
SELECTED = ROOT / "content" / "selected.txt"
OUTPUT = ROOT / "projects" / "index.html"
SITE = "https://ericspencer.us"
PAGE_DESCRIPTION = (
    "Software, research, experiments, coursework, and live apps from Eric Spencer."
)
TIER_ORDER = ("P1", "P1.5", "P2", "P3")
TIER_LABELS = {
    "P1": ("Primary work", "The projects that define the current direction."),
    "P1.5": ("Live apps", ""),
    "P2": ("Other work", ""),
}


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


def project_url_key(url: str) -> str:
    """Return the final path segment used for editorial URL overrides."""
    value = url.rstrip("/").rsplit("/", 1)[-1]
    return key(re.sub(r"\.(?:html?|php)$", "", value))


def load_editorial() -> dict:
    data = json.loads(PRIORITIES.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("project-priorities.json must contain an object")
    for field in ("P1", "P1.5", "P2", "P3", "forks", "last", "additional"):
        if field not in data:
            raise ValueError(f"project-priorities.json is missing {field}")
    return data


def editorial_rank(project: dict[str, str], editorial: dict) -> int:
    """Return the hand-curated quality order, with unknowns after their tier."""
    if any(project_matches(project, token) for token in editorial["last"]):
        return 1000000
    tier_tokens = {
        "P1": editorial["P1"],
        "P1.5": editorial["P1.5"],
        "P2": editorial["P2"],
        "P3": editorial["P3"] + editorial["forks"],
    }
    offset = 0
    for tier in TIER_ORDER:
        tokens = tier_tokens[tier]
        for position, token in enumerate(tokens):
            if project_matches(project, token):
                return offset + position
        offset += len(tokens) + 1
    return offset + 1000


def project_matches(project: dict[str, str], token: str) -> bool:
    token_key = key(token)
    return token_key in {
        key(project["name"]),
        key(project["url"]),
        project_url_key(project["url"]),
    }


def load_live_apps() -> list[dict[str, str]]:
    editorial = load_editorial()
    apps = json.loads(PUBLIC_APPS.read_text(encoding="utf-8"))
    if not isinstance(apps, list):
        raise ValueError("public-apps.json must contain an array")
    live_apps = []
    for app in apps:
        for field in ("slug", "name", "url", "description"):
            if not isinstance(app.get(field), str) or not app[field].strip():
                raise ValueError(f"app is missing {field}: {app!r}")
        if len(app["description"].split()) > 5:
            raise ValueError(f"app description must be five words or fewer: {app!r}")
        live_app = dict(app)
        live_app["is_live_app"] = True
        live_app["rank"] = editorial_rank(live_app, editorial)
        live_apps.append(live_app)
    return sorted(live_apps, key=lambda item: (item["rank"], item["name"].casefold()))


def live_app_for(
    project: dict[str, str],
    live_apps: list[dict[str, str]],
    fuzzy: bool = True,
) -> dict[str, str] | None:
    """Find the live destination that supersedes an app's source/writeup row."""
    project_key = key(project["name"])
    for app in live_apps:
        app_keys = (key(app["name"]), key(app["slug"]))
        if any(
            app_key == project_key
            or (fuzzy and (app_key in project_key or project_key in app_key))
            for app_key in app_keys if app_key
        ):
            return app
    return None


def load_projects() -> list[dict[str, str]]:
    editorial = load_editorial()
    projects = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if not isinstance(projects, list):
        raise ValueError("public-projects.json must contain a JSON array")

    projects.extend(editorial["additional"])

    # Merge duplicate names from the reviewed manifest and editorial rows.
    # Later entries win, which lets an editorial destination replace a raw
    # repository row without duplicating the same project in the list.
    merged: dict[str, dict[str, str]] = {}
    for project in projects:
        if not isinstance(project, dict):
            raise ValueError(f"project must be an object: {project!r}")
        project = dict(project)
        project["language"] = str(project.get("language", "")).strip()
        merged[key(project["name"])] = project
    projects = list(merged.values())

    seen: set[str] = set()
    seen_urls: set[str] = set()
    visible: list[dict[str, str]] = []
    for project in projects:
        for field in ("name", "url", "description"):
            if not isinstance(project.get(field), str) or not project[field].strip():
                raise ValueError(f"project is missing {field}: {project!r}")
        project["priority"] = "P2"
        p3_tokens = editorial["P3"] + editorial["forks"]
        if any(project_matches(project, token) for token in p3_tokens):
            project["priority"] = "P3"
        else:
            for tier in TIER_ORDER:
                if any(project_matches(project, token) for token in editorial[tier]):
                    project["priority"] = tier
                    break
        name_key = key(project["name"])
        if name_key in seen:
            raise ValueError(f"duplicate catalog project: {project['name']}")
        seen.add(name_key)
        if not valid_url(project["url"]):
            raise ValueError(f"project URL must be https://, http://, or root-relative: {project['url']}")
        if project["url"] in seen_urls:
            raise ValueError(f"duplicate catalog destination: {project['url']}")
        seen_urls.add(project["url"])
        project["rank"] = editorial_rank(project, editorial)
        visible.append(project)

    return sorted(visible, key=lambda item: (item["rank"], item["name"].casefold()))


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
        projects.append({
            "name": name,
            "url": url,
            "description": description,
            "selection_rank": len(projects),
        })
    if not projects:
        raise ValueError("selected.txt must contain at least one project")
    return projects


def render_row(project: dict[str, str], show_description: bool = True) -> str:
    url = html.escape(project["url"], quote=True)
    name = html.escape(project["name"])
    attrs = ' target="_blank" rel="noopener"' if external(project["url"]) else ""
    description = (
        f'<span class="project-description">{html.escape(project["description"])}</span>'
        if show_description else ""
    )
    return (
        '<li class="project">'
        f'<a class="project-name" href="{url}"{attrs}>{name}</a>'
        f'{description}'
        "</li>"
    )


def selected_projects(
    projects: list[dict[str, str]],
    selected: list[dict[str, str]],
    live_apps: list[dict[str, str]],
) -> list[dict[str, str]]:
    """Put the P1 projects beside the existing homepage selection."""
    merged = {}
    for project in selected:
        app = (
            live_app_for(project, live_apps, fuzzy=False)
            if not project["url"].startswith("/projects/") else None
        )
        if app:
            merged[key(app["name"])] = {
                **app,
                "selection_rank": project["selection_rank"],
            }
        else:
            merged[key(project["name"])] = project
    for project in projects:
        if project["priority"] == "P1":
            merged.setdefault(key(project["name"]), project)
    return sorted(
        merged.values(),
        key=lambda item: (item.get("selection_rank", -1), item.get("rank", 100000)),
    )


def render(
    projects: list[dict[str, str]],
    selected: list[dict[str, str]],
    live_apps: list[dict[str, str]],
) -> str:
    live_rows = "\n".join(render_row(app, show_description=True) for app in live_apps)
    selected_rows = "\n".join(
        render_row(project, show_description=not project.get("is_live_app", False))
        for project in selected
    )
    selected_keys = {key(project["name"]) for project in selected}
    other_projects = [
        project for project in projects
        if project["priority"] != "P1"
        and not live_app_for(project, live_apps)
        and key(project["name"]) not in selected_keys
    ]
    other_rows = "\n".join(render_row(project) for project in other_projects)
    selected_items = [
        {
            "@type": "ListItem",
            "position": position,
            "item": dict(
                {
                    "@type": "CreativeWork",
                    "name": project["name"],
                    "url": absolute_url(project["url"]),
                },
                **({"description": project["description"]}
                   if not project.get("is_live_app", False) else {}),
            ),
        }
        for position, project in enumerate(selected, 1)
    ]
    structured_data = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": "Projects",
            "url": f"{SITE}/projects/",
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
<title>Projects | Eric Spencer</title>
<meta name="description" content="{PAGE_DESCRIPTION}">
<meta name="author" content="Eric Spencer">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
<link rel="canonical" href="https://ericspencer.us/projects/">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta name="theme-color" content="#faf7f2">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline' 'wasm-unsafe-eval' https://esm.run; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https://api.github.com https://huggingface.co; object-src 'self'; base-uri 'self'; form-action 'self'">
<meta property="og:type" content="website">
<meta property="og:title" content="Projects | Eric Spencer">
<meta property="og:description" content="{PAGE_DESCRIPTION}">
<meta property="og:url" content="https://ericspencer.us/projects/">
<meta property="og:image" content="https://ericspencer.us/assets/og/projects.jpg">
<meta property="og:image:type" content="image/jpeg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Projects | Eric Spencer">
<meta property="og:site_name" content="Eric Spencer">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Projects | Eric Spencer">
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
<link rel="stylesheet" href="/assets/css/portfolio.css?v=20260915">
</head>
<body class="portfolio-page">
<div class="wrap">
<p class="name">Eric Spencer</p>
<nav aria-label="Primary"><a href="/">index</a> · <a href="/research/">publications</a> · <a href="/projects/" aria-current="page">projects</a> · <a href="/cv/">cv</a></nav>
<hr>
<main>
<h1>Projects</h1>
<p class="intro">Software, research, experiments, coursework, and live apps.</p>
<section aria-labelledby="selected-work">
<h2 id="selected-work">Selected work</h2>
<ol class="project-list selected-list">{selected_rows}</ol>
</section>
<section aria-labelledby="projects-p15">
<h2 id="projects-p15">{TIER_LABELS["P1.5"][0]}</h2>
{f'<p class="section-intro">{TIER_LABELS["P1.5"][1]}</p>' if TIER_LABELS["P1.5"][1] else ''}
<ol class="project-list">{live_rows}</ol>
</section>
<section aria-labelledby="projects-p2">
<h2 id="projects-p2">{TIER_LABELS["P2"][0]}</h2>
{f'<p class="section-intro">{TIER_LABELS["P2"][1]}</p>' if TIER_LABELS["P2"][1] else ''}
<ol class="project-list">{other_rows}</ol>
</section>
</main>
<footer>© 2026 Eric Spencer · Chicago, IL · <a href="mailto:eric@ericspencer.us">eric@ericspencer.us</a></footer>
</div>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail when projects/ is stale")
    args = parser.parse_args()
    projects = load_projects()
    live_apps = load_live_apps()
    selected = selected_projects(projects, load_selected(), live_apps)
    output = render(projects, selected, live_apps)
    if args.check:
        if not OUTPUT.exists():
            print("projects/ is stale; run python3 scripts/build_projects.py", file=sys.stderr)
            return 1
        # apply_og_tags.py and seo_tags.py intentionally enrich the generated
        # head later in the release pipeline. Check the manifest-owned body
        # instead of requiring the whole document to remain byte-identical.
        current = OUTPUT.read_text(encoding="utf-8")
        forbidden = (
            'Projects A–Z', 'source repository is never disclosed',
            'catalog-tools',
            'project-filter', 'project-count',
        )
        expected_body = re.search(r"<main>(.*?)</main>", output, re.S)
        actual_body = re.search(r"<main>(.*?)</main>", current, re.S)
        expected = re.sub(r"\s+", " ", expected_body.group(1) if expected_body else "")
        actual = re.sub(r"\s+", " ", actual_body.group(1) if actual_body else "")
        if (not expected_body or not actual_body or expected != actual
                or any(text in current for text in forbidden)):
            print("projects/ is stale; run python3 scripts/build_projects.py", file=sys.stderr)
            return 1
        print("projects/ is current")
        return 0
    OUTPUT.write_text(output, encoding="utf-8")
    counts = {tier: sum(project["priority"] == tier for project in projects) for tier in TIER_ORDER}
    print(f"Built {counts} visible projects -> projects/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
