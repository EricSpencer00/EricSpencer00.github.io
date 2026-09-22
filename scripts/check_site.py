#!/usr/bin/env python3
"""Validate the public route and SEO contract before a deploy.

The site is intentionally static, so a small structural audit catches the
mistakes that are otherwise easy to miss in generated HTML: an extensionful
canonical, a link to an old page path, duplicate indexable canonicals, broken
local canonical routes, invalid JSON-LD, or a sitemap that advertises a legacy
URL.
"""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlsplit

from build_project_routes import is_live_project_source
from build_blog import load_posts

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://ericspencer.us"
SKIP_DIRS = {".git", "ai4fm", "backup-site", "editor", "tests"}
SKIP_FILES = {
    ROOT / "404.html",  # GitHub Pages' fallback document keeps its file URL.
    ROOT / "blog" / "_template.html",
}
EXTENSIONFUL = re.compile(r"\.(?:html?|js)(?:[?#]|$)", re.IGNORECASE)
# These public documents belong to a separately deployed GitHub project site.
# Its canonical URLs really end in .html; this repository cannot rename them.
EXTERNAL_HTML_ROUTES = {"/DailyTask-web/privacy.html", "/DailyTask-web/terms.html"}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title: list[str] = []
        self.description: list[str] = []
        self.og_title: list[str] = []
        self.og_description: list[str] = []
        self.og_url: list[str] = []
        self.twitter_card: list[str] = []
        self.canonicals: list[str] = []
        self.robots: list[str] = []
        self.hrefs: list[str] = []
        self.policies: list[str] = []
        self.script_sources: list[str] = []
        self.h1_count = 0
        self.json_ld: list[str] = []
        self._in_title = False
        self._in_json_ld = False
        self._json_buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value or "" for key, value in attrs}
        tag = tag.lower()
        if tag == "title":
            self._in_title = True
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "meta":
            if values.get("http-equiv", "").lower() == "content-security-policy":
                self.policies.append(values.get("content", ""))
            name = values.get("name", "").lower()
            prop = values.get("property", "").lower()
            if name == "description":
                self.description.append(values.get("content", ""))
            elif name == "robots":
                self.robots.append(values.get("content", ""))
            elif name == "twitter:card":
                self.twitter_card.append(values.get("content", ""))
            if prop == "og:title":
                self.og_title.append(values.get("content", ""))
            elif prop == "og:description":
                self.og_description.append(values.get("content", ""))
            elif prop == "og:url":
                self.og_url.append(values.get("content", ""))
                self.canonicals.append(values.get("content", ""))
        elif tag == "link" and values.get("rel", "").lower() == "canonical":
            self.canonicals.append(values.get("href", ""))
        elif tag == "a":
            self.hrefs.append(values.get("href", ""))
        elif tag == "script":
            if values.get("src"):
                self.script_sources.append(values["src"])
            if values.get("type", "").lower() == "application/ld+json":
                self._in_json_ld = True
                self._json_buffer = []

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "title":
            self._in_title = False
        elif tag == "script" and self._in_json_ld:
            self.json_ld.append("".join(self._json_buffer))
            self._in_json_ld = False
            self._json_buffer = []

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title.append(data)
        if self._in_json_ld:
            self._json_buffer.append(data)


def page_files() -> list[Path]:
    has_published_blog = bool(load_posts())
    return [
        path
        for path in sorted(ROOT.rglob("*.html"))
        if not any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts)
        and path not in SKIP_FILES
        and path.name != "googleecd5c6e317b1ab67.html"
        and (has_published_blog or path != ROOT / "blog" / "index.html")
    ]


def route_for(path: Path) -> str | None:
    relative = path.relative_to(ROOT)
    if relative == Path("index.html"):
        return "/"
    if relative.name == "index.html":
        return "/" + str(relative.parent).replace("\\", "/") + "/"
    return None


def local_route_exists(route: str) -> bool:
    if route == "/":
        return (ROOT / "index.html").is_file()
    path = ROOT / route.strip("/")
    return (path / "index.html").is_file() if path.is_dir() else path.is_file()


def is_noindex(parser: PageParser) -> bool:
    return any("noindex" in value.lower() for value in parser.robots)


def policy_allows(policy: str, directive: str, url: str) -> bool:
    """Check the URL source expressions used by this static site's policies.

    A nonce/hash-only policy fails closed here: this site doesn't emit either.
    Checking actual origins catches an analytics tag that is present but cannot
    load, which a metadata-only audit misses.
    """
    directives = {}
    for item in policy.split(";"):
        tokens = item.split()
        if tokens:
            directives.setdefault(tokens[0], tokens[1:])
    fallback = "script-src" if directive == "script-src-elem" else "default-src"
    sources = directives.get(directive, directives.get(fallback, directives.get("default-src")))
    if sources is None:
        return True
    target = urlsplit(url)
    for source in sources:
        if source == "*" or source == target.scheme + ":":
            return True
        if source == "'self'" and target.netloc == urlsplit(SITE).netloc:
            return True
        allowed = urlsplit(source)
        if allowed.scheme != target.scheme or not allowed.hostname:
            continue
        host = allowed.hostname
        matches = target.hostname == host
        if host.startswith("*."):
            matches = bool(target.hostname and target.hostname.endswith(host[1:]))
        if matches and allowed.port == target.port:
            if not allowed.path or target.path.startswith(allowed.path):
                return True
    return False


def check_analytics(parser: PageParser) -> list[str]:
    tags = [src for src in parser.script_sources
            if urlsplit(src).hostname == "www.googletagmanager.com"]
    if not tags:
        return []
    problems = []
    for policy in parser.policies:
        if any(not policy_allows(policy, "script-src-elem", src) for src in tags):
            problems.append("CSP blocks the Google Analytics loader")
        for endpoint in ("https://www.google-analytics.com/g/collect",
                         "https://region1.google-analytics.com/g/collect"):
            if not policy_allows(policy, "connect-src", endpoint):
                problems.append(f"CSP blocks Analytics collection: {endpoint}")
    return problems


def check_discovery(pages: dict[str, PageParser]) -> list[str]:
    incoming = set()
    for source, parser in pages.items():
        for href in parser.hrefs:
            target = urldefrag(urljoin(source, href))[0]
            if target != source and target in pages:
                incoming.add(target)
    return [f"{url}: no incoming link from another indexable page"
            for url in sorted(pages) if url != SITE + "/" and url not in incoming]


def check_pages() -> tuple[list[str], dict[str, int]]:
    problems: list[str] = []
    indexable: dict[str, int] = {}
    public_pages: dict[str, PageParser] = {}
    for path in page_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        if "<html" not in text.lower():
            continue
        parser = PageParser()
        try:
            parser.feed(text)
        except Exception as exc:
            problems.append(f"{path.relative_to(ROOT)}: invalid HTML ({exc})")
            continue
        rel = str(path.relative_to(ROOT))
        problems.extend(f"{rel}: {problem}" for problem in check_analytics(parser))
        canonical = next((value for value in parser.canonicals if value), None)
        if not canonical:
            if is_noindex(parser):
                continue
            problems.append(f"{rel}: missing canonical")
        elif canonical.startswith(SITE):
            route = canonical[len(SITE):] or "/"
            if EXTENSIONFUL.search(route):
                problems.append(f"{rel}: extensionful canonical {canonical}")
            if not is_noindex(parser):
                # The live app source trees under projects/2026/ are copied to
                # their public root routes at build time. They intentionally
                # share the root route's canonical rather than competing with
                # it as a second indexable page.
                if not is_live_project_source(path):
                    indexable[canonical] = indexable.get(canonical, 0) + 1
                    public_pages[canonical] = parser
                if not local_route_exists(route):
                    problems.append(f"{rel}: canonical route does not exist {route}")
        for href in parser.hrefs:
            target = urlsplit(urljoin(SITE, href))
            if (target.netloc == urlsplit(SITE).netloc and EXTENSIONFUL.search(target.path)
                    and target.path not in EXTERNAL_HTML_ROUTES):
                problems.append(f"{rel}: extensionful internal link {href}")
        if not is_noindex(parser):
            if len(parser.title) != 1 or not "".join(parser.title).strip():
                problems.append(f"{rel}: missing or duplicate title")
            if len(parser.description) != 1 or not parser.description[0].strip():
                problems.append(f"{rel}: missing or duplicate meta description")
            for label, values in (
                ("og:title", parser.og_title),
                ("og:description", parser.og_description),
                ("og:url", parser.og_url),
                ("twitter:card", parser.twitter_card),
            ):
                if len(values) != 1 or not values[0].strip():
                    problems.append(f"{rel}: missing or duplicate {label}")
            if parser.h1_count != 1:
                problems.append(f"{rel}: expected one H1, found {parser.h1_count}")
            if not parser.json_ld:
                problems.append(f"{rel}: missing JSON-LD")
            for block in parser.json_ld:
                try:
                    json.loads(block)
                except json.JSONDecodeError as exc:
                    problems.append(f"{rel}: invalid JSON-LD ({exc.msg})")
    for canonical, count in sorted(indexable.items()):
        if count != 1:
            problems.append(f"duplicate indexable canonical ({count} copies): {canonical}")
    problems.extend(check_discovery(public_pages))
    return problems, indexable


def check_sitemap(indexable: dict[str, int]) -> list[str]:
    path = ROOT / "sitemap.xml"
    if not path.is_file():
        return []
    problems: list[str] = []
    try:
        root = ET.fromstring(path.read_text(encoding="utf-8"))
    except ET.ParseError as exc:
        return [f"sitemap.xml: invalid XML ({exc})"]
    urls = [node.text or "" for node in root.findall("{*}url/{*}loc")]
    if len(urls) != len(set(urls)):
        problems.append("sitemap.xml: duplicate URLs")
    for url in urls:
        if EXTENSIONFUL.search(url):
            problems.append(f"sitemap.xml: extensionful URL {url}")
        if url.startswith(SITE) and url not in indexable:
            problems.append(f"sitemap.xml: URL is not an indexable canonical {url}")
    return problems


def main() -> int:
    problems, indexable = check_pages()
    problems.extend(check_sitemap(indexable))
    if problems:
        print("\n".join(problems), file=sys.stderr)
        print(f"site check failed with {len(problems)} problem(s)", file=sys.stderr)
        return 1
    print(f"site check passed: {len(indexable)} indexable canonical pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
