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

--fix rewrites not-a-stub and wrong-target mirrors from the canonical page.
The other four are list edits, so they are reported and left alone.

    python3 scripts/check_project_pages.py           # report, exit 1 on drift
    python3 scripts/check_project_pages.py --fix     # rewrite bad mirrors
"""

import argparse
import re
import sys
from pathlib import Path

from collapse_mirrors import MARKER, ROBOTS, SITE, STUB

ROOT = Path(__file__).resolve().parent.parent
LIST = ROOT / "content" / "project-pages.txt"


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
    """The site path a stub redirects to, or None if it is not a stub."""
    text = path.read_text(encoding="utf-8", errors="replace")
    if MARKER not in text or ROBOTS not in text:
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
    for page in sorted(ROOT.glob("projects/*.html")):
        if "/" + str(page.relative_to(ROOT)) not in listed_pages:
            problems.append(("unlisted-page", str(page.relative_to(ROOT))))
    for mirror in sorted(on_disk() - listed_mirrors):
        problems.append(("unlisted-mirror", mirror))

    for kind, what in problems:
        print(f"{kind}: {what}")
    if fixed:
        print(f"{fixed} mirror(s) rewritten from the canonical page")
    if problems:
        print(f"{len(problems)} problem(s); edit {LIST.relative_to(ROOT)}")
        return 1
    print(f"{len(listed_pages)} pages, {len(listed_mirrors)} mirrors, no drift")
    return 0


if __name__ == "__main__":
    sys.exit(main())
