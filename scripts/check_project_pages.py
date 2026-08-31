#!/usr/bin/env python3
"""Hold the project pages to one copy each, listed in content/project-pages.txt.

A project writeup lives at /projects/<slug>.html. Its old Hugo URLs stay alive
as redirect stubs under projects/<year>/<slug>/ and miscellaneous/<slug>/.
collapse_mirrors.py writes those stubs, but it reads the target out of the
mirror's own canonical tag -- so a mirror that never had one, or that points at
the wrong page, is skipped and keeps serving a second copy of the writeup. That
is how the copies drifted apart in the first place.

content/project-pages.txt says which mirror belongs to which page. This script
checks that list against the files on disk and reports every disagreement:

    missing-page     the canonical file is listed but not in the repo
    unlisted-page    projects/<slug>.html exists but is not in the list
    missing-mirror   the mirror is listed but not in the repo
    unlisted-mirror  a mirror directory exists but is not in the list
    not-a-stub       the mirror is a full copy of the page, not a redirect
    wrong-target     the stub redirects somewhere other than its canonical
    wrong-canonical  the page canonicalises to something other than itself

--fix rewrites not-a-stub and wrong-target mirrors from the canonical page.
The other five are list edits or page edits, so they are reported and left
alone. A mirror with a body is diffed against the page before it is
overwritten, and the drift is printed: a copy that grew paragraphs of its own
is an edit someone made, not a stale duplicate, and losing it in silence is
how this went wrong the first time.

    python3 scripts/check_project_pages.py           # report, exit 1 on drift
    python3 scripts/check_project_pages.py --fix     # rewrite bad mirrors
"""

import argparse
import difflib
import re
import sys
from pathlib import Path

from collapse_mirrors import MARKER, SITE, STUB

ROOT = Path(__file__).resolve().parent.parent
LIST = ROOT / "content" / "project-pages.txt"

# Page furniture, the same on every page. Only the writeup is worth diffing.
FURNITURE = re.compile(
    r"<pre class=\"banner\".*?</pre>|<nav\b.*?</nav>|<footer\b.*?</footer>"
    r"|<script\b.*?</script>|<style\b.*?</style>",
    re.S | re.I,
)


def entries():
    """Yield (canonical, [mirror paths], note) from the list."""
    for line in LIST.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("|") + ["", ""]
        canonical, mirrors, note = parts[0], parts[1], parts[2]
        yield canonical, [m for m in mirrors.split(",") if m], note


def on_disk():
    """Every mirror index.html in the repo, as repo-relative strings."""
    found = sorted(ROOT.glob("projects/20*/*/index.html"))
    found += sorted(ROOT.glob("miscellaneous/*/index.html"))
    return {str(p.relative_to(ROOT)) for p in found}


def target_of(path):
    """The site path a stub redirects to, or None if it is not a stub.

    The marker alone decides. Backfilling the noindex line onto older stubs is
    collapse_mirrors.py's job and it runs first, so demanding it here would only
    report a stub it is about to repair -- and would misread the one hand-made
    redirect that leaves noindex off on purpose (projects/index.html).
    """
    text = path.read_text(encoding="utf-8", errors="replace")
    if MARKER not in text:
        return None
    m = re.search(r'<link rel="canonical" href="' + re.escape(SITE) + r'([^"]+)"', text)
    return m.group(1) if m else None


def title_of(canonical, mirror):
    """The stub's title: the canonical page's, or the mirror's if it has none."""
    for path in (ROOT / canonical.lstrip("/"), mirror):
        if path.is_file():
            m = re.search(r"<title>(.*?)</title>", path.read_text(errors="replace"), re.S)
            if m:
                return m.group(1).strip()
    return "Eric Spencer"


def words(path):
    """A page's readable text, with the head and the furniture removed."""
    body = path.read_text(encoding="utf-8", errors="replace").split("</head>", 1)[-1]
    return re.sub(r"<[^>]+>", " ", FURNITURE.sub("", body)).split()


def drift(canonical, mirror):
    """How far a mirror's text has moved from the page it claims to be."""
    page = ROOT / canonical.lstrip("/")
    if not page.is_file():
        return "canonical served from another repo, nothing to diff against"
    a, b = words(page), words(mirror)
    shared = sum(n for _, _, n in difflib.SequenceMatcher(None, a, b).get_matching_blocks())
    return f"{shared}/{len(a)} words of the page, {len(b) - shared} words of its own"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true", help="rewrite mirrors that drifted")
    args = ap.parse_args()

    problems = []
    fixed = 0
    listed_mirrors = set()

    for canonical, mirrors, note in entries():
        if note != "external" and not (ROOT / canonical.lstrip("/")).is_file():
            problems.append(("missing-page", canonical))
        for mirror in mirrors:
            listed_mirrors.add(mirror)
            path = ROOT / mirror
            if not path.is_file():
                problems.append(("missing-mirror", mirror))
                continue
            target = target_of(path)
            if target == canonical:
                continue
            kind = "not-a-stub" if target is None else "wrong-target"
            if args.fix:
                if kind == "not-a-stub":
                    print(f"{mirror}: {drift(canonical, path)}")
                path.write_text(
                    STUB.format(
                        title=title_of(canonical, path),
                        url=SITE + canonical,
                        path=canonical,
                        marker=MARKER,
                    ),
                    encoding="utf-8",
                )
                fixed += 1
            else:
                problems.append((kind, mirror))

    listed_pages = {c for c, _, _ in entries()}
    # A page that canonicalises to its own mirror hands the mirror the ranking,
    # and collapse_mirrors.py then reads that back and leaves the mirror alone.
    for canonical, _, note in entries():
        page = ROOT / canonical.lstrip("/")
        if note == "external" or not page.is_file():
            continue
        m = re.search(r'<link rel="canonical" href="([^"]+)"', page.read_text(errors="replace"))
        if m and m.group(1) != SITE + canonical:
            problems.append(("wrong-canonical", f"{canonical} -> {m.group(1)}"))
    for page in sorted(ROOT.glob("projects/*.html")):
        rel = str(page.relative_to(ROOT))
        if "/" + rel in listed_pages or rel in listed_mirrors:
            continue
        # A stub under projects/ is a mirror of some other page, not a page of
        # its own -- /projects/index.html redirects to /projects.html. Listing
        # it as canonical would claim a redirect is what gets indexed.
        kind = "unlisted-mirror" if target_of(page) else "unlisted-page"
        problems.append((kind, rel))
    for mirror in sorted(on_disk() - listed_mirrors):
        problems.append(("unlisted-mirror", mirror))

    for kind, what in problems:
        print(f"{kind}: {what}")
    if fixed:
        print(f"{fixed} mirror(s) rewritten from the canonical page")
    if problems:
        print(f"{len(problems)} problem(s); fix the page or {LIST.relative_to(ROOT)}")
        return 1
    print(f"{len(listed_pages)} pages, {len(listed_mirrors)} mirrors, no drift")
    return 0


if __name__ == "__main__":
    sys.exit(main())
