#!/usr/bin/env python3
"""
build.py — reads content/*.txt, writes index.html.
Run by GitHub Actions on every push; do not edit index.html directly.
"""

from pathlib import Path
import html as htmllib

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
    posts = list(lines("blog.txt"))
    if not posts:
        return '<p class="dim-note">No posts yet.</p>'
    rows = []
    for line in posts:
        date, title, url, desc = parse(line, 4)
        rows.append(
            f'<div class="post-row">'
            f'<span class="post-d">{date}</span>'
            f'<div class="post-body">'
            f'<div class="post-title"><a href="{url}">{title}</a></div>'
            f'{"<p class=post-desc>" + desc + "</p>" if desc else ""}'
            f'</div></div>'
        )
    return "\n".join(rows)

def build_experience():
    rows = []
    for line in lines("experience.txt"):
        role, org, org_url, start, end, logo = parse(line, 6)
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
            initials = "".join(w[0] for w in org.split()[:2]).upper()
            logo_html = (
                f'<div class="cv-logo">'
                f'<svg width="36" height="36" viewBox="0 0 36 36"><rect width="36" height="36" rx="6" fill="#ddd"/>'
                f'<text x="18" y="24" font-family="Plus Jakarta Sans,sans-serif" font-size="11" font-weight="700" fill="#555" text-anchor="middle">{initials}</text></svg>'
                f'</div>'
            )
        org_link = f'<a href="{org_url}" target="_blank" rel="noopener">{org}</a>' if org_url else org
        rows.append(
            f'<div class="cv-row">'
            f'{logo_html}'
            f'<div class="cv-body">'
            f'<div class="cv-role">{role}</div>'
            f'<div class="cv-org">{org_link}</div>'
            f'<div class="cv-when">{date_str}</div>'
            f'</div></div>'
        )
    return "\n".join(rows)

# ── full page template ────────────────────────────────────────────────────────

def build_page(news, about, selected, blog, experience):
    return f"""<!doctype html><html lang="en"><head>
<meta charset="utf-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Eric Spencer</title>
<meta name="description" content="Eric Spencer — researcher, founder, and software engineer based in Chicago.">
<meta name="author" content="Eric Spencer">
<meta name="robots" content="index, follow">
<meta name="keywords" content="Eric Spencer, EricSpencer00, formal methods, TLA+, LLM, ChatTLA+, Loyola University Chicago, AI4FM">
<link rel="canonical" href="https://ericspencer.us/">
<meta property="og:type" content="website">
<meta property="og:title" content="Eric Spencer">
<meta property="og:description" content="Researcher, founder, and software engineer based in Chicago.">
<meta property="og:url" content="https://ericspencer.us/">
<meta property="og:site_name" content="Eric Spencer">
<meta property="og:image" content="https://ericspencer.us/ericspencer-site-backup/images/avatar.jpeg">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="Eric Spencer">
<meta name="twitter:description" content="Graduate researcher at Loyola University Chicago.">
<meta name="twitter:image" content="https://ericspencer.us/ericspencer-site-backup/images/avatar.jpeg">
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Person","name":"Eric Spencer","alternateName":"EricSpencer00","url":"https://ericspencer.us/","image":"https://ericspencer.us/ericspencer-site-backup/images/avatar.jpeg","sameAs":["https://github.com/EricSpencer00","https://huggingface.co/EricSpencer00","https://www.linkedin.com/in/ericspencer00/"],"jobTitle":"Founder | AI researcher","affiliation":{{"@type":"CollegeOrUniversity","name":"Loyola University Chicago"}},"email":"eric@ericspencer.us"}}
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap">
<style>
:root{{--paper:oklch(0.978 0.006 80);--ink:oklch(0.11 0.015 60);--accent:oklch(0.30 0.13 22);--dim:oklch(0.52 0.01 70);--rule:oklch(0.87 0.005 80)}}
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
.small{{font-size:13px;color:var(--dim)}}
code{{background:oklch(0.94 0.005 80);padding:1px 5px;border-radius:4px;font-size:13px}}
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
@media(max-width:560px){{.wrap{{padding:36px 18px 80px}}.proj .dt,.proj .ds{{display:none}}.post-d{{display:none}}#gh-repos .repo-row .dt,#gh-repos .repo-row .ds{{display:none}}}}
</style></head><body><div class="wrap">
<h1 class="name-hero">Eric Spencer</h1>
<nav class="top"><a href="/" class="active">index</a> &nbsp;&middot;&nbsp; <a href="/research.html">research</a> &nbsp;&middot;&nbsp; <a href="/projects.html">projects</a> &nbsp;&middot;&nbsp; <a href="/blog/">blog</a></nav>
<hr>

<h2 id="news">News</h2>
{news}

<h2 id="about">About</h2>
{about}
<div class="linkrow">
&#9656; <a href="https://github.com/EricSpencer00" target="_blank" rel="noopener">github</a> &middot;
<a href="https://huggingface.co/EricSpencer00" target="_blank" rel="noopener">huggingface</a> &middot;
<a href="https://www.linkedin.com/in/ericspencer00/" target="_blank" rel="noopener">linkedin</a> &middot;
<a href="https://ai4fm.cs.luc.edu/" target="_blank" rel="noopener">ai4fm.cs.luc.edu</a> &middot;
<a href="/assets/resume.pdf" target="_blank" rel="noopener">r&eacute;sum&eacute;</a> &middot;
<a href="mailto:eric@ericspencer.us">email</a>
</div>

<h2 id="selected">Selected Work</h2>
{selected}

<h2 id="blog">Blog</h2>
{blog}
<p class="small" style="margin-top:6px"><a href="/blog/">&rarr; all posts</a></p>

<div id="gh-repos">
<p class="loading" id="gh-loading">Loading repos&hellip;</p>
</div>

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
      /mac|ios|swift|tunes2tube|dexcom|ChessStats|youtube-dl|soundboard|apple-music|ReserveLibrary|tdx|DexVal|T-square/i.test(r.name)
    ],
    ['Systems, Languages & Tools', r =>
      /UDP-server|itch-parser|xoroshiro|mc-carspot|palindrome|grade-public|roman-numeral|etl-demo|fg-scrape|EmailExtract|scala|gitkey|flatten-repo|notify-agent|reverse-xoro|auto-decode/i.test(r.name)
    ],
    ['Web & Front-End', r =>
      /github[.]io$|[-]web$|front|fb-clone|design-skill|caterpillar|gcf-de|margaux|DailyTask|bio-ops|sneaker-run|slot-machine|spa-web|cone-site|uzz|pitch|archaic-radio|stockgenie-web|FreeLock-web|splithound-web|chambr-web|from-america[.]|webpage/i.test(r.name) ||
      (r.homepage||'').includes('github.io')
    ],
    ['Hackathons & Coursework', r =>
      /hack|Serenity|LoyolaHACK|comp[0-9]|COMP[0-9]|cs50|csapp|HealthUp|AoC|march-mad|MovieRec|BlackJack|AnagramSolver|Chat(?!TLA)|BrightBet|claude-architect-exam/i.test(r.name)
    ],
    ['Contributions & Forks', r => r.fork === true],
  ];

  async function fetchAll(source) {{
    const base = source.type === 'user'
      ? `https://api.github.com/users/${{source.name}}/repos?per_page=100&sort=updated&type=all`
      : `https://api.github.com/orgs/${{source.name}}/repos?per_page=100&sort=updated`;
    const res = await fetch(base, {{ headers: {{ Accept: 'application/vnd.github+json' }} }});
    if (!res.ok) return [];
    const data = await res.json();
    return data.map(r => ({{ ...r, _source: source.label }}));
  }}

  function makeRow(repo) {{
    const url = repo.homepage || repo.html_url;
    const desc = repo.description || '';
    const stars = repo.stargazers_count > 0
      ? `<span class="stars">&#9733; ${{repo.stargazers_count}}</span>` : '';
    const forkTag = repo.fork ? '<span class="tag">fork</span>' : '';
    const sourceTag = repo._source ? `<span class="tag">${{repo._source}}</span>` : '';
    return `<div class="repo-row">
      <a href="${{url}}" target="_blank" rel="noopener">${{repo.name}}</a>
      <span class="dt"></span>
      <span class="ds">${{desc}}${{forkTag}}${{sourceTag}}</span>
      ${{stars}}
    </div>`;
  }}

  async function render() {{
    const container = document.getElementById('gh-repos');
    const loading = document.getElementById('gh-loading');
    try {{
      const raw = (await Promise.all(SOURCES.map(fetchAll))).flat();
      const repos = dedup(raw).filter(r => !SKIP.has(r.name));

      const placed = new Set();
      let html = '';

      for (const [heading, matchFn] of CATEGORIES) {{
        const bucket = repos.filter(r => !placed.has(r.id) && matchFn(r));
        if (!bucket.length) continue;
        bucket.forEach(r => placed.add(r.id));
        html += `<div class="gh-cat">
          <h2>${{heading}} <span class="pill">(${{bucket.length}})</span></h2>
          ${{bucket.map(makeRow).join('\\n')}}
        </div>`;
      }}

      const rest = repos.filter(r => !placed.has(r.id));
      if (rest.length) {{
        html += `<div class="gh-cat">
          <h2>Other <span class="pill">(${{rest.length}})</span></h2>
          ${{rest.map(makeRow).join('\\n')}}
        </div>`;
      }}

      container.innerHTML = html;
    }} catch(e) {{
      if (loading) loading.textContent = 'Could not load repos.';
    }}
  }}

  render();
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
