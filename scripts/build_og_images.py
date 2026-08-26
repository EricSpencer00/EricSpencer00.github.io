#!/usr/bin/env python3
"""Generate the 1200x630 link-preview image for every published page.

Every page gets a card. By default the card is a screenshot of the page as it
actually renders, taken with headless Chrome. Where a page carries real imagery
of its own -- a project screenshot, a photo -- that image is used instead,
fitted onto the site's paper background.

The images land in assets/og/. Writing them into the pages is apply_og_tags.py.

    python3 scripts/build_og_images.py            # only what is missing
    python3 scripts/build_og_images.py --force    # reshoot everything
    python3 scripts/build_og_images.py --only cv hotdog
"""

import argparse
import concurrent.futures
import io
import re
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "og"
SITE = "https://ericspencer.us"

CARD = (1200, 630)
QUALITY = 88  # JPEG: a third the weight of PNG at this size, no visible loss

# Shoot a 900px-wide viewport rather than a 1200px one. The content column is
# ~700px, so a narrower window fills more of the frame with the thing the page
# is about -- the project title stays readable once a chat client shrinks the
# card to thumbnail width. Shot at 2x and downsampled, so the type stays crisp.
SHOT = (900, round(900 * CARD[1] / CARD[0]))
SCALE = 2

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Directories that are archives, samples or verification files, not pages.
SKIP = ("/.git/", "/backup-site/", "/.claude/", "/samples/", "/tests/", "/_template", "/google")

# Paper background, matching --paper in the site CSS.
PAPER = (250, 248, 243)

# Images that are chrome rather than content: logos, badges, icons.
NOT_CONTENT = re.compile(
    r"(logo|badge|icon|avatar|shields\.io|actions/workflows|favicon)", re.I
)

# Pages on ericspencer.us that GitHub Pages serves out of their own repos, so
# their HTML is not in this tree. Their cards still live in assets/og/ here --
# the pages reference them by absolute URL -- so keep shooting them, or a title
# change over in those repos would leave a stale card behind with no way to
# refresh it from this side.
EXTERNAL = [
    f"{SITE}/{path}/"
    for path in ("Claude-of-Duty", "ddia", "gta-v-gold-checklist", "hotdog")
]


def published_pages():
    """Every published HTML file, grouped by the canonical URL it points at.

    Most project pages exist twice -- once at /projects/<slug>.html and once at
    the old Hugo path /projects/<year>/<slug>/ -- and both carry the same
    canonical. One card per canonical, shared by every file that claims it.
    """
    by_canonical = {}
    for path in sorted(ROOT.rglob("*.html")):
        rel = "/" + str(path.relative_to(ROOT))
        if any(k in rel for k in SKIP):
            continue
        text = path.read_text(errors="replace")
        m = re.search(r'<link rel="canonical" href="([^"]+)"', text)
        url = m.group(1) if m else SITE + rel.replace("/index.html", "/")
        if not url.startswith(SITE):
            continue  # sunset pages that hand their ranking to another domain
        if "YOUR-SLUG" in url:
            continue  # unfilled post template, not a real page
        by_canonical.setdefault(url, []).append(path)
    for url in EXTERNAL:
        # No local files, so there is nothing for apply_og_tags.py to rewrite --
        # those pages carry their tags in their own repos.
        by_canonical.setdefault(url, [])
    return by_canonical


def slug_for(url):
    """A flat filename for a canonical URL: /projects/x.html -> projects-x."""
    p = url.replace(SITE, "").strip("/")
    p = re.sub(r"\.html$", "", p)
    p = re.sub(r"/index$", "", p)
    return re.sub(r"[^a-z0-9]+", "-", p.lower()).strip("-") or "home"


def content_image(pages):
    """The first real content image on a page, if it has one.

    Skips logos, badges and icons -- those make for a worse card than the page
    itself does.
    """
    for path in pages:
        text = path.read_text(errors="replace")
        body = text.split("</head>", 1)[-1]
        for src in re.findall(r'<img[^>]+src="([^"]+)"', body):
            if NOT_CONTENT.search(src):
                continue
            if src.startswith("/"):
                src = SITE + src
            if not src.startswith("http"):
                continue
            return src
    return None


def fetch(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "og-builder"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.read()
    except Exception:
        return None


def fit_to_card(img):
    """Place an image on a 1200x630 paper card.

    Landscape-ish images fill the card. Tall images -- phone screenshots, mostly
    -- are centred on the paper background rather than cropped to a sliver.
    """
    from PIL import Image

    img = img.convert("RGB")
    card = Image.new("RGB", CARD, PAPER)
    ratio = img.width / img.height
    target = CARD[0] / CARD[1]

    if 0.8 * target <= ratio <= 2.6:  # close enough to fill
        scale = max(CARD[0] / img.width, CARD[1] / img.height)
        resized = img.resize(
            (round(img.width * scale), round(img.height * scale)), Image.LANCZOS
        )
        card.paste(
            resized, ((CARD[0] - resized.width) // 2, (CARD[1] - resized.height) // 2)
        )
    else:  # letterbox, with breathing room
        scale = min(CARD[0] / img.width, (CARD[1] - 64) / img.height)
        resized = img.resize(
            (round(img.width * scale), round(img.height * scale)), Image.LANCZOS
        )
        card.paste(
            resized, ((CARD[0] - resized.width) // 2, (CARD[1] - resized.height) // 2)
        )
    return card


def screenshot(url, dest):
    """Shoot the live page at 2x and downsample to card size."""
    from PIL import Image

    # No --user-data-dir: pointing Chrome at a fresh profile makes it hang on
    # first-run setup instead of shooting. The default profile handles
    # concurrent headless instances fine.
    with tempfile.TemporaryDirectory() as tmp:
        raw = Path(tmp) / "shot.png"
        proc = subprocess.run(
            [
                CHROME,
                "--headless",
                "--disable-gpu",
                "--hide-scrollbars",
                "--no-sandbox",
                f"--force-device-scale-factor={SCALE}",
                f"--window-size={SHOT[0]},{SHOT[1]}",
                "--virtual-time-budget=6000",
                f"--screenshot={raw}",
                url,
            ],
            capture_output=True,
            timeout=90,
        )
        if not raw.exists():
            raise RuntimeError(proc.stderr.decode()[-300:] or "no screenshot written")
        img = Image.open(raw).convert("RGB").resize(CARD, Image.LANCZOS)
        save(img, dest)


def save(img, dest):
    img.save(dest, "JPEG", quality=QUALITY, optimize=True, progressive=True)


def is_live(url):
    """A page that does not resolve would only yield a card of the 404 screen."""
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "og-builder"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status == 200
    except Exception:
        return False


def build_one(url, pages, force):
    slug = slug_for(url)
    dest = OUT / f"{slug}.jpg"
    if dest.exists() and not force:
        return slug, "kept"
    if not is_live(url):
        dest.unlink(missing_ok=True)
        return slug, "dead"

    src = content_image(pages)
    if src:
        data = fetch(src)
        if data:
            try:
                from PIL import Image

                img = Image.open(io.BytesIO(data))
                if img.width >= 400:
                    save(fit_to_card(img), dest)
                    return slug, "photo"
            except Exception:
                pass

    screenshot(url, dest)
    return slug, "shot"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--only", nargs="*", default=None)
    ap.add_argument("--jobs", type=int, default=6)
    args = ap.parse_args()

    if not Path(CHROME).exists():
        sys.exit(f"Chrome not found at {CHROME}")
    OUT.mkdir(parents=True, exist_ok=True)

    pages = published_pages()
    if args.only:
        pages = {u: p for u, p in pages.items() if slug_for(u) in args.only}

    counts = {}
    with concurrent.futures.ThreadPoolExecutor(args.jobs) as pool:
        futures = {
            pool.submit(build_one, u, p, args.force): u for u, p in pages.items()
        }
        for done in concurrent.futures.as_completed(futures):
            url = futures[done]
            try:
                slug, how = done.result()
                counts[how] = counts.get(how, 0) + 1
                print(f"  {how:6} {slug}")
            except Exception as e:
                counts["failed"] = counts.get("failed", 0) + 1
                print(f"  FAIL   {url}: {e}")

    print(f"\n{len(pages)} pages: " + ", ".join(f"{v} {k}" for k, v in sorted(counts.items())))
    return 1 if counts.get("failed") else 0


if __name__ == "__main__":
    sys.exit(main())
