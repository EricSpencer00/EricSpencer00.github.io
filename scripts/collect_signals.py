#!/usr/bin/env python3
"""
collect_signals.py — snapshot repository traffic into assets/data/signals.json.

Stars are a lifetime vanity total: a repo starred once in 2023 outranks one
people are reading today. Views are the honest signal, but /traffic/views needs
push access on each repo, so the browser cannot ask for it -- this runs nightly
with a token and publishes a static file the page can fetch anonymously.

GitHub keeps only 14 days of traffic. Daily buckets are merged into the stored
file keyed by date, so re-runs are idempotent and the record outlives the
window GitHub itself retains.

Env:
  GITHUB_TOKEN   PAT with `repo` scope (or a fine-grained token with
                 Administration: read) for every account below.
  SIGNALS_OWNERS Comma-separated owners. Default: EricSpencer00,LUC-AI4FM
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# The full daily record is the source of truth and grows with every run; the
# page gets a rollup of it, because shipping the history to every visitor is a
# quarter-megabyte of JSON to render two numbers.
HISTORY = ROOT / "assets" / "data" / "signals-history.json"
OUT = ROOT / "assets" / "data" / "signals.json"

API = "https://api.github.com"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OWNERS = [o.strip() for o in
          os.environ.get("SIGNALS_OWNERS", "EricSpencer00,LUC-AI4FM").split(",") if o.strip()]

# Traffic older than this is dropped so the history, which is re-committed on
# every nightly run, does not grow without bound. 120 covers the 90-day window
# the page shows with a month to spare.
RETAIN_DAYS = 120


def get(url: str, *, allow_denied: bool = False):
    request = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "ericspencer.us-signals",
        **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}),
    })
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        # Traffic access can be unavailable for individual repositories. A
        # rate limit or failed inventory must abort without rewriting history.
        limited = (error.headers.get("X-RateLimit-Remaining") == "0"
                   or error.headers.get("Retry-After") is not None)
        if allow_denied and error.code in (403, 404) and not limited:
            return None
        raise


def repos(owner: str) -> list[dict]:
    out, page = [], 1
    while page <= 5:
        # `type=owner` keeps forks-of-others out of the traffic sweep; the site
        # shows them, but their views are not a signal about this work.
        data = get(f"{API}/users/{owner}/repos?per_page=100&page={page}&type=owner")
        if not data:
            break
        out.extend(data)
        if len(data) < 100:
            break
        page += 1
    return [r for r in out if not r.get("private")]


def load_existing() -> dict:
    if not HISTORY.exists():
        return {"repos": {}}
    try:
        return json.loads(HISTORY.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError("signals-history.json unreadable; preserving the snapshot") from error


def merge_daily(stored: dict, series: list[dict], key: str) -> dict:
    """Fold GitHub's 14-day buckets into the stored {date: {views, uniques}}."""
    for point in series:
        day = point["timestamp"][:10]
        entry = stored.setdefault(day, {})
        entry[key] = point.get("count", 0)
        entry[f"{key}_uniques"] = point.get("uniques", 0)
    cutoff = (date.today() - timedelta(days=RETAIN_DAYS)).isoformat()
    # Days with no traffic are dropped rather than stored as zeros: 71% of the
    # buckets GitHub returns are empty, and a missing day sums the same as a
    # zero one. Keeping them made the file four times bigger for nothing.
    return {d: v for d, v in sorted(stored.items())
            if d >= cutoff and (v.get("views") or v.get("clones"))}


def rollup(store: dict) -> dict:
    """The two windows the page shows, per repo, with the empties dropped.

    Clones are collected but deliberately not published: CI checkouts dominate
    them (one repo shows 6,805 clones against 61 views), so they measure robots,
    not readers.
    """
    today = date.today()
    windows = {"d14": (today - timedelta(days=14)).isoformat(),
               "d90": (today - timedelta(days=90)).isoformat()}
    out = {}
    for full, entry in store.items():
        daily = entry.get("daily", {})
        counts = {}
        for label, cutoff in windows.items():
            counts[label] = sum(v.get("views", 0) for d, v in daily.items() if d >= cutoff)
            counts[f"{label}u"] = sum(v.get("views_uniques", 0)
                                      for d, v in daily.items() if d >= cutoff)
        if counts["d90"]:
            out[full] = counts
    return out


def main() -> None:
    if not TOKEN:
        print("signals: skipped; SIGNALS_TOKEN is not configured. Existing snapshots preserved.",
              file=sys.stderr)
        return

    data = load_existing()
    store = data.setdefault("repos", {})
    seen = denied = 0
    collected = {}

    for owner in OWNERS:
        for repo in repos(owner):
            full = repo["full_name"]
            traffic = get(f"{API}/repos/{full}/traffic/views", allow_denied=True)
            if traffic is None:
                denied += 1
                continue
            if not isinstance(traffic.get("views"), list):
                raise ValueError(f"invalid traffic response for {full}; preserving the snapshot")
            clones = get(f"{API}/repos/{full}/traffic/clones", allow_denied=True) or {}

            entry = store.setdefault(full, {})
            daily = merge_daily(entry.get("daily", {}), traffic.get("views", []), "views")
            daily = merge_daily(daily, clones.get("clones", []), "clones")
            entry["daily"] = daily
            entry["stars"] = repo.get("stargazers_count", 0)
            entry["name"] = repo["name"]
            collected[full] = entry
            seen += 1

    if not seen:
        print(f"signals: no accessible traffic ({denied} denied); existing snapshots preserved",
              file=sys.stderr)
        return

    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    data["generated"] = stamp
    # Compute the complete rollup before writing either snapshot, so an
    # invalid response or history record cannot leave a half-refreshed pair.
    # Only publish repositories observed in this run. A denied repository's
    # retained history must never acquire a fresh collection timestamp.
    compact = {"generated": stamp, "repos": rollup(collected)}
    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    # Minified: this file is rewritten nightly, so every byte lands in a new
    # git blob. It is machine state, not something anyone reads in a diff.
    data["repos"] = {k: v for k, v in store.items() if v.get("daily")}
    HISTORY.write_text(json.dumps(data, separators=(",", ":"), sort_keys=True) + "\n",
                       encoding="utf-8")

    OUT.write_text(json.dumps(compact, separators=(",", ":"), sort_keys=True) + "\n",
                   encoding="utf-8")
    print(f"signals: {seen} repo(s) with traffic, {denied} without access; "
          f"{len(compact['repos'])} with views in the last 90d "
          f"-> {OUT.relative_to(ROOT)} ({OUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
