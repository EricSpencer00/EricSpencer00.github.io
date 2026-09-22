#!/usr/bin/env python3
"""
build_resume_pages.py — reads content/resumes.txt, writes a landing page per
resume/CV variant (e.g. /cv/index.html, /resume/80626/index.html), plus a
/resume/ index that forwards to the most recent dated variant.

The PDFs themselves live in /assets/pdf/ and are pushed here by CI in
github.com/EricSpencer00/resume. The public CV also has readable HTML drawn
from content/cv.json, experience.txt, and publications.json.
"""

from pathlib import Path
import html as htmllib
import json

ROOT = Path(__file__).parent.parent
CONTENT = ROOT / "content"

PAGE = """<!doctype html><html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} — Eric Spencer</title>
<meta name="description" content="{blurb}">
<meta name="robots" content="{robots}">
{canonical}<meta property="og:type" content="profile">
<meta property="og:title" content="{title} — Eric Spencer">
<meta property="og:description" content="{blurb}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap">
<style>
:root{{--paper:#faf7f2;--ink:#080401;--accent:#5f000b;--dim:#6d6863;--rule:#d6d4d1}}
/* A custom property holds any value, so a hex fallback in the same block is
   overwritten, not skipped. @supports is what keeps oklch off browsers that
   cannot read it: Chrome <=110, Safari <=15.3, Firefox <=112. */
@supports (color:oklch(0 0 0)){{:root{{--paper:oklch(0.978 0.006 80);--ink:oklch(0.11 0.015 60);--accent:oklch(0.30 0.13 22);--dim:oklch(0.52 0.01 70);--rule:oklch(0.87 0.005 80)}}}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--paper);color:var(--ink);font-family:"Plus Jakarta Sans",-apple-system,BlinkMacSystemFont,sans-serif;font-size:16px;line-height:1.7;-webkit-font-smoothing:antialiased}}
.wrap{{max-width:960px;margin:0 auto;padding:48px 24px 72px}}
h1{{font-size:clamp(28px,4vw,40px);font-weight:700;letter-spacing:-0.025em;line-height:1.1;margin:0 0 6px}}
p.sub{{color:var(--dim);margin:0 0 22px}}
nav.top{{font-size:14px;font-weight:500;color:var(--dim);margin:0 0 24px}}
nav.top a{{color:inherit;text-decoration:none}}
nav.top a:hover{{color:var(--ink)}}
nav.top a.active{{color:var(--ink);font-weight:600}}
a{{color:var(--accent);text-decoration:none}}
a:hover{{text-decoration:underline;text-underline-offset:3px}}
.actions{{display:flex;gap:14px;flex-wrap:wrap;font-family:"IBM Plex Mono",monospace;font-size:13px;margin:0 0 26px}}
.actions a{{border:1px solid var(--rule);border-radius:6px;padding:7px 13px;color:var(--ink)}}
.actions a:hover{{border-color:var(--ink);text-decoration:none}}
.doc{{width:100%;height:min(85vh,1100px);border:1px solid var(--rule);border-radius:8px;background:#fff}}
.cv-summary{{max-width:72ch;margin:30px 0 42px}}
.cv-summary h2,.pdf-title{{font-size:1.4rem;line-height:1.3;letter-spacing:-.02em;margin:34px 0 16px}}
.cv-summary h3{{font-size:1rem;line-height:1.5;margin:0 0 4px}}
.cv-summary p{{margin:6px 0 14px}}
.cv-date{{color:var(--dim);font-size:.875rem}}
.cv-entry{{padding:16px 0;border-top:1px solid var(--rule)}}
.cv-publications{{padding-left:1.35rem}}
.cv-publications li{{padding:7px 0}}
.cv-summary a{{overflow-wrap:anywhere}}
footer{{margin-top:28px;border-top:1px solid var(--rule);padding-top:14px;font-family:"IBM Plex Mono",monospace;font-size:12px;color:var(--dim)}}
@media (max-width:640px){{.doc{{height:70vh}}}}
</style></head><body>
<div class="wrap">
<nav class="top"><a href="/">index</a></nav>
<main>
<h1>{title}</h1>
<p class="sub">{blurb}</p>
<div class="actions">
  <a href="/assets/pdf/{pdf}" download>Download PDF</a>
  <a href="/assets/pdf/{pdf}" target="_blank" rel="noopener">Open in new tab</a>
  <a href="https://github.com/EricSpencer00/resume">LaTeX source</a>
</div>
{summary}
<object class="doc" data="/assets/pdf/{pdf}" type="application/pdf">
  <p>Your browser will not display the PDF inline.
  <a href="/assets/pdf/{pdf}">Download it instead</a>.</p>
</object>
</main>
<footer>Built from LaTeX in <a href="https://github.com/EricSpencer00/resume">EricSpencer00/resume</a>.</footer>
</div>
</body></html>
"""


REDIRECT = """<!doctype html><html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Resume — Eric Spencer</title>
<meta name="robots" content="noindex, nofollow">
<meta http-equiv="refresh" content="0;url=/{target}/">
</head><body>
<p><a href="/{target}/">Resume &rarr;</a></p>
<script>location.replace("/{target}/");</script>
</body></html>
"""


def recency(slug):
    """Sort key for a dated variant slug: resume/MDDYY, optionally -N.

    Variants are named by date written, M+DD+YY (Aug 6 2026 = 80626), with a
    counter appended for a second one the same day. Stripping the trailing DDYY
    leaves the month, so this stays correct for two-digit months (121526).
    """
    code, _, counter = slug.split("/", 1)[1].partition("-")
    if not code.isdigit():
        return (0, 0, 0, 0)
    n = int(code)
    return (n % 100, n // 10000, (n // 100) % 100, int(counter) if counter.isdigit() else 1)


def rows():
    path = CONTENT / "resumes.txt"
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            parts = line.split("|")
            parts += [""] * (5 - len(parts))
            yield parts[:5]


def cv_summary():
    """Render the public summary without requiring a PDF viewer or JavaScript."""
    data = json.loads((CONTENT / "cv.json").read_text(encoding="utf-8"))
    publications = json.loads((CONTENT / "publications.json").read_text(encoding="utf-8"))
    escape = htmllib.escape
    notes = {(entry["role"], entry["organization"]): entry["summary"]
             for entry in data["experience_notes"]}
    used_notes = set()
    experience = []
    for raw_line in (CONTENT / "experience.txt").read_text(encoding="utf-8").splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        fields = raw_line.split("|")
        if len(fields) < 5:
            raise ValueError("experience.txt rows need role, organization, URL, start, and end")
        role, organization, url, start, end = fields[:5]
        note_key = (role, organization)
        summary = notes.get(note_key, "")
        if summary:
            used_notes.add(note_key)
        experience.append(
            '<article class="cv-entry">'
            f'<h3>{escape(role)} · <a href="{escape(url, quote=True)}">{escape(organization)}</a></h3>'
            f'<p class="cv-date">{escape(start)} – {escape(end)}</p>'
            + (f'<p>{escape(summary)}</p>' if summary else "")
            + '</article>'
        )
    if unused := set(notes) - used_notes:
        raise ValueError(f"CV experience notes have no matching current experience entry: {sorted(unused)}")
    education = []
    for entry in data["education"]:
        education.append(
            '<article class="cv-entry">'
            f'<h3><a href="{escape(entry["url"], quote=True)}">{escape(entry["institution"])}</a></h3>'
            f'<p>{escape(entry["qualification"])}</p>'
            f'<p class="cv-date">Completed {escape(entry["completed"])}</p>'
            f'<p>{escape(entry["details"])}</p></article>'
        )
    papers = []
    for paper in publications:
        papers.append(
            f'<li><a href="{escape(paper["url"], quote=True)}">{escape(paper["title"])}</a>'
            f'<br><span class="cv-date">{escape(str(paper["year"]))} · {escape(paper["venue"])}</span></li>'
        )
    return (
        '<div class="cv-summary">'
        f'<p>{escape(data["intro"])}</p>'
        '<section aria-labelledby="cv-education"><h2 id="cv-education">Education</h2>'
        + "".join(education) + '</section>'
        '<section aria-labelledby="cv-experience"><h2 id="cv-experience">Experience</h2>'
        + "".join(experience) + '</section>'
        '<section aria-labelledby="cv-publications"><h2 id="cv-publications">Publications</h2>'
        '<ol class="cv-publications">' + "".join(papers) + '</ol>'
        '<p><a href="/research/">More research, models, and presentations</a></p></section>'
        '<p><a href="/projects/resilient/">Resilient compiler</a> · '
        '<a href="/projects/tla-plus/">TLA+ models and tools</a> · '
        '<a href="/projects/">All projects</a></p>'
        '</div><h2 class="pdf-title">Full CV</h2>'
        '<p>The PDF includes the full list of roles, projects, and technical skills.</p>'
    )


def main():
    built = []
    for slug, pdf, title, blurb, index in rows():
        indexable = index.strip().lower() in ("yes", "true", "1")
        out = ROOT / slug / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            PAGE.format(
                title=htmllib.escape(title),
                blurb=htmllib.escape(blurb),
                pdf=htmllib.escape(pdf),
                robots="index, follow" if indexable else "noindex, nofollow",
                canonical=(
                    f'<link rel="canonical" href="https://ericspencer.us/{slug}/">\n'
                    if indexable else ""
                ),
                summary=cv_summary() if slug == "cv" else "",
            ),
            encoding="utf-8",
        )
        built.append(f"/{slug}/")

    # Bare /resume/ forwards to the newest dated variant, so the path stays
    # valid as variants are added and never has to be hand-edited. noindex,
    # matching the tuned variants it points at.
    variants = [s for s in built if s.startswith("/resume/")]
    if variants:
        latest = max((s.strip("/") for s in variants), key=recency)
        out = ROOT / "resume" / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(REDIRECT.format(target=latest), encoding="utf-8")
        built.append(f"/resume/ -> /{latest}/")

    print("Built resume pages:", ", ".join(built))


if __name__ == "__main__":
    main()
