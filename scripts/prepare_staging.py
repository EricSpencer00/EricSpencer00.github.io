#!/usr/bin/env python3
"""Remove analytics and enforce crawler rules on the completed staging build."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# These directories are removed by deploy.yml before the Pages upload.
EXCLUDED = {".git", "ai4fm", "backup-site", "editor", "tests"}
SCRIPT = re.compile(r"<script\b[^>]*>.*?</script\s*>", re.I | re.S)
ANALYTICS = re.compile(
    r"G-30FQRTZWJ8|googletagmanager\.com/(?:gtag/js|gtm\.js)|"
    r"google-analytics\.com/(?:analytics|ga)\.js|\bgtag\s*\(|GoogleAnalyticsObject",
    re.I,
)
ROBOTS = re.compile(r"<meta\b(?=[^>]*\bname\s*=\s*['\"]robots['\"])[^>]*>", re.I)
NOINDEX = '<meta name="robots" content="noindex, follow">'


def files(root):
    for path in sorted(root.rglob("*")):
        if path.is_file() and not any(p in EXCLUDED for p in path.relative_to(root).parts):
            if path.suffix.lower() in {".html", ".js", ".json"}:
                yield path


def transform(text):
    text = SCRIPT.sub(lambda m: "" if ANALYTICS.search(m[0]) else m[0], text)
    if re.search(r"</head\s*>", text, re.I):
        robots = ROBOTS.search(text)
        if robots:
            text = ROBOTS.sub(lambda m: NOINDEX if m.start() == robots.start() else "", text)
        else:
            text = re.sub(r"</head\s*>", NOINDEX + "\n</head>", text, count=1, flags=re.I)
    return text


def prepare(root):
    for path in files(root):
        if path.suffix.lower() == ".html":
            original = path.read_text(encoding="utf-8")
            text = transform(original)
            if text != original:
                path.write_text(text, encoding="utf-8")
    (root / "CNAME").write_text("dev.ericspencer.us\n", encoding="utf-8")
    # Crawlers must be able to fetch the page-level noindex directive.
    (root / "robots.txt").write_text("User-agent: *\nAllow: /\n", encoding="utf-8")
    (root / "sitemap.xml").unlink(missing_ok=True)


def check(root):
    problems = []
    for path in files(root):
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(root)
        if ANALYTICS.search(text):
            problems.append(f"{rel}: analytics remain in the staging artifact")
        if path.suffix.lower() == ".html" and re.search(r"</head\s*>", text, re.I):
            if NOINDEX not in text:
                problems.append(f"{rel}: staging noindex directive is missing")
    for name, expected in (("CNAME", "dev.ericspencer.us\n"),
                           ("robots.txt", "User-agent: *\nAllow: /\n")):
        if not (root / name).exists() or (root / name).read_text() != expected:
            problems.append(f"{name}: unexpected staging host/crawler rules")
    if (root / "sitemap.xml").exists():
        problems.append("sitemap.xml: staging must not advertise a production sitemap")
    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        prepare(ROOT)
    problems = check(ROOT)
    print("\n".join(problems) if problems else "staging check passed: no analytics; noindex and host rules intact")
    return bool(problems)


if __name__ == "__main__":
    raise SystemExit(main())
