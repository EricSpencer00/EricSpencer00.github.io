# ericspencer.us

Hand-written HTML personal site with small Python build scripts. No frameworks.

- **Live:** [ericspencer.us](https://ericspencer.us)
- **Old site:** [ericspencer.us/ericspencer-site-backup/](https://ericspencer.us/ericspencer-site-backup/) — served from its own repo; the `backup-site/` copy here is kept for reference and stripped at deploy
- **Backup repo:** [ericspencer-site-backup](https://github.com/EricSpencer00/ericspencer-site-backup)

## Structure

```
index.html          homepage
projects.html       all 116+ repos + org work
research.html       papers, talks, models
projects/*.html     individual project writeups
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

Run `python3 scripts/build_blog.py` to compile Markdown into `blog/your-slug.html` and update `blog/index.html`. The deployment workflow runs this automatically. Set `published: false` while drafting.

## Link previews

Every page has its own 1200x630 card in `assets/og/`, so pasting a URL into
Slack, iMessage, LinkedIn or Twitter shows that page rather than a shared
thumbnail. Cards are screenshots of the live page, except where the page has
real imagery of its own — then that image is used.

```bash
python3 scripts/build_og_images.py   # reshoot cards (needs Chrome, run locally)
python3 scripts/apply_og_tags.py     # point pages at their cards
```

`apply_og_tags.py` runs on every deploy, after the other build scripts — they
rewrite whole `<head>` blocks, so the preview tags have to be reapplied or each
rebuild quietly drops pages back to a generic card. The card images themselves
are committed; only reshoot them after a visual change.
