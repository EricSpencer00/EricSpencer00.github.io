#!/usr/bin/env python3
"""Keep publication copy and structured data in sync with the CV's citations."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://ericspencer.us"
PAGE = f"{SITE}/research/"
PERSON = f"{SITE}/#eric"


def load_publications() -> list[dict]:
    return json.loads((ROOT / "content/publications.json").read_text(encoding="utf-8"))


def render_papers(papers: list[dict]) -> str:
    escape = html.escape
    parts = []
    for paper in papers:
        authors = ", ".join(escape(name) for name in paper["authors"])
        links = " · ".join(
            f'<a href="{escape(link["url"], quote=True)}">{escape(link["label"])}</a>'
            for link in paper["links"]
        )
        parts.append(
            f'<article class="publication" id="{escape(paper["id"], quote=True)}">\n'
            f'<h3>{escape(paper["title"])}</h3>\n'
            f'<p class="small">{authors}.</p>\n'
            f'<p class="small">{paper["year"]} · {escape(paper["venue"])} · '
            f'{escape(paper["role"])}. '
            f'<a href="https://doi.org/{escape(paper["doi"], quote=True)}">'
            f'DOI: {escape(paper["doi"])}</a></p>\n'
            f'<p>{escape(paper["summary"])}</p>\n'
            f'<p class="linkrow">{links}</p>\n'
            '</article>'
        )
    return "\n".join(parts)


def publication_schema(papers: list[dict]) -> dict:
    articles = []
    for paper in papers:
        articles.append({
            "@type": "ScholarlyArticle",
            "@id": f'{PAGE}#{paper["id"]}',
            "headline": paper["title"],
            "name": paper["title"],
            "url": f'{PAGE}#{paper["id"]}',
            "sameAs": [paper["url"], f'https://doi.org/{paper["doi"]}'],
            "identifier": {"@type": "PropertyValue", "propertyID": "DOI", "value": paper["doi"]},
            "author": [
                {"@type": "Person", "@id": PERSON, "name": name} if name == "Eric Spencer"
                else {"@type": "Person", "name": name}
                for name in paper["authors"]
            ],
            "datePublished": paper["publication_date"],
            "description": paper["summary"],
            "isPartOf": {"@type": "CreativeWork", "name": paper["venue"]},
            "inLanguage": "en",
        })
    return {"@context": "https://schema.org", "@graph": [
        {"@type": "Person", "@id": PERSON, "name": "Eric Spencer", "url": f"{SITE}/"},
        {
            "@type": "CollectionPage", "@id": f"{PAGE}#webpage", "url": PAGE,
            "name": "TLA+ & LLM Research Publications | Eric Spencer",
            "description": "Papers, models, datasets, and tools from Eric Spencer's research on formal methods and large language models.",
            "about": {"@id": PERSON}, "author": {"@id": PERSON},
            "mainEntity": {"@id": f"{PAGE}#publications"}, "inLanguage": "en",
        },
        {"@type": "ItemList", "@id": f"{PAGE}#publications", "name": "Research publications",
         "numberOfItems": len(articles), "itemListElement": [
             {"@type": "ListItem", "position": i, "item": {"@id": article["@id"]}}
             for i, article in enumerate(articles, 1)
         ]},
        *articles,
    ]}


def replace_section(source: str, name: str, content: str) -> str:
    start, end = f"<!-- BEGIN GENERATED {name} -->", f"<!-- END GENERATED {name} -->"
    if source.count(start) != 1 or source.count(end) != 1:
        raise ValueError(f"Expected one {name} section in research/index.html")
    return re.sub(re.escape(start) + r".*?" + re.escape(end),
                  lambda _: f"{start}\n{content}\n{end}", source, flags=re.S)


def build(source: str, papers: list[dict]) -> str:
    schema = json.dumps(publication_schema(papers), ensure_ascii=False, indent=2)
    source = replace_section(source, "PUBLICATION SCHEMA",
                             '<script type="application/ld+json">\n' + schema + '\n</script>')
    return replace_section(source, "PUBLICATIONS", render_papers(papers))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    path = ROOT / "research/index.html"
    source = path.read_text(encoding="utf-8")
    expected = build(source, load_publications())
    if args.check:
        if expected != source:
            print("Research publications need regeneration")
            return 1
        print("Research publications are current")
    else:
        path.write_text(expected, encoding="utf-8")
        print("Built research publication summaries and structured data")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
