#!/usr/bin/env python3
"""Publish the live project builds at their existing site paths.

The source for these small builds lives with the other project material under
``projects/``. GitHub Pages serves files from their repository paths, though,
so the old top-level paths are maintained as byte-for-byte route mirrors.

    python3 scripts/build_project_routes.py
    python3 scripts/build_project_routes.py --check
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

LIVE_PROJECTS = frozenset({"1rm", "stem-player", "ulam-spiral", "ulam-spiral-b12"})

ROUTES = {
    name: ROOT / "projects" / "2026" / name
    for name in LIVE_PROJECTS
}


def is_live_project_source(path: Path) -> bool:
    """Whether a path belongs to one of the live builds under projects/2026."""
    try:
        relative = path.relative_to(ROOT / "projects" / "2026")
    except ValueError:
        return False
    return bool(relative.parts) and relative.parts[0] in LIVE_PROJECTS


def source_files(source: Path) -> dict[Path, Path]:
    """Return source-relative files and their route-mirror destinations."""
    return {
        path.relative_to(source): path
        for path in sorted(source.rglob("*"))
        if path.is_file()
    }


def route_files(route: Path) -> dict[Path, Path]:
    return {
        path.relative_to(route): path
        for path in sorted(route.rglob("*"))
        if path.is_file()
    } if route.is_dir() else {}


def check_route(name: str, source: Path, destination: Path) -> list[str]:
    problems: list[str] = []
    expected = source_files(source)
    actual = route_files(destination)

    for relative in sorted(expected):
        target = destination / relative
        if not target.is_file():
            problems.append(f"{name}: missing route file {target.relative_to(ROOT)}")
        elif target.read_bytes() != expected[relative].read_bytes():
            problems.append(f"{name}: route differs {target.relative_to(ROOT)}")
    for relative in sorted(set(actual) - set(expected)):
        problems.append(f"{name}: stale route file {(destination / relative).relative_to(ROOT)}")
    return problems


def build_route(source: Path, destination: Path) -> None:
    expected = source_files(source)
    destination.mkdir(parents=True, exist_ok=True)

    # The destination is a generated public mount. Remove only files inside
    # this exact route before copying the source tree back into place.
    for relative, path in route_files(destination).items():
        if relative not in expected:
            path.unlink()

    for relative, path in expected.items():
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    problems: list[str] = []
    for name, source in ROUTES.items():
        if not source.is_dir():
            problems.append(f"{name}: missing project source {source.relative_to(ROOT)}")
            continue
        destination = ROOT / name
        if args.check:
            problems.extend(check_route(name, source, destination))
        else:
            build_route(source, destination)

    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 1
    print("project route mirrors are current" if args.check else "built project route mirrors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
