#!/usr/bin/env python3
"""Create missing typographic cards for pages that people can share.

Existing photographic or screenshot cards remain intact. This lightweight
fallback covers new canonical pages, noindex destinations, and the durable
app redirects without requiring a browser. Install requirements-assets.txt to
generate cards; --check uses only stdlib.
"""
from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path
from urllib.parse import urlsplit

from build_og_images import OUT, SITE, slug_for
from build_public_apps import app_path, load_apps
from check_site import PageParser, is_noindex, page_files, route_for

ROOT = Path(__file__).resolve().parent.parent


def candidates():
    # App entry cards are emitted below with their first-party share URLs.
    app_routes = {app_path(app) for app in load_apps()}
    for path in page_files():
        route = route_for(path)
        if not route or route in app_routes:
            continue
        text = path.read_text(encoding='utf-8')
        parser = PageParser()
        parser.feed(text)
        if is_noindex(parser):
            # Reuse a local canonical page's card. A separately deployed
            # project can share our hostname without having a page in this
            # tree; its redirect still needs a card at the canonical URL.
            canonical = next((value for value in parser.canonicals if value), '')
            card_url = SITE + route
            target_url = urlsplit(canonical)
            site_url = urlsplit(SITE)
            if ('<!-- redirect stub -->' in text
                    and (target_url.scheme, target_url.netloc) == (site_url.scheme, site_url.netloc)):
                target = ROOT / target_url.path.lstrip('/')
                if target.is_file() or (target / 'index.html').is_file():
                    continue
                card_url = canonical
            title = ''.join(parser.title).strip()
            description = (
                (parser.description[0] if parser.description else '')
                or (parser.social_meta.get('og:description') or [''])[0]
                or title
            )
            if title and description:
                yield card_url, title, description
            continue
        if SITE + route not in parser.canonicals:
            continue
        title = ''.join(parser.title).strip()
        if not title or not parser.description:
            continue
        yield SITE + route, title, parser.description[0]

    # The stable /apps/<slug>/ paths are noindex redirects to the app itself,
    # but people can still share those portfolio links. Give each redirect a
    # first-party card instead of relying on a social crawler to follow the
    # redirect and read metadata from a separately hosted app.
    for app in load_apps():
        yield SITE + app_path(app), app['name'], app['description']


def font(size, weight):
    from PIL import ImageFont
    from fontTools.ttLib import TTFont
    from fontTools.varLib.instancer import instantiateVariableFont

    source = TTFont(ROOT / 'assets/fonts/plus-jakarta-sans-latin-variable.woff2')
    instantiateVariableFont(source, {'wght': weight}, inplace=True)
    source.flavor = None
    data = io.BytesIO()
    source.save(data)
    data.seek(0)
    return ImageFont.truetype(data, size)


def wrap(text, face, width):
    lines, line = [], ''
    for word in text.split():
        candidate = f'{line} {word}'.strip()
        if line and face.getlength(candidate) > width:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    return lines


def render(title, description, destination):
    from PIL import Image, ImageDraw

    title = title.removesuffix(' | Eric Spencer').removesuffix(' — Eric Spencer')
    card = Image.new('RGB', (1200, 630), '#faf7f2')
    draw = ImageDraw.Draw(card)
    label = font(24, 500)
    heading = font(58, 700)
    body = font(29, 400)
    title_lines = wrap(title, heading, 1040)
    if len(title_lines) > 3:
        heading = font(46, 700)
        title_lines = wrap(title, heading, 1040)
    draw.text((80, 55), 'ERIC SPENCER', font=label, fill='#5f000b')
    draw.line((80, 111, 1120, 111), fill='#d6d4d1', width=2)
    y = 144
    for line in title_lines:
        draw.text((80, y), line, font=heading, fill='#080401')
        y += heading.size + 16
    y += 20
    lines = wrap(description, body, 1040)
    available = max(1, (522 - y) // 43)
    if len(lines) > available:
        lines = lines[:available]
        while body.getlength(lines[-1] + '…') > 1040:
            lines[-1] = lines[-1].rsplit(' ', 1)[0]
        lines[-1] += '…'
    for line in lines:
        draw.text((80, y), line, font=body, fill='#59544f')
        y += 43
    draw.text((80, 560), 'ericspencer.us', font=label, fill='#59544f')
    destination.parent.mkdir(parents=True, exist_ok=True)
    card.save(destination, 'JPEG', quality=88, optimize=True, progressive=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--only', nargs='*')
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args()
    missing, written = [], []
    for url, title, description in candidates():
        slug = slug_for(url)
        if args.only and slug not in args.only:
            continue
        destination = OUT / f'{slug}.jpg'
        if destination.exists() and not args.force:
            continue
        if args.check:
            missing.append(url)
        else:
            render(title, description, destination)
            written.append(slug)
    if missing:
        print('Missing social preview cards:\n' + '\n'.join(missing), file=sys.stderr)
        return 1
    print('Social preview cards are complete' if args.check else f'Generated {len(written)} social cards: ' + ', '.join(written))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
