# ericspencer.us

Hand-written HTML personal site with small Python build scripts. No frameworks.

- **Live:** [ericspencer.us](https://ericspencer.us)
- **Old site:** [ericspencer.us/backup-site/](https://ericspencer.us/backup-site/)
- **Backup repo:** [ericspencer-site-backup](https://github.com/EricSpencer00/ericspencer-site-backup)

## Structure

```
index.html          homepage
projects.html       all 116+ repos + org work
research.html       papers, talks, models
projects/*.html     individual project writeups
backup-site/        full Hugo site archive

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
```
