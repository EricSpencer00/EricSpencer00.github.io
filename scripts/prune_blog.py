#!/usr/bin/env python3
"""
prune_blog.py — drop blog/ from the build when nothing is published.

blog/index.html has to stay in git: it carries the POSTS_START/POSTS_END
markers that build_blog.py fills in. But with no published posts it is a page
that says "No posts yet." with nothing linking to it, so it ships only once
there is something to read. Same idea as the backup-site strip in deploy.yml.

Run after build_blog.py and before build_sitemap.py.
"""

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_blog import load_posts

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    posts = load_posts()
    if posts:
        print(f"prune_blog: {len(posts)} published post(s), keeping blog/")
        return
    shutil.rmtree(ROOT / "blog", ignore_errors=True)
    print("prune_blog: no published posts, blog/ removed from this build")


if __name__ == "__main__":
    main()
