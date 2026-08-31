#!/usr/bin/env python3
"""
build.py — reads content/*.txt and content/blog/*.md, writes index.html.
Run by GitHub Actions on every push; do not edit index.html directly.
"""

from pathlib import Path
import html as htmllib

from build_blog import load_posts

ROOT = Path(__file__).parent.parent
CONTENT = ROOT / "content"

# ── helpers ──────────────────────────────────────────────────────────────────

def lines(filename):
    """Yield non-empty, non-comment lines from a content .txt file."""
    path = CONTENT / filename
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            yield line

def parse(line, n):
    """Split a pipe-delimited line into exactly n fields (padding with '')."""
    parts = line.split("|", n - 1)
    return parts + [""] * (n - len(parts))

# ── section builders ──────────────────────────────────────────────────────────

def build_news():
    rows = []
    for line in lines("news.txt"):
        date, text, url, label = parse(line, 4)
        pill = f' <a href="{url}" target="_blank" rel="noopener" class="pill">{label}</a>' if url else ""
        rows.append(f'<div class="news"><span class="d">{date}</span><span class="t">{text}{pill}</span></div>')
    return "\n".join(rows)

def build_about():
    text = (CONTENT / "about.txt").read_text(encoding="utf-8")
    paras = [p.strip() for p in text.split("\n\n") if p.strip() and not p.strip().startswith("#")]
    return "\n".join(f'<p class="lead">{p}</p>' if i == 0 else f"<p>{p}</p>" for i, p in enumerate(paras))

def build_selected():
    rows = []
    for line in lines("selected.txt"):
        name, url, desc = parse(line, 3)
        rows.append(f'<div class="proj"><a class="nm" href="{url}">{name}</a><span class="dt"></span><span class="ds">{desc}</span></div>')
    return "\n".join(rows)

def build_blog():
    """The whole Blog section, or nothing at all when nothing is published.

    An empty section advertised a blog and then showed "No posts yet.", so the
    heading and the "all posts" link are part of what gets gated, not just the
    list. Publishing any post in content/blog/ brings the section back.
    """
    posts = load_posts()
    if not posts:
        return ""
    rows = []
    for post in posts:
        rows.append(
            f'<div class="post-row">'
            f'<span class="post-d">{post.date}</span>'
            f'<div class="post-body">'
            f'<div class="post-title"><a href="/blog/{post.slug}.html">{htmllib.escape(post.title)}</a></div>'
            f'<p class="post-desc">{htmllib.escape(post.description)}</p>'
            f'</div></div>'
        )
    return (
        '<h2 id="blog">Blog</h2>\n'
        + "\n".join(rows)
        + '\n<p class="small" style="margin-top:6px"><a href="/blog/">&rarr; all posts</a></p>'
    )

def build_experience():
    rows = []
    for line in lines("experience.txt"):
        role, org, org_url, start, end, logo, note = parse(line, 7)
        end_str = "present" if end.lower() == "present" else end
        date_str = f"{start} &mdash; {end_str}"
        if logo:
            logo_html = (
                f'<div class="cv-logo">'
                f'<img src="/assets/logos/{logo}" alt="{htmllib.escape(org)}" '
                f'width="36" height="36" style="border-radius:6px;object-fit:contain;background:#fff">'
                f'</div>'
            )
        else:
            words = org.split()
            if len(words) > 1:
                initials = "".join(w[0] for w in words[:2]).upper()
            else:
                # Single-word orgs used to render one lonely letter. Prefer the
                # word's own capitals ("HorneSci" -> "HS"), else its first two.
                caps = [c for c in words[0] if c.isupper()]
                initials = ("".join(caps[:2]) if len(caps) > 1 else words[0][:2]).upper()
            logo_html = (
                f'<div class="cv-logo">'
                f'<svg width="36" height="36" viewBox="0 0 36 36"><rect width="36" height="36" rx="6" fill="#ddd"/>'
                f'<text x="18" y="24" font-family="Plus Jakarta Sans,sans-serif" font-size="11" font-weight="700" fill="#555" text-anchor="middle">{initials}</text></svg>'
                f'</div>'
            )
        org_link = f'<a href="{org_url}" target="_blank" rel="noopener">{org}</a>' if org_url else org
        note_html = f'<div class="cv-note">{note}</div>' if note else ""
        rows.append(
            f'<div class="cv-row">'
            f'{logo_html}'
            f'<div class="cv-body">'
            f'<div class="cv-role">{role}</div>'
            f'<div class="cv-org">{org_link}</div>'
            f'<div class="cv-when">{date_str}</div>'
            f'{note_html}'
            f'</div></div>'
        )
    return "\n".join(rows)

# ── full page template ────────────────────────────────────────────────────────

def build_page(news, about, selected, blog, experience):
    return f"""<!doctype html><html lang="en"><head>
<meta charset="utf-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Eric Spencer — Formal Methods &amp; LLM Researcher, Chicago</title>
<meta name="description" content="Formal methods and LLM researcher at Loyola University Chicago (AI4FM), founder of FROM AMERICA LLC. ChatTLA+ models, TLA+ spec generation, the Resilient compiler.">
<meta name="author" content="Eric Spencer">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
<link rel="canonical" href="https://ericspencer.us/">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta name="theme-color" content="#faf7f2">
<meta property="og:type" content="profile">
<meta property="og:title" content="Eric Spencer — Formal Methods &amp; LLM Researcher, Chicago">
<meta property="og:description" content="Formal methods and LLM researcher at Loyola University Chicago (AI4FM), founder of FROM AMERICA LLC.">
<meta property="og:url" content="https://ericspencer.us/">
<meta property="og:site_name" content="Eric Spencer">
<meta property="og:image" content="https://ericspencer.us/assets/og/home.jpg">
<meta property="og:image:type" content="image/jpeg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Eric Spencer &mdash; ericspencer.us">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Eric Spencer — Formal Methods &amp; LLM Researcher, Chicago">
<meta name="twitter:description" content="Formal methods and LLM researcher at Loyola University Chicago (AI4FM), founder of FROM AMERICA LLC.">
<meta name="twitter:image" content="https://ericspencer.us/assets/og/home.jpg">
<script type="application/ld+json">
{{"@context":"https://schema.org","@graph":[
{{"@type":"WebSite","@id":"https://ericspencer.us/#site","url":"https://ericspencer.us/","name":"Eric Spencer","inLanguage":"en-US","publisher":{{"@id":"https://ericspencer.us/#eric"}}}},
{{"@type":"ProfilePage","@id":"https://ericspencer.us/#page","url":"https://ericspencer.us/","name":"Eric Spencer — Formal Methods & LLM Researcher, Chicago","isPartOf":{{"@id":"https://ericspencer.us/#site"}},"primaryImageOfPage":{{"@id":"https://ericspencer.us/#pfp"}},"mainEntity":{{"@id":"https://ericspencer.us/#eric"}}}},
{{"@type":"ImageObject","@id":"https://ericspencer.us/#pfp","url":"https://ericspencer.us/assets/img/eric-spencer.jpg","contentUrl":"https://ericspencer.us/assets/img/eric-spencer.jpg","width":460,"height":460,"caption":"Eric Spencer"}},
{{"@type":"Person","@id":"https://ericspencer.us/#eric","name":"Eric Spencer","alternateName":"EricSpencer00","url":"https://ericspencer.us/","image":{{"@id":"https://ericspencer.us/#pfp"}},"sameAs":["https://github.com/EricSpencer00","https://huggingface.co/EricSpencer00","https://www.linkedin.com/in/ericspencer00/"],"owns":[{{"@id":"https://sideswing.tech/#app"}},{{"@id":"https://picai.us/#app"}},{{"@id":"https://vocal.best/#app"}},{{"@id":"https://stemacle.com/#app"}},{{"@id":"https://stockgenie.app/#app"}},{{"@id":"https://ipaidforthisshirt.com/#site"}},{{"@id":"https://famousmoji.com/#site"}}],"jobTitle":"Founder | AI researcher","knowsAbout":["Formal methods","TLA+","Large language models","Model checking","Systems programming","Compilers"],"affiliation":{{"@type":"CollegeOrUniversity","name":"Loyola University Chicago","url":"https://luc.edu"}},"worksFor":[{{"@type":"Organization","name":"HorneSci","url":"https://hornesci.github.io"}},{{"@type":"Organization","name":"FROM AMERICA LLC","url":"https://fromamerica-llc.com"}}],"address":{{"@type":"PostalAddress","addressLocality":"Chicago","addressRegion":"IL","addressCountry":"US"}},"email":"eric@ericspencer.us"}},
{{"@type":"MobileApplication","@id":"https://sideswing.tech/#app","name":"SideSwing","url":"https://sideswing.tech/","applicationCategory":"GameApplication","operatingSystem":"iOS","author":{{"@id":"https://ericspencer.us/#eric"}}}},
{{"@type":"WebApplication","@id":"https://picai.us/#app","name":"Picaius","url":"https://picai.us/","applicationCategory":"MultimediaApplication","operatingSystem":"Web, iOS","author":{{"@id":"https://ericspencer.us/#eric"}}}},
{{"@type":"MobileApplication","@id":"https://vocal.best/#app","name":"VoCal","url":"https://vocal.best/","applicationCategory":"HealthApplication","operatingSystem":"iOS","author":{{"@id":"https://ericspencer.us/#eric"}}}},
{{"@type":"SoftwareApplication","@id":"https://stemacle.com/#app","name":"Stemacle","url":"https://stemacle.com/","applicationCategory":"MultimediaApplication","operatingSystem":"macOS, Web","author":{{"@id":"https://ericspencer.us/#eric"}}}},
{{"@type":"MobileApplication","@id":"https://stockgenie.app/#app","name":"StockGenie","url":"https://stockgenie.app/","applicationCategory":"FinanceApplication","operatingSystem":"iOS","author":{{"@id":"https://ericspencer.us/#eric"}}}},
{{"@type":"WebSite","@id":"https://ipaidforthisshirt.com/#site","name":"I Paid For This Shirt","url":"https://ipaidforthisshirt.com/","author":{{"@id":"https://ericspencer.us/#eric"}}}},
{{"@type":"WebSite","@id":"https://famousmoji.com/#site","name":"Famous Moji","url":"https://famousmoji.com/","author":{{"@id":"https://ericspencer.us/#eric"}}}}
]}}
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap">
<style>
:root{{--paper:#faf7f3;--paper:oklch(0.978 0.006 80);--ink:#080401;--ink:oklch(0.11 0.015 60);--accent:#5f000b;--accent:oklch(0.30 0.13 22);--dim:#6d6863;--dim:oklch(0.52 0.01 70);--rule:#d6d4d1;--rule:oklch(0.87 0.005 80)}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}
body{{margin:0;background:var(--paper);color:var(--ink);font-family:"Plus Jakarta Sans",-apple-system,BlinkMacSystemFont,sans-serif;font-size:16px;line-height:1.7;-webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale}}
.wrap{{max-width:720px;margin:0 auto;padding:56px 24px 100px}}
.name-hero{{font-size:clamp(34px,5.5vw,52px);font-weight:700;letter-spacing:-0.025em;line-height:1.05;margin:0 0 10px}}
nav.top{{font-family:"Plus Jakarta Sans",sans-serif;font-size:14px;font-weight:500;color:var(--dim);margin:16px 0 0}}
nav.top a{{color:inherit;text-decoration:none;border:0;padding:0 2px}}
nav.top a:hover{{color:var(--ink)}}
nav.top a.active{{color:var(--ink);font-weight:600}}
hr{{border:0;border-top:1px solid var(--rule);margin:28px 0}}
a{{color:var(--accent);text-decoration:none;border:0}}
a:hover{{text-decoration:underline;text-decoration-thickness:1px;text-underline-offset:3px}}
code,kbd,.mono,pre{{font-family:"IBM Plex Mono",ui-monospace,monospace}}
h2{{font-family:"Plus Jakarta Sans",sans-serif;font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:0.07em;color:var(--dim);margin:48px 0 14px;scroll-margin-top:20px}}
h2 .pill{{font-family:"IBM Plex Mono",monospace;font-size:10px;text-transform:none;letter-spacing:0;font-weight:400;vertical-align:middle;margin-left:6px}}
h3{{font-size:18px;font-weight:600;letter-spacing:-0.01em;margin:20px 0 4px}}
p{{margin:12px 0}}
.lead{{font-size:17px;line-height:1.65;letter-spacing:-0.01em}}
.proj{{font-family:"Plus Jakarta Sans",sans-serif;font-size:14px;line-height:1.8;display:flex;gap:10px;align-items:baseline;padding:2px 0;white-space:nowrap;overflow:hidden}}
.proj a.nm{{flex:0 0 auto;font-weight:600;color:var(--ink);border:0}}
.proj a.nm:hover{{color:var(--accent);text-decoration:none}}
.proj .dt{{flex:1;border-bottom:1px dotted var(--rule);transform:translateY(-3px);min-width:14px}}
.proj .ds{{flex:0 1 auto;color:var(--dim);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:13px}}
.news{{font-family:"Plus Jakarta Sans",sans-serif;font-size:14px;display:flex;gap:16px;align-items:baseline;padding:4px 0}}
.news .d{{flex:0 0 88px;font-family:"IBM Plex Mono",monospace;font-size:12px;color:var(--dim);font-variant-numeric:tabular-nums}}
.news .t{{flex:1;font-size:15px;color:var(--ink)}}
.pill{{font-family:"IBM Plex Mono",monospace;font-size:11px;color:var(--dim)}}
.linkrow{{font-family:"Plus Jakarta Sans",sans-serif;font-size:14px;font-weight:500;margin:12px 0 0}}
.linkrow a{{margin-right:6px;color:var(--dim);border:0}}
.linkrow a:hover{{color:var(--ink);text-decoration:none}}
.post-row{{display:flex;gap:20px;align-items:baseline;padding:10px 0;border-bottom:1px solid var(--rule)}}
.post-row:last-child{{border-bottom:0}}
.post-d{{flex:0 0 88px;font-family:"IBM Plex Mono",monospace;font-size:12px;color:var(--dim);font-variant-numeric:tabular-nums}}
.post-body{{flex:1}}
.post-title{{font-size:16px;font-weight:600;letter-spacing:-0.01em;margin:0 0 2px}}
.post-title a{{color:var(--ink);border:0}}
.post-title a:hover{{color:var(--accent);text-decoration:none}}
.post-desc{{font-size:14px;color:var(--dim);margin:0}}
.dim-note{{font-size:14px;color:var(--dim);font-style:italic}}
.cv-row{{display:flex;gap:14px;align-items:flex-start;margin:14px 0}}
.cv-logo{{flex:0 0 36px}}
.cv-body{{flex:1}}
.cv-role{{font-size:15px;font-weight:600;letter-spacing:-0.01em;margin:0 0 2px}}
.cv-org{{font-size:14px;color:var(--ink)}}
.cv-when{{font-family:"IBM Plex Mono",monospace;font-size:12px;color:var(--dim);margin:2px 0 0}}
.cv-note{{font-size:14px;color:var(--dim);margin:3px 0 0}}
.small{{font-size:13px;color:var(--dim)}}
code{{background:#edebe7;background:oklch(0.94 0.005 80);padding:1px 5px;border-radius:4px;font-size:13px}}
.tag{{display:inline-block;font-family:"IBM Plex Mono",monospace;font-size:10px;border:1px solid var(--rule);border-radius:3px;padding:0 5px;color:var(--dim);background:transparent;margin-left:4px}}
footer{{margin-top:60px;border-top:1px solid var(--rule);padding-top:16px;font-family:"Plus Jakarta Sans",sans-serif;font-size:13px;color:var(--dim);display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px}}
/* GitHub repos dynamic section */
#gh-repos .gh-cat{{margin:48px 0 0}}
#gh-repos .gh-cat h2{{margin-bottom:14px}}
#gh-repos .repo-row{{font-family:"Plus Jakarta Sans",sans-serif;font-size:14px;line-height:1.8;display:flex;gap:10px;align-items:baseline;padding:2px 0;white-space:nowrap;overflow:hidden}}
#gh-repos .repo-row a{{flex:0 0 auto;font-weight:600;color:var(--ink);border:0;text-decoration:none}}
#gh-repos .repo-row a:hover{{color:var(--accent)}}
#gh-repos .repo-row .dt{{flex:1;border-bottom:1px dotted var(--rule);transform:translateY(-3px);min-width:14px}}
#gh-repos .repo-row .ds{{flex:0 1 auto;color:var(--dim);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:13px}}
#gh-repos .repo-row .stars{{flex:0 0 auto;font-family:"IBM Plex Mono",monospace;font-size:11px;color:var(--dim);opacity:0.65}}
#gh-repos .loading{{font-size:14px;color:var(--dim);font-style:italic;margin:8px 0}}
/* Hugging Face section reuses the repo-row layout */
#hf-list .gh-cat{{margin:48px 0 0}}
#hf-list .gh-cat h2{{margin-bottom:14px}}
#hf-list .repo-row{{font-family:"Plus Jakarta Sans",sans-serif;font-size:14px;line-height:1.8;display:flex;gap:10px;align-items:baseline;padding:2px 0;white-space:nowrap;overflow:hidden}}
#hf-list .repo-row a{{flex:0 0 auto;font-weight:600;color:var(--ink);border:0;text-decoration:none}}
#hf-list .repo-row a:hover{{color:var(--accent)}}
#hf-list .repo-row .dt{{flex:1;border-bottom:1px dotted var(--rule);transform:translateY(-3px);min-width:14px}}
#hf-list .repo-row .ds{{flex:0 1 auto;color:var(--dim);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:13px}}
#hf-list .repo-row .stars{{flex:0 0 auto;font-family:"IBM Plex Mono",monospace;font-size:11px;color:var(--dim);opacity:0.65}}
#hf-list .loading{{font-size:14px;color:var(--dim);font-style:italic;margin:8px 0}}
/* "Show more" disclosure: rows past the third are hidden until asked for */
.gh-rest[hidden]{{display:none}}
.gh-more{{font-family:"Plus Jakarta Sans",sans-serif;font-size:13px;color:var(--dim);background:none;border:0;border-bottom:1px dotted var(--rule);padding:2px 0;margin-top:6px;cursor:pointer}}
.gh-more:hover{{color:var(--accent);border-bottom-color:var(--accent)}}
.cat-note{{font-size:14px;color:var(--dim);margin:-4px 0 10px;font-variant-numeric:tabular-nums}}
.cat-note b{{color:var(--ink);font-weight:600}}
@media(max-width:560px){{.wrap{{padding:36px 18px 80px}}.proj .dt,.proj .ds{{display:none}}.post-d{{display:none}}#gh-repos .repo-row .dt,#gh-repos .repo-row .ds{{display:none}}#hf-list .repo-row .dt,#hf-list .repo-row .ds{{display:none}}}}
</style></head><body><div class="wrap">
<h1 class="name-hero">Eric Spencer</h1>
<nav class="top"><a href="/" class="active">index</a> &nbsp;&middot;&nbsp; <a href="/research.html">research</a> &nbsp;&middot;&nbsp; <a href="/projects.html">projects</a> &nbsp;&middot;&nbsp; <a href="/blog/">blog</a> &nbsp;&middot;&nbsp; <a href="/cv/">cv</a></nav>
<hr>

<h2 id="news">News</h2>
{news}

<h2 id="about">About</h2>
{about}
<div class="linkrow">
&#9656; <a href="https://github.com/EricSpencer00" target="_blank" rel="me noopener">github</a> &middot;
<a href="https://huggingface.co/EricSpencer00" target="_blank" rel="me noopener">huggingface</a> &middot;
<a href="https://www.linkedin.com/in/ericspencer00/" target="_blank" rel="me noopener">linkedin</a> &middot;
<a href="https://ai4fm.cs.luc.edu/" target="_blank" rel="noopener">ai4fm.cs.luc.edu</a> &middot;
<a href="/assets/resume.pdf" target="_blank" rel="noopener">r&eacute;sum&eacute;</a> &middot;
<a href="mailto:eric@ericspencer.us">email</a>
</div>

<h2 id="selected">Selected Work</h2>
{selected}

{blog}

<div id="gh-repos">
<p class="loading" id="gh-loading">Loading repos&hellip;</p>
</div>

<div id="hf-list">
<p class="loading" id="hf-loading">Loading Hugging Face models&hellip;</p>
</div>

<!-- The two lists above are built from the GitHub and Hugging Face APIs at view
     time. Crawlers that do not run scripts would otherwise see nothing here, so
     the headline artifacts are also stated in plain HTML. -->
<noscript>
<h2>Open Source</h2>
<div class="proj"><a class="nm" href="https://huggingface.co/EricSpencer00/chattla-20b" target="_blank" rel="noopener">chattla-20b</a><span class="dt"></span><span class="ds">gpt-oss-20b fine-tuned to write verifiable TLA+ specifications.</span></div>
<div class="proj"><a class="nm" href="https://huggingface.co/EricSpencer00" target="_blank" rel="noopener">huggingface.co/EricSpencer00</a><span class="dt"></span><span class="ds">The ChatTLA+ models and the datasets they were trained on.</span></div>
<div class="proj"><a class="nm" href="https://github.com/EricSpencer00" target="_blank" rel="noopener">github.com/EricSpencer00</a><span class="dt"></span><span class="ds">Formal methods, LLM tooling, compilers, macOS and iOS apps.</span></div>
<div class="proj"><a class="nm" href="/projects.html">All projects</a><span class="dt"></span><span class="ds">Every public repository and writeup, by category.</span></div>
</noscript>

<h2 id="cv">Experience</h2>
{experience}

<footer>
<span>&copy; 2026 Eric Spencer &middot; Chicago, IL</span>
<span><a href="mailto:eric@ericspencer.us">eric@ericspencer.us</a></span>
</footer>
</div>

<script>
(function() {{
  // GitHub org/user repos to fetch
  const SOURCES = [
    {{ type: 'user', name: 'EricSpencer00', label: null }},
    {{ type: 'org',  name: 'LUC-AI4FM',    label: 'LUC-AI4FM' }},
  ];

  // Repos to skip entirely (noise, profile READMEs, this site's own repo)
  const SKIP = new Set([
    'EricSpencer00.github.io', 'dev.EricSpencer00.github.io',
    'EricSpencer00',          // profile README
    'Hello-World',            // first-ever GitHub repo
    'scala-hello-world',      // trivial starter
    'echotest-scala',         // trivial starter
    'shapes-oo-scala',        // trivial starter
    'copilot-cli-test',       // sandbox, no content
    'argon-design-system-angular', // upstream fork, unrelated
  ]);

  // Prefer org-canonical repos over personal forks of the same name.
  // After fetching, we deduplicate by repo name keeping the org version.
  function dedup(all) {{
    const byName = new Map();
    for (const r of all) {{
      const key = r.name.toLowerCase();
      if (!byName.has(key)) {{ byName.set(key, r); continue; }}
      const existing = byName.get(key);
      // prefer non-fork over fork; prefer org over personal
      const existingIsOrg = existing._source != null;
      const rIsOrg = r._source != null;
      if (!existing.fork && r.fork) continue;          // keep existing non-fork
      if (existing.fork && !r.fork) {{ byName.set(key, r); continue; }} // swap to non-fork
      if (rIsOrg && !existingIsOrg) {{ byName.set(key, r); }}          // prefer org
    }}
    return [...byName.values()];
  }}

  // AI topics that are specific enough to override the name-based check
  const AI_TOPICS = new Set(['llm','machine-learning','deep-learning','artificial-intelligence',
    'natural-language-processing','nlp','reinforcement-learning','pytorch','tensorflow',
    'huggingface','fine-tuning','rag','transformers','gpt','openai']);

  // Categories: [ [heading, match_fn], ... ]
  // Repos matched earlier are excluded from later categories.
  const CATEGORIES = [
    ['Formal Methods & Verification', r =>
      /tla|formal|coq|rocq|alloy|resilient|goldbach|fm-cb|TLAJVM|ralph-tla|FormaLLM/i.test(r.name) ||
      (r.topics||[]).some(t => /^(tla|tla-plus|formal-methods|coq|alloy|model-checking)$/i.test(t))
    ],
    ['AI, LLMs & Machine Learning', r =>
      /\b(llm|gpt|ollama|picai|sign-language|rvc-|reelforge|rl-agent|als-sig|yeat-llm|ITS-RAG|llmjammer|terminalgpt|ai-os|ascii-llm|glucopilot|comp388-llm|connect-4)\b/i.test(r.name) ||
      (r.topics||[]).some(t => AI_TOPICS.has(t.toLowerCase()))
    ],
    ['macOS, iOS & Desktop', r =>
      /mac|ios|swift|tunes2tube|dexcom|ChessStats|youtube-dl|soundboard|apple-music|ReserveLibrary|tdx|DexVal|T-square|ripcord/i.test(r.name)
    ],
    ['Systems, Languages & Tools', r =>
      /UDP-server|itch-parser|xoroshiro|mc-carspot|palindrome|grade-public|roman-numeral|etl-demo|fg-scrape|EmailExtract|scala|gitkey|flatten-repo|notify-agent|reverse-xoro|auto-decode|tlakit/i.test(r.name)
    ],
    ['Web & Front-End', r =>
      /github[.]io$|[-]web$|front|fb-clone|design-skill|caterpillar|gcf-de|margaux|DailyTask|bio-ops|sneaker-run|slot-machine|spa-web|cone-site|uzz|pitch|archaic-radio|stockgenie-web|FreeLock-web|splithound-web|chambr-web|from-america[.]|webpage/i.test(r.name) ||
      (r.homepage||'').includes('github.io')
    ],
    ['Hackathons & Coursework', r =>
      /hack|Serenity|LoyolaHACK|comp[0-9]|COMP[0-9]|cs50|csapp|HealthUp|AoC|march-mad|MovieRec|BlackJack|AnagramSolver|Chat(?!TLA)|BrightBet|claude-architect-exam/i.test(r.name)
    ],
  ];

  // The first three rows of each category are the ones worth leading with, so
  // they are named here rather than left to whatever GitHub sorted most recent.
  // `repo` pins an existing repo (optionally relabelled); `url` alone adds a
  // site that has no public repo behind it. Anything not listed keeps its
  // normal position after the pins, hidden behind "Show more".
  const PINNED = {{
    'Formal Methods & Verification': [
      {{ repo: 'ralph-tla' }},
      {{ repo: 'interactive-microwave-tla' }},
      {{ repo: 'FormaLLM' }},
    ],
    'AI, LLMs & Machine Learning': [
      {{ repo: 'TerminalGPT' }},
      {{ repo: 'yeat-llm' }},
      {{ repo: 'usage-badge' }},
    ],
    // T-square sits fourth on purpose: visible only after "Show more".
    'macOS, iOS & Desktop': [
      {{ repo: 'ripcord' }},
      {{ repo: 'tunes2tube-mac' }},
      {{ repo: 'iOS-soundboard' }},
      {{ repo: 'T-square' }},
    ],
    'Systems, Languages & Tools': [
      {{ repo: 'tlakit' }},
      {{ repo: 'reverse-xoroshiro128plusplus' }},
      {{ repo: 'grade-public-commits' }},
    ],
    'Web & Front-End': [
      {{ name: 'fromamerica-llc.com', url: 'https://fromamerica-llc.com',
        desc: 'FROM AMERICA LLC: independent software studio.' }},
      {{ repo: 'gcf-de', url: 'https://ericspencer.us/gcf-de/' }},
      {{ name: 'stockgenie.app', url: 'https://stockgenie.app',
        desc: 'Daily AI stock pick, free tier plus options.' }},
    ],
    'Hackathons & Coursework': [
      {{ name: 'sideswing.tech', url: 'https://sideswing.tech',
        desc: 'Phone-as-club golf swing tracker.' }},
      {{ repo: 'VoCal', name: 'vocal.best', url: 'https://vocal.best' }},
      {{ name: 'brightbet.tech', url: 'https://brightbet.tech',
        desc: 'Sports betting model and dashboard.' }},
    ],
    'Other': [
      {{ repo: 'ddia' }},
      {{ repo: 'Claude-architect-quiz' }},
      {{ repo: 'pm-whale-tracker' }},
    ],
  }};

  // The account is past 100 repos, so a single page silently drops the tail
  // (and with it any pinned repo that happens to live there). Walk the pages.
  const PER_PAGE = 100;
  const MAX_PAGES = 5;

  async function fetchAll(source) {{
    const root = source.type === 'user'
      ? `https://api.github.com/users/${{source.name}}/repos?type=all&`
      : `https://api.github.com/orgs/${{source.name}}/repos?`;
    const out = [];
    for (let page = 1; page <= MAX_PAGES; page++) {{
      const res = await fetch(
        `${{root}}per_page=${{PER_PAGE}}&sort=updated&page=${{page}}`,
        {{ headers: {{ Accept: 'application/vnd.github+json' }} }});
      if (!res.ok) break;
      const data = await res.json();
      if (!Array.isArray(data) || !data.length) break;
      out.push(...data.map(r => ({{ ...r, _source: source.label }})));
      if (data.length < PER_PAGE) break;
    }}
    return out;
  }}

  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g,
    c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c]));

  // One row, whether it came from a repo, a pin, or Hugging Face.
  function row({{ url, name, desc, count, tags }}) {{
    const tagHtml = (tags || []).map(t => `<span class="tag">${{esc(t)}}</span>`).join('');
    const countHtml = count ? `<span class="stars">${{count}}</span>` : '';
    return `<div class="repo-row">
      <a href="${{esc(url)}}" target="_blank" rel="noopener">${{esc(name)}}</a>
      <span class="dt"></span>
      <span class="ds">${{esc(desc)}}${{tagHtml}}</span>
      ${{countHtml}}
    </div>`;
  }}

  // ── attention, not applause ────────────────────────────────────────────────
  // Stars are a lifetime total that never decays, so a repo starred once years
  // ago outranked everything anyone is actually reading -- and only 17 repos
  // here have any stars at all, against 54 with real traffic. Views come from
  // /traffic/views, which needs push access, so a nightly job publishes them to
  // signals.json and this just reads the file. If the file is missing or stale
  // the rows fall back to stars rather than losing their count entirely.
  let SIGNALS = {{}};

  async function loadSignals() {{
    try {{
      const res = await fetch('/assets/data/signals.json', {{ cache: 'no-cache' }});
      if (!res.ok) return;
      const data = await res.json();
      SIGNALS = data.repos || {{}};
    }} catch (e) {{ /* stars remain the fallback */ }}
  }}

  const numf = n => n.toLocaleString('en-US');

  function signalFor(repo) {{
    const s = SIGNALS[repo.full_name] || SIGNALS[`${{repo.owner && repo.owner.login}}/${{repo.name}}`];
    // Unique visitors is the number that survives scrutiny: raw views count a
    // reload, and one person refreshing their own repo should not read as reach.
    if (s && s.d90u > 0) {{
      const total = `&#8599; ${{numf(s.d90u)}} reader${{s.d90u === 1 ? '' : 's'}}`;
      // The 14-day figure is only worth a second number once there is older
      // history to contrast it with; until then it just repeats the total.
      const recent = s.d14u > 0 && s.d14u < s.d90u ? `${{numf(s.d14u)}} this fortnight` : '';
      return [total, recent].filter(Boolean).join(' &middot; ');
    }}
    return repo.stargazers_count > 0 ? `&#9733; ${{repo.stargazers_count}}` : '';
  }}

  function repoRow(repo, override) {{
    const o = override || {{}};
    return row({{
      url: o.url || repo.homepage || repo.html_url,
      name: o.name || repo.name,
      desc: o.desc || repo.description || '',
      count: signalFor(repo),
      tags: [repo.fork ? 'fork' : null, repo._source].filter(Boolean),
    }});
  }}

  // A category renders its first three rows, then tucks the rest behind a
  // button. Categories of three or fewer get no button at all.
  const VISIBLE = 3;
  let catSeq = 0;

  function renderCat(heading, rows, note) {{
    if (!rows.length) return '';
    const id = `gh-rest-${{++catSeq}}`;
    const head = rows.slice(0, VISIBLE).join('\\n');
    const rest = rows.slice(VISIBLE);
    const restHtml = rest.length
      ? `<div class="gh-rest" id="${{id}}" hidden>${{rest.join('\\n')}}</div>
         <button class="gh-more" type="button" aria-expanded="false" aria-controls="${{id}}"
                 data-count="${{rest.length}}">Show ${{rest.length}} more</button>`
      : '';
    const noteHtml = note ? `<p class="cat-note">${{note}}</p>` : '';
    return `<div class="gh-cat">
      <h2>${{esc(heading)}} <span class="pill">(${{rows.length}})</span></h2>
      ${{noteHtml}}
      ${{head}}
      ${{restHtml}}
    </div>`;
  }}

  function wireDisclosures(container) {{
    container.querySelectorAll('.gh-more').forEach(btn => {{
      btn.addEventListener('click', () => {{
        const panel = document.getElementById(btn.getAttribute('aria-controls'));
        const open = !panel.hidden;
        panel.hidden = open;
        btn.setAttribute('aria-expanded', String(!open));
        btn.textContent = open ? `Show ${{btn.dataset.count}} more` : 'Show less';
      }});
    }});
  }}

  async function render() {{
    const container = document.getElementById('gh-repos');
    const loading = document.getElementById('gh-loading');
    try {{
      const [raw] = await Promise.all([
        Promise.all(SOURCES.map(fetchAll)).then(xs => xs.flat()),
        loadSignals(),
      ]);
      const repos = dedup(raw).filter(r => !SKIP.has(r.name));
      const byName = new Map(repos.map(r => [r.name.toLowerCase(), r]));

      // A pin claims its repo for its own category, so the regexes below never
      // steal it into an earlier one.
      const claimed = new Set();
      for (const pins of Object.values(PINNED)) {{
        for (const p of pins) {{
          const hit = p.repo && byName.get(p.repo.toLowerCase());
          if (hit) claimed.add(hit.id);
        }}
      }}

      function pinnedRows(heading) {{
        return (PINNED[heading] || []).map(p => {{
          const hit = p.repo && byName.get(p.repo.toLowerCase());
          if (hit) return repoRow(hit, p);
          // No repo behind it (private, or another org): a plain link, but only
          // if the pin carries its own URL.
          return p.url ? row({{ url: p.url, name: p.name || p.repo, desc: p.desc || '' }}) : '';
        }}).filter(Boolean);
      }}

      const placed = new Set();
      let html = '';

      for (const [heading, matchFn] of CATEGORIES) {{
        const bucket = repos.filter(r =>
          !placed.has(r.id) && !claimed.has(r.id) && matchFn(r));
        bucket.forEach(r => placed.add(r.id));
        html += renderCat(heading, [...pinnedRows(heading), ...bucket.map(r => repoRow(r))]);
      }}

      const rest = repos.filter(r => !placed.has(r.id) && !claimed.has(r.id));
      html += renderCat('Other', [...pinnedRows('Other'), ...rest.map(r => repoRow(r))]);

      container.innerHTML = html;
      wireDisclosures(container);
    }} catch(e) {{
      if (loading) loading.textContent = 'Could not load repos.';
    }}
  }}

  // ── Hugging Face ───────────────────────────────────────────────────────────
  // Same layout as the repo list, sorted by downloads so the models that get
  // used lead. The default listing only carries `downloads`, which is the
  // last-30-days figure -- the lifetime count needs an explicit expand, so both
  // numbers are asked for and both are shown.
  // `pipeline_tag` is a models-only field: asking for it on /api/datasets is a
  // 400, which would silently empty the datasets list.
  const HF_USER = 'EricSpencer00';
  const HF_FIELDS = {{
    models:   ['downloads', 'downloadsAllTime', 'likes', 'pipeline_tag', 'tags'],
    datasets: ['downloads', 'downloadsAllTime', 'likes', 'tags'],
  }};

  async function fetchHF(kind) {{
    const fields = HF_FIELDS[kind].map(f => `expand[]=${{f}}`).join('&');
    const res = await fetch(
      `https://huggingface.co/api/${{kind}}?author=${{HF_USER}}&limit=100&${{fields}}`,
      {{ headers: {{ Accept: 'application/json' }} }});
    if (!res.ok) return [];
    const data = await res.json();
    return Array.isArray(data) ? data : [];
  }}

  const allTime = x => x.downloadsAllTime || 0;
  const monthly = x => x.downloads || 0;
  const num = n => n.toLocaleString('en-US');

  function hfRow(item, kind) {{
    const short = item.id.includes('/') ? item.id.split('/')[1] : item.id;
    const tags = (item.tags || [])
      .filter(t => !t.includes(':') && !/^(region|license|arxiv)/.test(t))
      .slice(0, 2);
    const parts = [];
    if (allTime(item) > 0) parts.push(`&#8595; ${{num(allTime(item))}}`);
    if (monthly(item) > 0) parts.push(`${{num(monthly(item))}}/mo`);
    return row({{
      url: `https://huggingface.co/${{kind === 'datasets' ? 'datasets/' : ''}}${{item.id}}`,
      name: short,
      desc: item.pipeline_tag || tags.join(', ') || '',
      count: parts.join(' &middot; '),
      tags: item.likes > 0 ? [`${{item.likes}} like${{item.likes === 1 ? '' : 's'}}`] : [],
    }});
  }}

  async function renderHF() {{
    const container = document.getElementById('hf-list');
    const loading = document.getElementById('hf-loading');
    try {{
      const [models, datasets] = await Promise.all([fetchHF('models'), fetchHF('datasets')]);
      const all = [...models, ...datasets];
      const sum = (xs, f) => xs.reduce((n, x) => n + f(x), 0);
      const bydl = (a, b) => allTime(b) - allTime(a) || monthly(b) - monthly(a);

      // The ChatTLA+ family is what the downloads are actually for, so it gets
      // its own line rather than being left implicit in the per-row numbers.
      const chattla = all.filter(x => /chattla|tla-/i.test(x.id));
      const note = chattla.length
        ? `ChatTLA+ models and datasets: <b>${{num(sum(chattla, allTime))}}</b> downloads all-time,
           ${{num(sum(chattla, monthly))}} in the last 30 days.`
        : '';

      let html = '';
      html += renderCat('Hugging Face Models',
        models.sort(bydl).map(m => hfRow(m, 'models')), note);
      html += renderCat('Hugging Face Datasets',
        datasets.sort(bydl).map(d => hfRow(d, 'datasets')));
      if (!html) {{ loading.textContent = 'No Hugging Face artifacts found.'; return; }}
      container.innerHTML = html;
      wireDisclosures(container);
    }} catch(e) {{
      if (loading) loading.textContent = 'Could not load Hugging Face models.';
    }}
  }}

  render();
  renderHF();
}})();
</script>
</body></html>
"""

# ── main ──────────────────────────────────────────────────────────────────────

def main():
    news       = build_news()
    about      = build_about()
    selected   = build_selected()
    blog       = build_blog()
    experience = build_experience()

    page = build_page(news, about, selected, blog, experience)
    out  = ROOT / "index.html"
    out.write_text(page, encoding="utf-8")
    print(f"Built {out} ({len(page):,} bytes)")

if __name__ == "__main__":
    main()
