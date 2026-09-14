# SEO / GEO project triage and issue backlog

**Status:** planned; research and prioritization only  
**Date:** 2026-09-11  
**Owner:** Eric Spencer  
**Scope:** `ericspencer.us`, the public GitHub portfolio, AI4FM/research surfaces, and FROM AMERICA product surfaces

## Decision summary

The portfolio should be treated as three connected surfaces rather than one flat list of projects:

1. **Eric Spencer / research entity** — formal methods, TLA+, LLMs, Loyola/AI4FM, papers, models, datasets, and the current professional identity.
2. **Selected real work** — maintained software, usable tools, live apps, research artifacts, and products with an identifiable audience or destination.
3. **Archive** — coursework, hackathon prototypes, experiments, toys, duplicated writeups, forks, and personal notes.

All three can remain useful to a human browsing the site. They should not all compete for the same search visibility. The selected layer should receive the strongest internal links, the most complete descriptions, and the cleanest structured data. Archive material should be clearly labeled and should be eligible for `noindex` when it has no independent search intent or is too thin/stale to represent the work well.

This is an issue backlog, not a ranking report. The earlier 50-query fuzzy scan measured visibility in the search tool, not Google position, Search Console position, or consistent placement across AI assistants. Do not assign letter grades until position, query, location, device, and date are measured from a real search dataset.

## Evidence collected

### Public inventory and strongest surfaces

- [Eric Spencer’s GitHub profile](https://github.com/EricSpencer00) currently shows **161 repositories**, 60 stars, and pins **Resilient**, **LUC-AI4FM/TLA-Prove**, and **LUC-AI4FM/tlakit**. The profile identifies Eric as a formal methods researcher at Loyola University Chicago and links the personal site, ORCID, LinkedIn, and Hugging Face.
- The [personal homepage](https://ericspencer.us/) currently leads with formal methods, LLM research, AI4FM, ChatTLA+, Resilient, FROM AMERICA, and selected work such as Not Hotdog, tlakit, and paper-digest.
- The current [projects hub](https://ericspencer.us/projects.html) exposes the entire public-repository corpus plus LUC-AI4FM and FROM AMERICA work. That is useful as an index, but it is too broad to be the only information architecture for search.
- The public research graph is strong: [AI4FM](https://ai4fm.cs.luc.edu/), [DBLP](https://dblp.org/pid/439/8284.html), arXiv papers, Hugging Face models, GitHub repositories, and the personal site reinforce one another.
- The [Resilient repository](https://github.com/EricSpencer00/Resilient) has a substantially more specific proposition than its name alone: a statically typed compiled language for safety-critical embedded systems, with Z3-backed contracts, `no_std` runtime work, and self-healing blocks.
- The [tlakit repository](https://github.com/LUC-AI4FM/tlakit) and [PyPI package](https://pypi.org/project/tlakit/) create a strong package-to-documentation-to-author path. The [TLA-Prove repository](https://github.com/LUC-AI4FM/TLA-Prove) supplies a similarly strong research-artifact path.

### Local site inventory

The following are read-only observations from this repository:

- `content/project-pages.txt` maps **59 canonical project writeups** and **62 redirect mirrors**; `scripts/check_project_pages.py` reports `62 pages, 62 mirrors, no drift`.
- The 59 canonical writeups contain **58 unique titles and 58 unique descriptions**. The duplicate pair is `projects/fraud-predictor.html` and `projects/fraud-predictor-full.html`, both titled “Machine Learning Fraud Identifier” with the same description.
- A metadata pass found **17 project descriptions shorter than 80 characters** and **7 rendered titles shorter than 25 characters**. These are not automatically penalties, but they are weak opportunities for intent matching.
- The existing project-copy audit flags several very thin or archive-like writeups, including Daily Task, AuraOS, Anagram Solver V2, BrightBet, Dexcom Navbar Icon, Movie Recommendation, and the maze/transcript pages. Thinness should be handled by tier: expand valuable work; archive or noindex low-value work.
- `scripts/build_og_images.py` currently discovers **77 canonical URL groups** and **134 grouped HTML files**, including canonical pages, mirrors, and four pages served by external project repositories. The checked-in `sitemap.xml` currently contains **67 `<loc>` entries**, so sitemap freshness needs a release-time check.
- `scripts/seo_tags.py --check` currently labels every visited page `would-write` instead of calculating whether a change is actually needed. Its output should not be treated as an SEO defect count.
- The shared metadata pattern is otherwise broadly healthy on the main site: canonical URLs, robots directives, Open Graph/Twitter fields, link-preview images, and JSON-LD are present on the major pages.

### Earlier visibility scan

The 50-query fuzzy scan should be retained as a baseline with a clear label:

- 8 identity queries, 12 research queries, and 30 product/project queries.
- 44/50 first results were owned, authoritative, or otherwise relevant in the search tool.
- Research queries were the strongest: site, GitHub, AI4FM, arXiv, and DBLP repeatedly surfaced.
- Product queries were mixed: 13/30 led directly to a project, app, or package; 8/30 led only to the portfolio index; 4/30 required a GitHub/profile relay; and 5/30 were noisy or non-target results.
- The most important collisions were **PicAI vs Picaius**, **GluCoPilot vs another GlucoPilot app**, the generic word **Resilient**, and the changing public name **TLA Runner / TLA+ Generator**.

### Safe measure-only run — 2026-09-11

This is the local, non-mutating equivalent of the linked skill’s `/seo measure` mode. No Search Console, Bing Webmaster Tools, App Store Connect, or backlink account is connected in this workspace, so those panels remain unmeasured.

- **Census:** 134 grouped/published HTML files across 77 canonical URL groups; the checked-in sitemap contains 67 URLs. This is a release-freshness issue, not proof that all 10 missing URLs should be indexed.
- **Metadata:** 17 canonical project descriptions are under 80 characters; 7 rendered project titles are under 25 characters; the fraud pair is the one duplicate title/description collision.
- **Link health:** 559 local link targets were checked. The first pass produced 42 candidates; after excluding known external project routes, 20 candidates remain for human/HTTP classification. They include extensionless relative links in `chatgpt_research.html` and `fraud-predictor.html`, multiple `/ericspencer-site-backup/` links, a case/slug mismatch for `Claude-architect-quiz`, and a malformed `pythonanywhere.com` link. Some other candidates may be valid routes served from external project repositories, so they must not be bulk-rewritten from the local report alone.
- **Page weight:** the largest grouped pages are `projects/iterative-maze-solver.html` (63,735 bytes), `projects.html` (61,120 bytes), and `projects/recursive-maze-solver.html` (44,467 bytes). The maze pages are content-quality/maintenance candidates more than an automatic performance failure.
- **Verification:** `python3 scripts/check_project_pages.py` passes with `62 pages, 62 mirrors, no drift`; `git diff --check` passes.

## Project triage

The labels below are editorial and SEO decisions, not judgments about technical merit. A project can be technically interesting and still be a poor standalone search landing page.

### Tier A — real work that should actively rank

These projects have a strong combination of current evidence: a maintained repository, a live destination or package, a research artifact, a clear audience, or a distinctive technical proposition.

**Research, formal methods, and systems**

- **Resilient** — flagship compiler/language project; link the name to “verified systems programming language” or “safety-critical embedded systems language.”
- **TLA+ Generator / TLA-Prove** — one project family with separate product/demo and research/repository surfaces; plain English to model-checked TLA+ is the clearest intent.
- **ChatTLA+ models and datasets** — include the model, dataset, benchmark, and paper as a connected research family rather than unrelated repositories.
- **tlakit** — package/toolchain client with a package registry destination and strong technical audience.
- **FormaLLM** — formal-specification synthesis evaluation toolkit; label fork/upstream relationship accurately if applicable.
- **TLA-Extraction and the TLA+ benchmark/paper repositories** — research artifacts that should resolve to the paper, dataset, code, and author graph.
- **paper-digest / arxiv-report** — live research-discovery utility with a clear problem statement.

**Tools and distinctive engineering work**

- **AEO Queries** — a Chrome extension for observing the search queries generated by ChatGPT, Claude, and Perplexity; this is strategically aligned with the GEO work itself.
- **Not Hotdog** — distinctive, technically specific browser ML demonstration: an int8 CNN, handwritten JavaScript kernels, zero dependencies, and bit-exact parity.
- **Git Key Guardian** — concrete security utility with an easy-to-understand audience and action.
- **flatten-repo** — VS Code extension for producing LLM-ready repository context; the repository description is already specific.
- **tunes2tube** — macOS utility with a concrete input/output workflow.
- **stemacle** — browser-based stem player with a dedicated product destination.

**FROM AMERICA and product surfaces**

- **Picaius** (`picai`) — real product surface; use Picaius consistently, with “free photo editor for iOS and the web” as the descriptor.
- **StockGenie** (`StockGenie`, `stockgenie-web`) — real App Store product; use “AI stock-pick app for iPhone” as the descriptor and disclose the product status accurately.
- **Daily Task** (`DailyTask`, `DailyTask-web`) — real App Store product, but its portfolio writeup is too thin to represent it.
- **GluCoPilot** (`GluCoPilot`, `cs-glucopilot`, `glucopilot-v2`) — real hackathon/product prototype; target Dexcom/CGM glucose insights, not the bare name.

These are the candidates for the home page’s selected-work section, project-specific SEO copy, strong GitHub-to-site links, and product/research schema. They do not all need identical treatment: an app, a package, a research dataset, and a compiler should have different page templates.

### Tier B — credible secondary work; keep accessible, selectively promote

These are useful proof of skill or credible technical artifacts, but most should not receive the same navigation weight as Tier A:

- **Rubik’s Snake formally verified**, **TLA+ Dexcom G7**, **TLA+ Laptop**, **TLA+ Walk-In Oven**, and **Interactive Microwave TLA** — strong niche/formal-methods demonstrations; keep indexable when the writeup has a clear model, limitation, and artifact link.
- **ITS RAG Bot**, **AI Sign Language Interpreter**, **DexVal**, **Cubed Pack Solver**, **Connect 4**, and **mc-carspot** — substantial technical demonstrations with a defined problem.
- **llmjammer**, **TerminalGPT**, **TDX Window Blocker**, **One Rep Max**, and **usage-badge** — practical utilities; promote only when the README, installation path, and live behavior are current.
- **AI Headshots**, **Serenity**, **BrightBet**, **AuraOS**, **Gesture**, **HealthUp**, **CTA Transit Tracker**, and **MLB Hall of Fame Predictor** — legitimate prototypes, coursework, or hackathon work; label the status prominently and do not imply ongoing products.
- **Recent/index-only work requiring a dedicated evidence pass:** `colibri`, `tof-audit`, `polymarket-whale-tracker`, `chess-coach`, `hardtekk-generator`, `cad-bench-submission`, `HST-Studio`, and other recent items on `projects.html` that do not yet have a canonical writeup. Do not classify these as toys just because they lack a writeup; first collect README, live URL, release, and maintenance evidence.

Tier B pages should get one useful paragraph, one primary artifact link, a status label, and a distinct search intent. They should not crowd the home page or compete with the research entity for “Eric Spencer” queries.

### Tier C — archive, toy, coursework, duplicate, or personal note

These can remain browsable, but they should be grouped under archive/experiments and should usually be removed from selected work. Consider `noindex` when the page has no independent search intent, is stale, is a transcript dump, or duplicates a stronger page.

- **Explicit experiments/toys:** AIs Talking Philosophy, Training an LLM on ASCII, Yeat LLM, Song Recommender, iOS Soundboard, Anagram Solver, Anagram Solver V2, Free Time Calculator, UDP server, and the Skeuomorphic Project Desk.
- **Learning/coursework/archive pages:** Ancestry Tree, Advent of Code 2025, Movie Recommendation, `~/.zshrc` walkthrough, COMP 388 LLM Homework, COMP322 Final Project Reflection, and other course-specific pages whose value is primarily historical.
- **Transcript-heavy/archive pages:** Iterative Maze Solver, Recursive Maze Solver, Researching ChatGPT with ChatGPT, and similar pages where the transcript is longer than the durable project explanation. Preserve a short summary if it is personally meaningful; do not make the transcript the primary SEO asset.
- **Duplicate or overlapping content:** the two Machine Learning Fraud Identifier pages; consolidate or assign a deliberate canonical relationship.
- **Small educational implementations:** Roman numeral converter, Scala hello world/workshop material, and similar starter exercises.

### Separate class — forks, contributions, and inherited work

Do not present a fork or contribution as an independent authored product. Keep GitHub discoverability, but label the relationship:

- **Forks/prototypes:** Claude-of-Duty and ReelForge should say whether they are forks, extensions, or experiments and credit the original author where required.
- **External contributions/forks:** Whisky, BrowserOS, vscode, tlaplus, typescript-go, linguist, Examples, and the other contribution entries should live under a “Contributions & forks” section, not in the core authored-project set.
- **Research forks:** keep serious research value, but use `isBasedOn`, upstream links, and author/contributor wording that matches the repository.

## Targeted issue backlog

Priority meanings: **P0** = fixes the entity/canonical foundation; **P1** = materially improves qualified discovery; **P2** = measurement, automation, or polish.

### P0 — foundation and collision fixes

#### SEO-001 — Establish a selected-work taxonomy and index policy

**Targets:** `projects.html`, `content/project-pages.txt`, project-page generator/data source, GitHub profile README.

**Fix:** Add explicit fields for `tier`, `status`, `ownership`, `audience`, `canonical URL`, `primary artifact`, and `index policy`. Use at least `selected`, `research`, `product`, `secondary`, `archive`, and `contribution`. Keep the all-repositories page, but create a selected layer of roughly 8–12 items.

**Acceptance criteria:** every public repo and organization project is accounted for; every canonical writeup has one tier; selected projects are reachable from the home page within one click; archive/contribution labels are visible to humans; no page is hidden solely because it is hard to classify.

#### SEO-002 — Make `/projects.html` the one project-hub URL

**Targets:** `/projects/`, `projects/index.html`, internal links, sitemap, old mirror paths.

**Fix:** Use `/projects.html` consistently in internal links, canonical tags, and the sitemap. Verify the deployed old `/projects/` path returns a real redirect where the host supports it; otherwise keep the static redirect stub but do not serve a second full project index there. Request recrawl after deployment.

**Acceptance criteria:** one project hub appears in the sitemap; old paths do not contain a second full copy; canonical and redirect targets agree; a crawler sees the same title/description/links regardless of which legacy path it enters.

#### SEO-003 — Consolidate the duplicate fraud writeups

**Targets:** `projects/fraud-predictor-full.html`, `projects/fraud-predictor.html`, corresponding mirror stubs.

**Fix:** Treat `fraud-predictor-full.html` as the likely richer canonical candidate, subject to a final content comparison. Redirect the thinner page to it, or give the two pages genuinely different intents such as overview vs reproducible comparison. Do not leave identical title, description, and intent under two canonicals.

**Acceptance criteria:** one intended URL owns “machine learning fraud identifier”; the other is a redirect or has unique title, description, H1, copy, and canonical; the sitemap lists only the intended indexable URL.

#### GEO-001 — Reconcile the Eric Spencer entity graph

**Targets:** `index.html`, `research.html`, GitHub profile README, AI4FM people page, ORCID, LinkedIn, Hugging Face, FROM AMERICA.

**Fix:** Choose one current description of Eric’s role and reuse it across the major profiles. Add stable author/entity links where they are missing. The homepage’s Person JSON-LD should include the verified ORCID and AI4FM relationship where appropriate; do not put project URLs into `sameAs` unless they are truly same-entity profiles.

**Known consistency checks:** “graduate researcher” vs “formal methods researcher”; Loyola/AI4FM wording; HorneSci and FROM AMERICA roles; ChatTLA+ download counts shown as 13,500+ in one place and lower/older counts elsewhere.

**Acceptance criteria:** a crawler or assistant can answer who Eric is, what he researches, and where the authoritative sources are without choosing between conflicting current-status statements. Volatile counts have a date/source or are removed from evergreen metadata.

#### BRAND-001 — Use disambiguating descriptors for collision-prone names

**Targets:** Picaius, GluCoPilot, Resilient, Daily Task, StockGenie, TLA+ Generator/Runner, ReelForge.

**Fix:** Put the category and ownership context in the title, H1, meta description, first paragraph, Open Graph title, and relevant JSON-LD. Recommended naming patterns:

| Surface | Preferred public phrasing | Primary intent |
| --- | --- | --- |
| Picaius | `Picaius — free photo editor for iOS and the web` | product/editor discovery |
| GluCoPilot | `GluCoPilot — Dexcom/CGM glucose insights prototype by Eric Spencer` | glucose insights / hackathon prototype |
| Resilient | `Resilient — verified systems programming language` | embedded systems / formal verification |
| Daily Task | `Daily Task — wellness tracker for iPhone by Eric Spencer` | habit/wellness tracker app |
| StockGenie | `StockGenie — AI stock-pick app for iPhone` | stock-pick app |
| TLA+ Generator | `TLA+ Generator — plain English to model-checked specifications` | TLA+ generation |
| ReelForge | `ReelForge — captioned-video experiment based on [upstream]` | distinguish fork/experiment |

**Acceptance criteria:** searching each bare brand plus its category produces the intended Eric-owned or Eric-authored surface in the fixed benchmark; Picaius is used consistently instead of PicAI when referring to the owned product.

### P1 — page quality, internal authority, and structured data

#### SEO-004 — Rewrite selected-project titles and descriptions around search intent

**Targets:** Tier A pages and their external destinations.

**Fix:** Replace generic `Project | Eric Spencer` framing with a specific proposition, audience, and artifact. Keep Eric’s name in the title when it helps entity association, but do not use it as the only differentiator. Start with Resilient, TLA+ Generator, tlakit, AEO Queries, Not Hotdog, Git Key Guardian, flatten-repo, tunes2tube, Daily Task, StockGenie, GluCoPilot, and Picaius.

**Acceptance criteria:** each selected page has a unique title, unique description, matching H1, a concrete audience/problem, and one primary next action. Descriptions are long enough to explain the result without padding; title length is checked after rendering, not from an assumed character limit.

#### SEO-005 — Decide page-by-page whether thin content should grow or leave the index

**Targets:** the 17 short-description pages and the thin/archive pages identified in the copy audit; priority examples include `dailytask.html`, `ai-os.html`, `anagram_v2.html`, `brightbet.html`, `dexcom-navbar-macos.html`, `movierec.html`, `serenity.html`, `skeuomorphism.html`, and the maze/transcript pages.

**Fix:** For valuable projects, add an honest case study: problem, what was built, technical decisions, current status, artifact link, limitation, and one screenshot/demo. For archive material, add a concise summary and status label, then consider `noindex` and remove it from the sitemap. Do not fill thin pages with generic AI-written prose.

**Acceptance criteria:** every indexable page answers “what is this, who is it for, what exists now, and where is the proof?” in the first screenful; archive pages are intentionally searchable or intentionally non-indexable.

#### SEO-006 — Give app pages a product-grade landing path

**Targets:** Daily Task, StockGenie, Picaius, GluCoPilot.

**Fix:** Add a product-specific landing block with current status, platform, core features, screenshots with descriptive alt text, support/privacy links where applicable, and the canonical App Store or product URL. The current Daily Task writeup shows screenshots/features but does not give the reader a clear App Store action. StockGenie should similarly connect portfolio, product site, and App Store. GluCoPilot should state clearly that it is a hackathon/prototype and avoid medical-product implications.

**Acceptance criteria:** every real app has one owned landing URL; it links to the store/demo and back to the author/company entity; structured data describes only capabilities and platforms that actually exist.

#### SEO-007 — Add artifact links and reciprocal author links

**Targets:** Tier A and high-value Tier B project pages, GitHub README files, package pages, App Store/product pages, AI4FM/research pages.

**Fix:** Build a deliberate link graph:

```text
Eric Spencer entity
  ├─ research hub ── AI4FM ── paper ── arXiv / DBLP / ORCID
  ├─ selected project ── GitHub ── docs / demo / package / App Store
  └─ FROM AMERICA ── product landing ── App Store / web app
```

Add a canonical portfolio link to the top of each Tier A README, then add the repository/package/store link to the portfolio page. Use descriptive anchors such as “Resilient verified systems language,” not repeated “click here.”

**Acceptance criteria:** no selected project is an orphan; each has an authoritative source and a next action; research artifacts identify the paper, dataset, code, and author without relying on a search result snippet.

#### SEO-008 — Use schema that matches the artifact, not one schema for everything

**Targets:** project-page generator and JSON-LD on Tier A/B pages.

**Fix:** Keep `Article` for genuine narrative writeups. Use the narrowest accurate type for the underlying object: `SoftwareApplication` for real apps, `SoftwareSourceCode` or `TechArticle` for tools, `Dataset` for released datasets, and `ScholarlyArticle` for papers when required fields are available. Connect the narrative page to the underlying artifact with `mainEntity`, `about`, `isPartOf`, `codeRepository`, `downloadUrl`, or `sameAs` only when semantically correct.

**Acceptance criteria:** JSON-LD validates; no project is described as a production application merely because it has an HTML page; research pages expose authors, identifiers, publication dates, and source links that agree with arXiv/DBLP/ORCID.

#### SEO-009 — Remove obsolete `meta keywords` generation

**Targets:** project-page generator, `index.html`, `research.html`, `projects.html`, all generated project pages.

**Fix:** Stop emitting `meta name="keywords"` and remove existing instances during the next metadata regeneration. Keep the words in visible copy, titles, descriptions, headings, and structured data where they are useful.

**Acceptance criteria:** no generated page relies on meta keywords; the audit checks meaningful metadata rather than counting the presence of a deprecated field.

#### SEO-010 — Make the sitemap match the index policy at build time

**Targets:** `scripts/build_sitemap.py`, `sitemap.xml`, archive/noindex metadata.

**Fix:** Keep the existing design principle of one canonical URL per page and excluding `noindex` pages, but run the builder in the release path and fail if the checked-in sitemap is stale. The current code discovers 77 canonical groups while the checked-in sitemap has 67 URLs; reconcile the difference deliberately, including the four external canonical pages.

**Acceptance criteria:** sitemap URL count is explainable from the manifest; redirect mirrors and `noindex` pages are excluded; every listed URL returns the canonical page; every selected page is listed.

#### SEO-011 — Improve legacy mirror and redirect QA

**Targets:** `scripts/check_project_pages.py`, `collapse_mirrors.py`, `content/project-pages.txt`, the four external project surfaces.

**Fix:** Keep one canonical per writeup and preserve useful old URLs, but test redirect behavior, canonical tags, title, and accidental full-copy content. Audit `/Claude-of-Duty/`, `/ddia/`, `/gta-v-gold-checklist/`, and `/hotdog/` for metadata parity because their canonical content is served from other project repositories.

**Acceptance criteria:** legacy paths are recoverable for users, do not compete with canonical pages, and do not silently become stale copies; external project pages either meet the shared metadata contract or are clearly treated as external exceptions.

### P2 — measurement and maintenance

#### SEO-012 — Fix the `seo_tags.py --check` false-positive report

**Targets:** `scripts/seo_tags.py`.

**Fix:** Refactor `apply()` into a pure comparison plus a write operation, or add a dry-run mode that calculates the resulting text and compares it with the original. `--check` should print only pages that would actually change and return nonzero when changes are pending.

**Acceptance criteria:** an unchanged tree reports zero pending changes; a deliberately modified fixture reports exactly the required change; the report distinguishes missing metadata, stale metadata, and already-correct pages.

#### SEO-013 — Add a crawl and rendering QA report

**Targets:** all canonical pages, mirrors, external canonical pages, generated OG images, links and images.

**Fix:** Add a repeatable audit for HTTP status, redirect chain, canonical target, title uniqueness, description length, robots policy, OG/Twitter image existence, JSON-LD validity, broken internal/external links, image alt text, mobile viewport, and content that exists only after JavaScript execution. Run it against the built site and a deployed URL.

**Acceptance criteria:** the report separates errors from warnings; canonical pages, redirects, and archive pages are tested under their intended policy; any exception is recorded in the manifest rather than ignored.

#### SEO-016 — Triage the link-health candidates before changing URLs

**Targets:** `projects/chatgpt_research.html`, `projects/fraud-predictor.html`, `projects/chattla-dataset.html`, `projects/claude-architect-quiz.html`, `projects/resilient.html`, `projects/skeuomorphism.html`, `projects/tunes2tube-mac.html`, `projects.html`, and any route served by an external project repository.

**Fix:** Resolve each candidate through the deployed site before editing it. Repair the clearly local extensionless links with the current canonical `.html` paths; remove or replace stale `/ericspencer-site-backup/` links; correct malformed external URLs; and maintain an explicit allowlist for valid external project routes. Do not interpret a local-file miss as a live 404 until HTTP status and redirect behavior have been checked.

**Acceptance criteria:** every internal link resolves to a current canonical page or intentional redirect; external exceptions have a recorded owner and destination; the audit reports confirmed broken links separately from unresolved-but-valid external routes.

#### GEO-002 — Establish a fixed GEO benchmark instead of fuzzy spot checks

**Targets:** a versioned query set and result log, not production pages initially.

**Fix:** Retain the 50-query scan as baseline `v1`, then maintain a smaller fixed benchmark with query families:

| Family | Example intents |
| --- | --- |
| Identity | `Eric Spencer formal methods`, `Eric Spencer Chicago`, `Eric Spencer AI4FM` |
| Research | `Eric Spencer TLA+`, `ChatTLA+`, `LLM generated TLA+ specifications`, `TLA-Prove` |
| Software | `Resilient programming language`, `tlakit Python TLA+`, `TLA+ Generator` |
| Products | `Picaius photo editor`, `Daily Task wellness tracker`, `StockGenie AI app`, `GluCoPilot Dexcom` |
| Attribution | `who created Resilient`, `who made TLA+ Generator`, `Eric Spencer projects` |

For each run record assistant/search engine, date, location, device, exact query, result/citation, position or presence, whether Eric is attributed correctly, and factual errors. Run the same prompts across the assistants that matter instead of treating one web-search tool as “AI ranking.”

**Acceptance criteria:** the benchmark can show improvement or regression over time; every observed result is labeled as position, presence, or citation—not a fabricated universal rank.

#### SEO-014 — Connect actual search and product measurement

**Targets:** Google Search Console, Bing Webmaster Tools, App Store Connect, product analytics, and the benchmark log.

**Fix:** Use Search Console/Bing for query, impression, position, and CTR data. Use App Store Connect for Daily Task and StockGenie impressions/product-page views/conversion. Track product-site referrals and GitHub/package clicks separately from rankings.

**Acceptance criteria:** future reports contain real position/CTR data for web pages and real impression/conversion data for apps; “visibility in the tool” is reported as a separate metric.

#### SEO-015 — Add a monthly entity/content maintenance check

**Targets:** homepage, research page, selected project metadata, GitHub profile, AI4FM, product sites, sitemap.

**Fix:** Check for role/status drift, dead links, stale counts, renamed products, changed repository ownership, broken App Store links, and new index-only projects. Require a status label (`shipped`, `maintained`, `prototype`, `archived`, `fork`, or `coursework`) before a new project enters selected work.

**Acceptance criteria:** an update to one identity fact or product name produces a visible list of affected surfaces; stale project pages do not remain silently promoted.

## First implementation order

When implementation begins, use this order:

1. `SEO-001`, `SEO-002`, `SEO-003`, and `SEO-012`: taxonomy, canonical project hub, sitemap truth, and trustworthy audits.
2. `SEO-003` duplicate consolidation plus `GEO-001` and `BRAND-001`: remove the largest identity and brand ambiguities.
3. `SEO-004`, `SEO-005`, and `SEO-006`: rewrite and expand only the selected pages and real product surfaces.
4. `SEO-007`, `SEO-008`, `SEO-009`, and `SEO-011`: strengthen the cross-domain graph and make metadata/schema semantically accurate.
5. `SEO-013`, `GEO-002`, `SEO-014`, and `SEO-015`: turn the work into a measurable, maintainable system.

## Out of scope for this pass

- No production HTML, metadata, redirects, schema, sitemap, GitHub README, App Store listing, or external product page was changed.
- No claim is made about exact Google rankings from the 50-query scan.
- No archive page is being deleted. The proposed `noindex` decisions are reversible and should be confirmed against future recruiting, research, or personal-history goals before implementation.
- No project was labeled a “toy” solely because it lacks a live URL or recent commit; the next evidence pass should resolve ambiguous/index-only projects before changing their visibility policy.

## Source files and references

- [`content/project-pages.txt`](../content/project-pages.txt) — canonical/mirror map.
- [`projects.html`](../projects.html) — current all-projects index and categories.
- [`index.html`](../index.html) — current entity copy, links, and homepage JSON-LD.
- [`research.html`](../research.html) — current research metadata and artifact links.
- [`scripts/build_sitemap.py`](../scripts/build_sitemap.py) — sitemap generation policy.
- [`scripts/build_og_images.py`](../scripts/build_og_images.py) — published-page discovery and canonical grouping.
- [`scripts/check_project_pages.py`](../scripts/check_project_pages.py) — mirror/canonical consistency check.
- [`scripts/seo_tags.py`](../scripts/seo_tags.py) — shared head metadata hygiene and the pending check-mode fix.
- [`editor/audit.md`](../editor/audit.md) — existing local project-copy audit used as supporting evidence; preserve its current untracked state.
