# ericspencer.us

Hand-written HTML personal site with small Python build scripts. No frameworks.

- **Live:** [ericspencer.us](https://ericspencer.us)
- **Old site source:** [ericspencer-site-backup](https://github.com/EricSpencer00/ericspencer-site-backup) — the `backup-site/` copy here is kept for reference and stripped at deploy
- **Backup repo:** [ericspencer-site-backup](https://github.com/EricSpencer00/ericspencer-site-backup)

## Structure

```
index.html          homepage
projects/           projects and live work
research/           publications: papers, talks, models, and tools
projects/*/         individual project writeups
projects/2026/1rm/ source for the live 1RM build and its route mirror
projects/2026/stem-player/ Stemacle route stub
projects/2026/ulam-spiral/ live Ulam spiral build
projects/2026/ulam-spiral-b12/ base-twelve Ulam spiral build
blog/               compiled from content/blog/*.md
cv/, resume/        landing pages, built from content/resumes.txt
assets/og/          link-preview cards, one per page
backup-site/        full Hugo site archive (stripped at deploy)
```

## Pages served from other repos

Some paths under ericspencer.us are GitHub Pages project sites, not files here.
A repo named `foo` with Pages enabled takes over `ericspencer.us/foo/` and
shadows any `foo/` directory in this repo — so if that repo's Pages build ever
fails, the path 404s and this repo cannot cover for it.

| Path | Repo |
| --- | --- |
| `/Claude-of-Duty/` | `Claude-of-Duty` (`gh-pages` branch; source on `main`) |
| `/ddia/` | `ddia` |
| `/gta-v-gold-checklist/` | `gta-v-gold-checklist` |
| `/hotdog/` | `hotdog` |
| `/ericspencer-site-backup/` | `ericspencer-site-backup` |

Edit those pages in their own repos. Their preview cards still live in
`assets/og/` here and are listed in `EXTERNAL` in `scripts/build_og_images.py`,
so reshooting keeps working.

## One copy of each project page

A project writeup lives at `projects/<slug>/`. Its old flat `.html` URL and Hugo
URLs (`projects/<year>/<slug>/`, `miscellaneous/<slug>/`) stay alive as
noindex redirect stubs, so the writeup is served once and the old links still
work.

`content/project-pages.txt` lists which mirror belongs to which page. The
pairing is not derivable from the slug, so add a line when you add a page.

The live builds in `projects/` keep their existing public paths (`/1rm/`,
`/stem-player/`, `/ulam-spiral/`, and `/ulam-spiral-b12/`).
`scripts/build_project_routes.py` refreshes those top-level route mirrors on
each deployment.

```bash
python3 scripts/check_project_pages.py         # report drift; runs on deploy
python3 scripts/check_project_pages.py --fix   # rewrite mirrors from the page
```

`--fix` diffs a mirror against the page before it overwrites it and prints how
many words were the mirror's own, so a copy that was edited by hand is not lost
without a word.

## Blog workflow

Write posts as `content/blog/your-slug.md` with front matter:

```yaml
---
title: A post title
date: 2026-07-12
description: A short description for listings and search engines.
published: true
---
```

Run `python3 scripts/build_blog.py` to compile Markdown into `blog/your-slug/` and update `blog/index.html`. The deployment workflow runs this automatically. Set `published: false` while drafting.

## Link previews

Pages have 1200×630 preview cards in `assets/og/`. Existing cards use page
screenshots or project imagery. New pages get a card from their title and
description, using the same licensed fonts as the site.
The stable `/apps/<slug>/` links are redirects, but they get their own cards so
iMessage, X, and other share previews work even when a crawler does not follow
the product's redirect.

```bash
python3 -m pip install -r requirements-assets.txt
python3 scripts/build_social_cards.py  # generate missing cards from metadata
python3 scripts/build_social_cards.py --force --only research  # refresh a card
python3 scripts/build_og_images.py   # optional page screenshots (needs Chrome)
python3 scripts/apply_og_tags.py     # point pages at their cards
```

`apply_og_tags.py` runs on every deploy, after the other build scripts — they
rewrite whole `<head>` blocks, so the preview tags have to be reapplied or each
rebuild quietly drops pages back to a generic card. The card images themselves
are committed; only reshoot them after a visual change.

## SEO release checks

Publication citations, artifact links, and summaries live in
`content/publications.json`. `scripts/build_research.py` updates the research
page; the CV generator reads the same citations and `content/cv.json`.

Run the generators in the order in `.github/workflows/deploy.yml`, then:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/check_site.py
python3 scripts/build_social_cards.py --check
```

The release check rejects missing internal links to indexable pages and CSP
policies that block the installed Analytics tag or its collection endpoints.
Fonts are served from `assets/fonts/`; the upstream licenses are kept beside
the font files. Experience logos use small WebP variants for their 36px boxes.
