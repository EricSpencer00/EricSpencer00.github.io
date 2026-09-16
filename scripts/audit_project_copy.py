#!/usr/bin/env python3
"""Create a transparent, review-first audit of the local project copy desk.

This deliberately does *not* claim to identify AI authorship from prose style.
It looks for direct disclosures, AI subject matter, and reviewable editing signals
so a human can make the final call.  The output is local-only: editor/audit.md
and editor/audit.json are never copied into the deployed site.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "editor" / "index.md"
MARKDOWN_OUT = ROOT / "editor" / "audit.md"
JSON_OUT = ROOT / "editor" / "audit.json"

PROJECT = re.compile(
    r"<!-- PROJECT (?P<slug>[^ ]+) START -->\n## (?P<title>[^\n]+)\n\n"
    r"- URL: (?P<url>[^\n]+)\n- Description: (?P<description>[^\n]*)\n"
    r"- Review: (?P<review>[^\n]+)\n\n### Copy\n\n(?P<copy>[\s\S]*?)"
    r"\n<!-- PROJECT \1 END -->"
)

# A mention says that a page is about or uses an AI product; it is not evidence
# that its prose was AI-authored.
AI_TERMS = re.compile(
    r"\b(?:AI|A\.I\.|artificial intelligence|LLM(?:s)?|large language model(?:s)?|"
    r"ChatGPT|OpenAI|Claude|Anthropic|Gemini|Copilot|Ollama|GPT(?:-?\d+(?:\.\d+)?)?|"
    r"Llama(?:\s?\d+)?|Mistral|Gemma|Replicate|Perplexity|RAG|generative)\b",
    re.I,
)

# These are intentionally narrow: only explicit wording counts as an authorship
# disclosure.  No style feature is ever labelled proof of AI authorship.
AUTHORSHIP = re.compile(
    r"\b(?:written|drafted|generated|rewritten|edited|polished|made|created)\s+"
    r"(?:by|with|using)\s+(?:ChatGPT|Claude|Gemini|Copilot|OpenAI|an?\s+AI|"
    r"an?\s+LLM|a\s+language model)\b|\b(?:ChatGPT|Claude|Gemini|Copilot|"
    r"OpenAI|an?\s+AI|an?\s+LLM)\s+(?:wrote|drafted|generated|rewrote|edited|polished)\b",
    re.I,
)

AI_CONTRIBUTION = re.compile(
    r"\b(?:code|repository|project|implementation|application)\b[^.]{0,120}\b"
    r"(?:written|built|made|created|generated)\s+(?:with|using)(?:\s+the\s+help\s+of|\s+help\s+from)?\s+"
    r"(?:ChatGPT|Claude|Gemini|Copilot|OpenAI|an?\s+AI|an?\s+LLM|a\s+language model)\b",
    re.I,
)

# A raw transcript is materially different from a page that merely discusses an
# AI product.  It is direct evidence that model output appears on the page, but
# it still does not identify who wrote the surrounding portfolio prose.
MODEL_OUTPUT = re.compile(
    r"\b(?:ChatGPT|Claude|Gemini|Copilot|an?\s+AI|an?\s+LLM)\s+(?:said|replied|responded)\s*:|"
    r"\bThread generated with (?:ChatGPT|Claude|Gemini|Copilot|an?\s+AI|an?\s+LLM)\b",
    re.I,
)

# Common marketing filler is useful as an editing prompt, not an authorship test.
STYLE = re.compile(
    r"\b(?:seamless(?:ly)?|cutting-edge|robust|comprehensive|revolutionary|"
    r"groundbreaking|game[- ]changing|leverag(?:e|es|ed|ing)|utiliz(?:e|es|ed|ing)|"
    r"in today['’]s .*? landscape)\b",
    re.I,
)

# Claims with a fixed number, money, percentage, or broad absolute need a source,
# date, or qualifying context.  They are not presumed false.
VERIFY = re.compile(
    r"(?:\$\s?\d|\b\d+(?:\.\d+)?\s?(?:%|x|×|million|billion|thousand)\b|"
    r"\b(?:the\s+)?(?:first|best|only)\s+(?:ever|available|way|option|version|solution)\b|"
    r"\b(?:always|never)\s+(?:does|works|sends|returns|delivers|fails|shows|uses)\b)",
    re.I,
)

# This is a narrow professional-tone screen: profanity, contempt, or language
# that tells a reader their time is being wasted.  It does not judge a project's
# subject matter or technical vocabulary.
TONE = re.compile(
    r"\b(?:fuck(?:ing)?|shit|bullshit|crap|damn|hell|stupid|dumb|idiot(?:ic)?|"
    r"garbage|nonsense|ridiculous|worse version|waste (?:their|your|my) time)\b",
    re.I,
)

FIRST_PERSON = re.compile(r"\b(?:I|I'm|I've|I'll|I'd|me|my|mine|we|we're|we've|we'll|we'd|us|our|ours)\b")
PERSONA = re.compile(
    r"\b(?:Eric\s+Spencer(?:'s)?|a\s+project\s+by\s+Eric(?:\s+Spencer)?|"
    r"Eric\s+Spencer\s+(?:built|made|created|wrote|developed))\b",
    re.I,
)
ASIDE = re.compile(
    r"\b(?:the\s+thing\s+I\s+actually|in\s+hindsight|funny\s+to\s+watch|"
    r"worth\s+calling\s+out|the\s+whole\s+point|the\s+only\s+thing\s+that\s+matters)\b",
    re.I,
)
MARKUP = re.compile(r"<!doctype|</?(?:html|head|body|script|style)\b|\[\[https?://", re.I)
LINK = re.compile(r"\[[^\]]*\]\([^)]*\)")


def clean(value: str) -> str:
    """Turn enough Markdown into plain text to make sentence excerpts readable."""
    value = re.sub(r"```[\s\S]*?```", " code block ", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", value)
    value = re.sub(r"`([^`]*)`", r"\1", value)
    value = re.sub(r"^#{1,6}\s+", "", value, flags=re.M)
    value = re.sub(r"^[-*]\s+", "", value, flags=re.M)
    return html.unescape(re.sub(r"\s+", " ", value)).strip()


def sentences(value: str) -> list[str]:
    plain = clean(value)
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9`\"'])", plain) if part.strip()]


def excerpt(value: str, limit: int = 230) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    return value if len(value) <= limit else value[: limit - 1].rstrip() + "…"


def add(flags: list[dict], kind: str, severity: str, note: str, text: str) -> None:
    item = {"kind": kind, "severity": severity, "note": note, "text": excerpt(text)}
    if item not in flags:
        flags.append(item)


def audit(record: dict) -> dict:
    copy = record["copy"]
    plain = clean(copy)
    lines = sentences(copy) or [plain]
    flags: list[dict] = []
    terms = sorted({match.group(0) for match in AI_TERMS.finditer(plain)}, key=str.lower)
    is_ai_material = bool(terms)

    for line in lines:
        if AUTHORSHIP.search(line):
            add(flags, "authorship disclosure", "evidence", "Explicitly describes AI help with the writing.", line)
        if AI_CONTRIBUTION.search(line):
            add(flags, "AI contribution disclosure", "evidence", "Explicitly describes AI help with the project or its code; this is not necessarily prose authorship.", line)
        if MODEL_OUTPUT.search(line):
            add(flags, "quoted model output", "evidence", "This appears to preserve output or a transcript from an AI system.", line)
        if AI_TERMS.search(line):
            add(flags, "AI subject matter", "info", "Names an AI tool, model, or AI-related concept; this is not prose-authorship evidence.", line)
        if STYLE.search(line):
            add(flags, "generic phrasing", "review", "Consider replacing marketing-style language with a concrete fact, example, or outcome.", line)
        if VERIFY.search(line):
            add(flags, "claim to verify", "review", "Add a date, source, measurement, or qualifier if this claim is meant to be current.", line)
        if TONE.search(line):
            add(flags, "professional tone", "review", "Consider neutral wording if this page is intended as public portfolio copy.", line)
        if is_ai_material and FIRST_PERSON.search(line):
            add(flags, "STE001 voice", "required", "AI-related material must use a neutral declaration, not first-person voice.", line)
        if PERSONA.search(line):
            add(flags, "STE001 attribution", "required", "Replace a claim about Eric with a neutral, verifiable project statement.", line)
        if ASIDE.search(line):
            add(flags, "editorial aside", "review", "Convert commentary about the writer's reaction into a project fact, result, or limitation.", line)
        if MARKUP.search(line):
            add(flags, "formatting leak", "review", "Raw markup or malformed Markdown is appearing in the copy review export.", line)

    links = len(LINK.findall(copy))
    if len(plain.split()) < 45:
        add(flags, "thin writeup", "review", "This has under 45 words of body copy; add context or mark it intentionally brief.", plain)
    if links == 0 and len(plain.split()) > 100:
        add(flags, "source gap", "review", "A longer technical writeup has no linked repository, demo, or supporting source.", plain)

    # Keep the review desk practical: three excerpts per non-evidence category
    # are enough to diagnose a page without drowning its editor in warnings.
    kept: list[dict] = []
    counts: Counter[str] = Counter()
    for flag in flags:
        cap = 8 if flag["kind"] == "authorship disclosure" else 3
        if counts[flag["kind"]] < cap:
            kept.append(flag)
            counts[flag["kind"]] += 1
    ste001_required = [flag for flag in kept if flag["kind"].startswith("STE001")]
    return {**record, "wordCount": len(plain.split()), "aiTerms": terms, "linkCount": links, "ste001Required": bool(ste001_required), "flags": kept}


def render_markdown(records: list[dict]) -> str:
    all_flags = [flag for record in records for flag in record["flags"]]
    kinds = Counter(flag["kind"] for flag in all_flags)
    evidence = sum(flag["kind"] == "authorship disclosure" for flag in all_flags)
    contribution = sum(flag["kind"] == "AI contribution disclosure" for flag in all_flags)
    lines = [
        "# Project prose audit",
        "",
        f"Generated {date.today().isoformat()} from `editor/index.md`: {len(records)} project writeups.",
        "",
        "## How to read this",
        "",
        "This is a transparent editing audit, not an AI-authorship detector. Current evidence does not support proving who wrote prose from its style alone. `authorship disclosure` is shown only where a page expressly says that AI helped write or edit it. `quoted model output` identifies page text that labels itself as an AI response or transcript. `AI subject matter` means the project mentions an AI product or concept; it says nothing about authorship.",
        "",
        "`STE001` is the site rule for a neutral statement declaration: name the artifact, describe a concrete behavior, and name evidence, a limit, or a result. It must not use first-person voice or claim an Eric persona. Example: `STE001 — The extension records browser-visible search queries and exports prompt/query pairs as CSV.`",
        "",
        "The remaining flags are review prompts: factual claims that may need a date or source, marketing-like filler, raw-export problems, thin context, editorial asides, and narrow professional-tone issues (profanity, contempt, or telling a reader their time is being wasted). They are not errors until you decide they are.",
        "",
        "## Summary",
        "",
        f"- Explicit prose-authorship disclosures: **{evidence}**",
        f"- Explicit AI project/code contribution disclosures: **{contribution}**",
        f"- Pages requiring a STE001 conversion: **{sum(record['ste001Required'] for record in records)}**",
        f"- Pages that mention AI tools or concepts: **{sum(bool(record['aiTerms']) for record in records)}**",
        f"- Pages with at least one editing prompt: **{sum(bool(record['flags']) for record in records)}**",
    ]
    for kind, count in sorted(kinds.items()):
        lines.append(f"- {kind.title()}: **{count}** excerpt{'s' if count != 1 else ''}")
    lines.extend(["", "## Page-by-page review", ""])
    for record in records:
        lines.extend([
            f"### {record['title']}",
            "",
            f"- URL: {record['url']}",
            f"- Words: {record['wordCount']} · Links: {record['linkCount']}",
            f"- AI terms named: {', '.join(record['aiTerms']) if record['aiTerms'] else 'none'}",
        ])
        if not record["flags"]:
            lines.append("- Findings: no rule-based review prompts.")
        else:
            for flag in record["flags"]:
                lines.extend([
                    f"- **{flag['kind'].title()}** — {flag['note']}",
                    f"  - “{flag['text']}”",
                ])
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit the local project copy desk")
    parser.add_argument("--check", action="store_true", help="fail when a STE001 rule still needs conversion")
    args = parser.parse_args()
    source = SOURCE.read_text(encoding="utf-8")
    raw_records = [match.groupdict() for match in PROJECT.finditer(source)]
    if not raw_records:
        raise SystemExit("No project records found in editor/index.md")
    records = [audit(record) for record in raw_records]
    MARKDOWN_OUT.write_text(render_markdown(records), encoding="utf-8")
    JSON_OUT.write_text(json.dumps({"generated": date.today().isoformat(), "records": records}, indent=2) + "\n", encoding="utf-8")
    required = sum(record["ste001Required"] for record in records)
    print(f"Audited {len(records)} project writeups -> {MARKDOWN_OUT.relative_to(ROOT)} ({required} STE001 conversion{'s' if required != 1 else ''} required)")
    if args.check and required:
        raise SystemExit(f"STE001 check failed: {required} project writeups still need conversion")


if __name__ == "__main__":
    main()
