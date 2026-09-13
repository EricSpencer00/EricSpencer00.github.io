# Public content and SEO audit

Audited 2026-09-13 against the `dev` checkout for `ericspencer00.github.io`.
The canonical public HTML, generated catalogs, local app entry points, and
deployment workflows were reviewed together. The old backup site, editor
workspace, tests, and redirect-only mirrors are not treated as public content.

## Verified

- 63 canonical project writeups and 62 legacy mirrors pass the project-page
  drift check.
- 144 published HTML documents pass the SEO-head hygiene check.
- 64 JSON-LD blocks parse as JSON.
- `sitemap.xml` contains 64 indexable URLs, including `/1rm/`,
  `/ulam-spiral/`, and `/ulam-spiral-b12/`.
- Internal links, local assets, canonical URLs, robots directives, and the
  deploy-time mirror policy were checked. Known malformed block wrappers in
  the project archive were repaired.
- Open Graph cards now exist for local indexable pages. Five metadata-only
  entries point to pages served from another repository or to an external
  destination: the Claude architect quiz, Resilient, editor, LaTeX, and the
  archived resume route.

## Changes made

- Added a shared landing-page shell to the portfolio surfaces: projects,
  project writeups, publications, CV, blog, news, and 404.
- Kept interactive app UIs such as Ulam Spiral and 1RM product-specific; the
  shared shell is for editorial and portfolio pages around those apps.
- Replaced catalog narration, fake precision, unsupported “first” claims,
  vague AI labels, and financial/medical overstatement with direct artifact
  descriptions and explicit prototype boundaries.
- Removed legacy `meta keywords` tags and made Open Graph metadata consistent.
- Added a local-host option to the card builder so SEO previews can be tested
  before a page is live.
- Made project-page normalization repeatable in both dev and production
  deploy workflows.

## Human follow-up

- Resolved 2026-09-13: the ChatTLA+ paper was accepted to and presented at
  ICSOFT 2026. The dataset page now records the repository's review-era
  anonymized name without suggesting that the paper is still under review.
- External URLs and third-party claims were not treated as locally verified.
  In particular, confirm the `/latex/` redirect target and any hosted pages
  that are not generated from this repository.
- The noindex transcript pages remain historical artifacts. Their metadata and
  catalog descriptions are neutral, but their quoted exchanges and provenance
  notes were preserved rather than rewritten as original prose.
- The remaining generic-word scan hits are intentional: two words occur in
  quoted ChatGPT output on `meta_research`, and “dynamic programming” is a
  concrete algorithmic option on `mc-carspot`, not promotional copy.
- The pre-existing editor working copy (`editor/index.md`) still contains its
  own review-desk flags; it was not overwritten during this pass. Canonical
  public pages were edited separately and regenerated.
