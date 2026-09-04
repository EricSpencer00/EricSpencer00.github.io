#!/usr/bin/env python3
"""Export every canonical project writeup into editor/index.md.

This is intentionally a one-way bootstrap tool.  After the export, edit
editor/index.md directly; it is a review queue, not a deployment generator.
"""

from __future__ import annotations

import html
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "content" / "project-pages.txt"
OUT = ROOT / "editor" / "index.md"


class Markdown(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.href: list[str] = []
        self.in_pre = False
        self.in_code = False

    def line(self, prefix: str = "") -> None:
        if self.parts and not self.parts[-1].endswith("\n\n"):
            self.parts.append("\n\n")
        if prefix:
            self.parts.append(prefix)

    def handle_starttag(self, tag: str, attrs) -> None:
        attrs = dict(attrs)
        if tag in {"h1", "h2", "h3"}:
            self.line({"h1": "# ", "h2": "## ", "h3": "### "}[tag])
        elif tag == "p":
            self.line()
        elif tag == "li":
            self.line("- ")
        elif tag == "blockquote":
            self.line("> ")
        elif tag == "br":
            self.parts.append("\n")
        elif tag == "a":
            self.href.append(attrs.get("href", ""))
            self.parts.append("[")
        elif tag == "pre":
            self.line("```\n")
            self.in_pre = True
        elif tag == "code" and not self.in_pre:
            self.parts.append("`")
            self.in_code = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self.href:
            self.parts.append(f"]({self.href.pop()})")
        elif tag == "pre":
            if self.parts and not self.parts[-1].endswith("\n"):
                self.parts.append("\n")
            self.parts.append("```\n\n")
            self.in_pre = False
        elif tag == "code" and self.in_code:
            self.parts.append("`")
            self.in_code = False

    def handle_data(self, data: str) -> None:
        self.parts.append(html.unescape(data))

    def text(self) -> str:
        value = "".join(self.parts)
        value = re.sub(r"[ \t]+\n", "\n", value)
        value = re.sub(r"\n{3,}", "\n\n", value)
        return value.strip()


def records():
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        canonical, _, note = (line.split("|") + ["", ""])[:3]
        if note == "external" or canonical == "/projects.html":
            continue
        yield canonical, ROOT / canonical.lstrip("/")


def meta(source: str, name: str) -> str:
    match = re.search(
        rf'<meta[^>]+(?:name|property)="{re.escape(name)}"[^>]+content="([^"]*)"',
        source,
        re.I,
    )
    return html.unescape(match.group(1)).strip() if match else ""


def extract(path: Path) -> tuple[str, str, str]:
    source = path.read_text(encoding="utf-8", errors="replace")
    title_match = re.search(r"<title>(.*?)</title>", source, re.I | re.S)
    title = html.unescape(re.sub(r"\s+", " ", title_match.group(1))).replace(" | Eric Spencer", "").strip()
    description = meta(source, "description")
    body = source.split('<hr class="dash">', 1)[-1].split("<footer", 1)[0]
    parser = Markdown()
    parser.feed(body)
    return title, description, parser.text()


def main() -> None:
    pages = list(records())
    out = [
        "# Project copy review",
        "",
        f"{len(pages)} canonical project pages. Edit the text beneath each `### Copy` heading.",
        "",
        "The review desk at `editor/index.html` reads this file, keeps browser-local drafts, and can download the revised Markdown.",
        "",
    ]
    for canonical, path in pages:
        slug = path.stem
        title, description, body = extract(path)
        out.extend([
            f"<!-- PROJECT {slug} START -->",
            f"## {title}",
            "",
            f"- URL: {canonical}",
            f"- Description: {description}",
            "- Review: needs-review",
            "",
            "### Copy",
            "",
            body,
            "",
            f"<!-- PROJECT {slug} END -->",
            "",
        ])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(out), encoding="utf-8")
    print(f"Exported {len(pages)} project writeups to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
