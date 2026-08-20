#!/usr/bin/env python3
"""Build blog/*.html and blog/index.html from content/blog/*.md."""

from __future__ import annotations

import html
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "content" / "blog"
OUTPUT = ROOT / "blog"


@dataclass(frozen=True)
class Post:
    slug: str
    title: str
    date: str
    description: str
    body: str


def parse_front_matter(path: Path) -> Post | None:
    raw = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n(.*)\Z", raw, re.DOTALL)
    if not match:
        raise ValueError(f"{path}: expected YAML front matter between --- lines")

    fields = {}
    for line in match.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, separator, value = line.partition(":")
        if not separator:
            raise ValueError(f"{path}: invalid front matter line: {line}")
        fields[key.strip()] = value.strip().strip("\"'")

    if fields.get("published", "true").lower() in {"false", "no", "draft"}:
        return None
    for field in ("title", "date", "description"):
        if not fields.get(field):
            raise ValueError(f"{path}: missing front matter field '{field}'")

    slug = fields.get("slug", path.stem)
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise ValueError(f"{path}: slug must contain lowercase letters, numbers, and hyphens")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", fields["date"]):
        raise ValueError(f"{path}: date must use YYYY-MM-DD")

    return Post(slug, fields["title"], fields["date"], fields["description"], match.group(2).strip())


def load_posts() -> list[Post]:
    if not SOURCE.exists():
        return []
    posts = [post for path in sorted(SOURCE.glob("*.md")) if (post := parse_front_matter(path))]
    return sorted(posts, key=lambda post: post.date, reverse=True)


def inline_markdown(value: str) -> str:
    escaped = html.escape(value, quote=False)
    placeholders: list[str] = []

    def protect(fragment: str) -> str:
        placeholders.append(fragment)
        return f"\x00{len(placeholders) - 1}\x00"

    escaped = re.sub(
        r"!\[([^\]]*)\]\(([^)\s]+)(?:\s+['\"]([^'\"]*)['\"])?\)",
        lambda match: protect(
            f'<img src="{html.escape(match.group(2), quote=True)}" '
            f'alt="{html.escape(match.group(1), quote=True)}">'
        ),
        escaped,
    )
    escaped = re.sub(
        r"\[([^\]]+)\]\(([^)\s]+)\)",
        lambda match: protect(
            f'<a href="{html.escape(match.group(2), quote=True)}">{match.group(1)}</a>'
        ),
        escaped,
    )
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*(.+?)\*\*|__(.+?)__", lambda match: f"<strong>{match.group(1) or match.group(2)}</strong>", escaped)
    escaped = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)|(?<!_)_([^_]+)_(?!_)", lambda match: f"<em>{match.group(1) or match.group(2)}</em>", escaped)
    escaped = re.sub(
        r"(?<![\w\"=])(https?://[^\s<]+)",
        lambda match: protect(f'<a href="{match.group(1)}" target="_blank" rel="noopener">{match.group(1)}</a>'),
        escaped,
    )
    for index, fragment in enumerate(placeholders):
        escaped = escaped.replace(f"\x00{index}\x00", fragment)
    return escaped


def markdown_to_html(markdown: str) -> str:
    output: list[str] = []
    paragraph: list[str] = []
    list_type: str | None = None
    in_code = False
    code_lines: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            output.append(f"<p>{inline_markdown(' '.join(paragraph))}</p>")
            paragraph.clear()

    def close_list() -> None:
        nonlocal list_type
        if list_type:
            output.append(f"</{list_type}>")
            list_type = None

    for line in markdown.splitlines():
        if line.startswith("```"):
            if in_code:
                output.append(f"<pre><code>{html.escape(chr(10).join(code_lines))}</code></pre>")
                code_lines.clear()
            else:
                flush_paragraph()
                close_list()
            in_code = not in_code
            continue
        if in_code:
            code_lines.append(line)
            continue

        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            close_list()
            continue
        heading = re.match(r"^(#{1,3})\s+(.+)$", stripped)
        if heading:
            flush_paragraph()
            close_list()
            level = len(heading.group(1)) + 1
            output.append(f"<h{level}>{inline_markdown(heading.group(2))}</h{level}>")
            continue
        if re.fullmatch(r"[-*_]{3,}", stripped):
            flush_paragraph()
            close_list()
            output.append("<hr>")
            continue
        quote = re.match(r"^>\s?(.*)$", stripped)
        if quote:
            flush_paragraph()
            close_list()
            output.append(f"<blockquote>{inline_markdown(quote.group(1))}</blockquote>")
            continue
        item = re.match(r"^([-*+] |\d+\. )(.+)$", stripped)
        if item:
            flush_paragraph()
            requested_type = "ol" if item.group(1)[0].isdigit() else "ul"
            if list_type != requested_type:
                close_list()
                output.append(f"<{requested_type}>")
                list_type = requested_type
            output.append(f"<li>{inline_markdown(item.group(2))}</li>")
            continue
        close_list()
        paragraph.append(stripped)

    if in_code:
        raise ValueError("unterminated fenced code block")
    flush_paragraph()
    close_list()
    return "\n".join(output)


def render_post(post: Post) -> str:
    template = (OUTPUT / "_template.html").read_text(encoding="utf-8")
    replacements = {
        "POST TITLE": html.escape(post.title),
        "POST DESCRIPTION": html.escape(post.description, quote=True),
        "YOUR-SLUG": post.slug,
        "YYYY-MM-DD": post.date,
        "<!-- Write your post content here -->\n<p>...</p>": markdown_to_html(post.body),
    }
    for old, new in replacements.items():
        template = template.replace(old, new)
    return template


def render_index(posts: list[Post]) -> str:
    path = OUTPUT / "index.html"
    index = path.read_text(encoding="utf-8")
    rows = "\n".join(
        f'<div class="post-row"><span class="post-d">{post.date}</span>'
        f'<div class="post-body"><div class="post-title"><a href="/blog/{post.slug}.html">'
        f"{html.escape(post.title)}</a></div><p class=\"post-desc\">"
        f"{html.escape(post.description)}</p></div></div>"
        for post in posts
    ) or '<p style="color:var(--dim);font-size:14px;font-style:italic">No posts yet.</p>'
    start = "<!-- POSTS_START -->"
    end = "<!-- POSTS_END -->"
    if start not in index or end not in index:
        raise ValueError("blog/index.html: missing POSTS_START/POSTS_END markers")
    before, remainder = index.split(start, 1)
    _, after = remainder.split(end, 1)
    return f"{before}{start}\n{rows}\n\n{end}{after}"


def prune_orphans(posts: list[Post]) -> list[str]:
    """Delete post pages whose source is gone or has gone back to draft.

    Flipping a post to `published: false` used to leave its HTML behind, so an
    unpublished draft stayed reachable by direct link and stayed in the sitemap.
    """
    keep = {f"{post.slug}.html" for post in posts} | {"index.html", "_template.html"}
    removed = []
    for path in sorted(OUTPUT.glob("*.html")):
        if path.name not in keep:
            path.unlink()
            removed.append(path.name)
    return removed


def main() -> None:
    posts = load_posts()
    OUTPUT.mkdir(exist_ok=True)
    for post in posts:
        (OUTPUT / f"{post.slug}.html").write_text(render_post(post), encoding="utf-8")
    (OUTPUT / "index.html").write_text(render_index(posts), encoding="utf-8")
    removed = prune_orphans(posts)
    print(f"Built {len(posts)} blog post(s)"
          + (f"; removed {', '.join(removed)}" if removed else ""))


if __name__ == "__main__":
    main()