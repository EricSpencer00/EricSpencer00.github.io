#!/usr/bin/env python3
"""Generate the static HTML site: single homepage with everything,
   thin /projects.html and /research.html sub-pages, deep project pages,
   year-mirror pages for old Hugo URLs, smart 404 routing for the rest,
   sitemap and robots."""
import os, re, json, html as html_mod, shutil
from datetime import datetime

REPO = "/Users/eric/GitHub/EricSpencer00.github.io"
OUT = REPO
PROD = "https://ericspencer.us"
BACKUP_URL = "https://ericspencer.us/ericspencer-site-backup"
OG_IMAGE = f"{BACKUP_URL}/images/avatar.jpeg"
TODAY = datetime.now().strftime("%Y-%m-%d")
BACKUP_SOURCE = "/tmp/ericspencer-backup"  # cloned backup repo with Hugo source

# ── CSS ───────────────────────────────────────────────────────────
CSS = """:root{
  --paper:#f7f4ec; --ink:#181410; --maroon:#6d1414; --maroon2:#8a1f1f;
  --rule:#d8d0bf; --dim:#6f675a; --gold:#9a7b3a;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{
  margin:0; background:var(--paper);
  background-image:radial-gradient(#00000005 1px,transparent 1px);
  background-size:3px 3px;
  color:var(--ink);
  font-family:"Charter","Georgia","Times New Roman",serif;
  font-size:17px; line-height:1.6;
}
.wrap{max-width:760px;margin:0 auto;padding:34px 22px 90px}
a{color:var(--maroon);text-decoration:none;border-bottom:1px dotted #b98c8c}
a:hover{color:#fff;background:var(--maroon);border-bottom:1px solid var(--maroon)}
code,kbd,.mono,pre{font-family:"IBM Plex Mono","SFMono-Regular","JetBrains Mono",ui-monospace,Menlo,monospace}
pre.banner{
  color:var(--maroon); font-size:clamp(5.4px,1.55vw,11px); line-height:1.12;
  margin:0 0 2px; letter-spacing:0; overflow:hidden; white-space:pre;
}
.sub{font-family:"IBM Plex Mono",monospace;font-size:13px;color:var(--dim);
  letter-spacing:.04em;margin:0 0 4px}
.cursor::after{content:"_";color:var(--maroon);animation:bl 1s steps(1) infinite}
@keyframes bl{50%{opacity:0}}
hr{border:0;border-top:1px solid var(--rule);margin:22px 0}
.dash{border:0;border-top:1px dashed var(--rule);margin:20px 0}
h2{font-family:"IBM Plex Mono",monospace;font-size:13px;font-weight:700;
  text-transform:uppercase;letter-spacing:.22em;color:var(--maroon);
  margin:34px 0 12px;display:flex;align-items:center;gap:10px;
  scroll-margin-top:20px}
h2::before{content:"§";color:var(--gold);font-weight:400}
h2 .ln{flex:1;border-top:1px solid var(--rule);height:1px}
h3{font-size:18px;margin:20px 0 4px}
p{margin:10px 0}
nav.top{font-family:"IBM Plex Mono",monospace;font-size:13px;margin:6px 0 0;color:var(--dim)}
nav.top a{border:0;padding:1px 3px}
nav.top a:hover{background:var(--maroon);color:#fff}
.meta{font-family:"IBM Plex Mono",monospace;font-size:12.5px;color:var(--dim)}
.lead{font-size:17px}
ul.bare{list-style:none;margin:8px 0;padding:0}
.proj{font-family:"IBM Plex Mono",monospace;font-size:13.5px;line-height:1.75;
  display:flex;gap:10px;align-items:baseline;padding:1px 0;white-space:nowrap;
  overflow:hidden}
.proj a.nm{flex:0 0 auto;font-weight:600;border-bottom:1px dotted #b98c8c}
.proj .dt{flex:1;border-bottom:1px dotted #ddd4c2;transform:translateY(-3px);min-width:14px}
.proj .ds{flex:0 1 auto;color:var(--dim);overflow:hidden;text-overflow:ellipsis;
  white-space:nowrap;font-family:"Charter",Georgia,serif;font-size:14px}
.proj .lg{flex:0 0 auto;color:var(--maroon2);font-size:11px;opacity:.8}
.tag{display:inline-block;font-family:"IBM Plex Mono",monospace;font-size:10.5px;
  border:1px solid var(--rule);border-radius:2px;padding:0 5px;color:var(--dim);
  background:#fff8;margin-left:4px}
.news{font-family:"IBM Plex Mono",monospace;font-size:13.5px;display:flex;gap:14px;
  align-items:baseline;padding:3px 0}
.news .d{flex:0 0 92px;color:var(--maroon2);font-size:12px;font-variant-numeric:tabular-nums}
.news .t{flex:1;font-family:Charter,Georgia,serif;font-size:15.5px;color:var(--ink)}
.pill{font-family:"IBM Plex Mono",monospace;font-size:11px;color:var(--dim)}
footer{margin-top:46px;border-top:1px solid var(--rule);padding-top:14px;
  font-family:"IBM Plex Mono",monospace;font-size:11.5px;color:var(--dim);
  display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px}
.linkrow{font-family:"IBM Plex Mono",monospace;font-size:13px;margin:4px 0 0}
.linkrow a{margin-right:2px}
blockquote{margin:14px 0;padding:6px 16px;border-left:3px solid var(--maroon);
  color:#352f27;font-style:italic;background:#fff6}
.small{font-size:13px;color:var(--dim)}
pre.code{background:#0d0b09;color:#d4cfbf;padding:12px 16px;border-radius:3px;
  overflow-x:auto;font-size:13px;line-height:1.5;margin:10px 0}
pre.code code{background:none;padding:0;color:inherit}
code{background:#e8e2d6;padding:1px 5px;border-radius:2px;font-size:14px}
img{max-width:100%;height:auto;border:1px solid var(--rule);border-radius:3px;margin:10px 0}
.back{font-family:"IBM Plex Mono",monospace;font-size:13px;margin:0 0 12px}
.back a{border:0}
ol,ul{margin:8px 0;padding-left:24px}
li{margin:4px 0}
@media(max-width:560px){
  .proj{white-space:normal;flex-wrap:wrap}
  .proj .dt{display:none}.proj .ds{white-space:normal;flex-basis:100%}
}"""

BANNER = """ _____      _        ____
| ____|_ __(_) ___  / ___| _ __   ___ _ __   ___ ___ _ __
|  _| | '__| |/ __| \\___ \\| '_ \\ / _ \\ '_ \\ / __/ _ \\ '__|
| |___| |  | | (__   ___) | |_) |  __/ | | | (_|  __/ |
|_____|_|  |_|\\___| |____/| .__/ \\___|_| |_|\\___\\___|_|
                          |_|                             """


def seo_head(title, desc, canonical_path, og_type="website",
             keywords="", article_meta=None):
    canonical = f"{PROD}{canonical_path}"
    full_title = title if "Eric Spencer" in title else f"{title} | Eric Spencer"
    safe_title = html_mod.escape(full_title)
    safe_desc = html_mod.escape(desc)
    safe_kw = html_mod.escape(keywords) if keywords else ""

    head = f"""<!doctype html><html lang="en"><head>
<meta charset="utf-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{safe_title}</title>
<meta name="description" content="{safe_desc}">
<meta name="author" content="Eric Spencer">
<meta name="robots" content="index, follow">
"""
    if safe_kw:
        head += f'<meta name="keywords" content="{safe_kw}">\n'
    head += f'<link rel="canonical" href="{canonical}">\n'
    head += f"""<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{safe_title}">
<meta property="og:description" content="{safe_desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="Eric Spencer">
<meta property="og:image" content="{OG_IMAGE}">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{safe_title}">
<meta name="twitter:description" content="{safe_desc}">
<meta name="twitter:image" content="{OG_IMAGE}">
<meta property="linkedin:title" content="{safe_title}">
<meta property="linkedin:description" content="{safe_desc}">
<meta property="linkedin:image" content="{OG_IMAGE}">
"""
    if og_type == "article" and article_meta:
        head += f"""<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Article",
"headline":{json.dumps(title)},
"description":{json.dumps(desc)},
"url":{json.dumps(canonical)},
"image":{json.dumps(OG_IMAGE)},
"author":{{"@type":"Person","name":"Eric Spencer","url":"{PROD}/"}},
"publisher":{{"@type":"Person","name":"Eric Spencer","url":"{PROD}/"}},
"datePublished":"{article_meta.get('date','2026-01-01')}",
"mainEntityOfPage":{json.dumps(canonical)}}}
</script>
"""
    else:
        head += f"""<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Person",
"name":"Eric Spencer",
"alternateName":"EricSpencer00",
"url":"{PROD}/",
"image":"{OG_IMAGE}",
"sameAs":["https://github.com/EricSpencer00","https://huggingface.co/EricSpencer00","https://www.linkedin.com/in/ericspencer00/"],
"jobTitle":"Founder | AI researcher",
"affiliation":{{"@type":"CollegeOrUniversity","name":"Loyola University Chicago"}},
"email":"eric@ericspencer.us"}}
</script>
"""
    head += f"<style>\n{CSS}\n</style></head><body><div class=\"wrap\">"
    return head


def page_foot():
    # Customer-facing footer — no developer/build copy
    return """
<footer>
<span>&copy; 2026 Eric Spencer &middot; Chicago, IL</span>
<span><a href="mailto:eric@ericspencer.us">eric@ericspencer.us</a></span>
</footer>
</div></body></html>"""


def nav(active):
    items = [("index","/","index"), ("research","/research.html","research"),
             ("projects","/projects.html","projects")]
    parts = [f'<a href="{href}">[{label}]</a>' if key==active else f'<a href="{href}">{label}</a>'
             for label, href, key in items]
    return f'~/{active} &nbsp; {" &nbsp;·&nbsp; ".join(parts)}'


# ── Markdown → HTML ───────────────────────────────────────────────
def md_to_html(text):
    text = text.strip()
    text = re.sub(r'\{\{<\s*youtube\s+(\S+)\s*>\}\}',
                  r'<p><a href="https://youtube.com/watch?v=\1" target="_blank" rel="noopener">&#9654; Watch on YouTube</a></p>', text)
    text = re.sub(r'\{\{<.*?>\}\}', '', text)
    text = re.sub(r'\{\{%.*?%\}\}', '', text)

    lines = text.split('\n')
    out = []
    in_code = False; in_list = False; in_ol = False
    para = []

    def flush_para():
        if para:
            p = ' '.join(para); p = inline(p)
            out.append(f'<p>{p}</p>'); para.clear()

    def flush_list():
        nonlocal in_list, in_ol
        if in_list: out.append('</ul>'); in_list = False
        if in_ol: out.append('</ol>'); in_ol = False

    def inline(s):
        s = re.sub(r'!\[([^\]]*)\]\((/[^)]+)\)',
                   lambda m: f'<img src="{BACKUP_URL}{m.group(2)}" alt="{m.group(1)}">', s)
        s = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1">', s)
        s = re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)', r'<a href="\2" target="_blank" rel="noopener">\1</a>', s)
        s = re.sub(r'\[([^\]]+)\]\((/[^)]+)\)',
                   lambda m: f'<a href="{BACKUP_URL}{m.group(2)}">{m.group(1)}</a>', s)
        s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', s)
        s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
        s = re.sub(r'__(.+?)__', r'<b>\1</b>', s)
        s = re.sub(r'\*(.+?)\*', r'<i>\1</i>', s)
        s = re.sub(r'_(.+?)_', r'<i>\1</i>', s)
        s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
        s = re.sub(r'(?<!["\'>])(https?://\S+?)(?=[<\s,;)\]]|$)', r'<a href="\1" target="_blank" rel="noopener">\1</a>', s)
        return s

    for line in lines:
        if re.match(r'^```', line):
            if in_code: out.append('</code></pre>'); in_code = False
            else:
                flush_para(); flush_list()
                out.append('<pre class="code"><code>'); in_code = True
            continue
        if in_code: out.append(html_mod.escape(line)); continue
        stripped = line.strip()
        if not stripped: flush_para(); flush_list(); continue
        if re.match(r'^-{3,}$', stripped) or re.match(r'^\*{3,}$', stripped):
            flush_para(); flush_list(); out.append('<hr class="dash">'); continue
        m = re.match(r'^(#{1,4})\s+(.+)', stripped)
        if m:
            flush_para(); flush_list()
            level = len(m.group(1)); text_h = inline(m.group(2))
            if level <= 2: out.append(f'<h2>{text_h}<span class="ln"></span></h2>')
            else: out.append(f'<h3>{text_h}</h3>')
            continue
        if stripped.startswith('>'):
            flush_para(); flush_list()
            q = inline(stripped.lstrip('> '))
            out.append(f'<blockquote>{q}</blockquote>'); continue
        m = re.match(r'^[-*+]\s+(.+)', stripped)
        if m:
            flush_para()
            if not in_list: flush_list(); out.append('<ul>'); in_list = True
            out.append(f'<li>{inline(m.group(1))}</li>'); continue
        m = re.match(r'^\d+\.\s+(.+)', stripped)
        if m:
            flush_para()
            if not in_ol: flush_list(); out.append('<ol>'); in_ol = True
            out.append(f'<li>{inline(m.group(1))}</li>'); continue
        flush_list(); para.append(stripped)
    flush_para(); flush_list()
    if in_code: out.append('</code></pre>')
    return '\n'.join(out)


def read_content(directory):
    results = {}
    if not os.path.isdir(directory): return results
    for f in sorted(os.listdir(directory)):
        if f == "_index.md" or not f.endswith(".md"): continue
        path = os.path.join(directory, f)
        with open(path) as fh: content = fh.read()
        match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
        if not match: continue
        fm_raw, body = match.groups()
        title = re.search(r'title:\s*["\']?(.*?)["\']?\s*$', fm_raw, re.M)
        desc = re.search(r'description:\s*["\']?(.*?)["\']?\s*$', fm_raw, re.M)
        date = re.search(r'date:\s*["\']?(\d{4}-\d{2}-\d{2})', fm_raw)
        slug = f.replace(".md", "")
        results[slug] = {
            "title": title.group(1).strip('"\'') if title else slug,
            "description": desc.group(1).strip('"\'') if desc else "",
            "body": body.strip(),
            "date": date.group(1) if date else "2026-01-01",
        }
    return results


projects_by_year = {}
for y in ["2021","2022","2023","2024","2025","2026"]:
    projects_by_year[y] = read_content(f"{BACKUP_SOURCE}/content/projects/{y}")
misc_content = read_content(f"{BACKUP_SOURCE}/content/miscellaneous")

SLUG_TO_YEAR = {s: y for y, items in projects_by_year.items() for s in items}
all_writeups = {}
for y in projects_by_year.values(): all_writeups.update(y)
all_writeups.update(misc_content)

# Interactive games / Hugo-CSS-dependent → backup-site only, no own page
GAMES_BACKUP_ONLY = {
    "blackjack","chess","sneaker-run","gameoflife","pixel-profile","wiki-race","chess-stats",
    "auto-decode","bio-ops-web","gcf-de","fortnite-oneshot","oneshot-hm2016","timbuktu","windows",
    "old-website","oldest-site","chattlaplus","cybersecurity","search-engine",
}

FULL_PAGE_SLUGS = {s for s,d in all_writeups.items()
                   if len(d["body"]) > 500 and s not in GAMES_BACKUP_ONLY}

SLUG_TO_REPO = {
    "LoyolaHACK":"LoyolaHACK","ai-conversation":"ai-conversation","ai-headshots":"ai-headshots",
    "ai-os":"ai-os","ascii-llm-training":"ascii-llm-training","connect-4":"connect-4",
    "coq":"rocq","dexcom-navbar-macos":"DexcomNavBarIcon-macos","fb-clone":"fb-clone",
    "flatten-repo":"flatten-repo","fraud-predictor":"fraud-predictor",
    "fraud-predictor-full":"fraud-predictor","gesture":"Gesture","gitkey":"git-key-guardian",
    "glucopilot":"GluCoPilot","interactive-microwave-tla":"interactive-microwave-tla",
    "ios-soundboard":"iOS-soundboard","llmjammer":"llmjammer","mc-carspot":"mc-carspot",
    "mlb-hackathon":"MLB-Hackathon","palindrome":"palindrome-sentence-generator",
    "sign-language":"Sign-Language-Recognition","tdx-window-blocker":"WindowBlockerForTDX-MacOS",
    "terminalgpt":"TerminalGPT","tla-formal-generation":"tla-formal-generation",
    "udp-server-binary":"UDP-server-binary","youtube-dl":"youtubeDL",
    "claude-architect-quiz":"Claude-architect-quiz","comp388-llm":"comp388-llm",
    "resilient":"Resilient","rubix-snake-puzzle":"rubix-snake-puzzle",
    "tunes2tube-mac":"tunes2tube-mac","yeat-llm":"yeat-llm",
    "aoc2025":"AoC2025","chattla-dataset":"chattla-dataset-anon","song-recommender":"song-recommender",
}

REPO_TO_SLUG = {r: s for s, r in SLUG_TO_REPO.items() if r and s in FULL_PAGE_SLUGS}

GH_PAGES = {
    "Resilient":"https://ericspencer.us/Resilient/",
    "audio-tabula-rasa":"https://ericspencer.us/audio-tabula-rasa/",
    "design-skill":"https://ericspencer.us/design-skill/",
    "als-signature-reversal":"https://ericspencer.us/als-signature-reversal/",
    "Claude-architect-quiz":"https://ericspencer.us/Claude-architect-quiz/",
    "pitch":"https://ericspencer.us/pitch/",
    "fortnite-oneshot":"https://ericspencer00.github.io/fortnite-oneshot/",
    "HackIllinois26":"https://brightbet.tech",
    "caterpillar":"https://ericspencer.us/caterpillar/",
    "slot-machine":"https://ericspencer.us/slot-machine/",
    "fg-scrape":"https://ericspencer.us/fg-scrape/",
    "sneaker-run":"https://ericspencer00.github.io/sneaker-run/",
    "cubed-pack-solve":"https://ericspencer00.github.io/cubed-pack-solve/",
    "oneshot-hm2016":"https://ericspencer00.github.io/oneshot-hm2016/",
    "gcf-de":"https://ericspencer00.github.io/gcf-de/",
    "fb-clone":"https://fb-clone-7ng.pages.dev/",
    "margaux-website":"https://ericspencer00.github.io/margaux-website/",
    "auto-decode":"https://ericspencer00.github.io/auto-decode/",
    "git-key-guardian":"https://ericspencer00.github.io/git-key-guardian/",
    "GluCoPilot":"https://ericspencer00.github.io/GluCoPilot/",
    "rubix-snake-puzzle":"https://ericspencer.us/rubix-snake-puzzle/",
}


def resolve_link(repo_name):
    slug = REPO_TO_SLUG.get(repo_name)
    if slug: return f"/projects/{slug}.html", ""
    if repo_name in GH_PAGES: return GH_PAGES[repo_name], "_blank"
    return f"https://github.com/EricSpencer00/{repo_name}", "_blank"


def proj_line(name, href, desc, lang="", tag="", target="_blank"):
    t = f' target="{target}" rel="noopener"' if target else ""
    line = f'<div class="proj"><a class="nm" href="{href}"{t}>{html_mod.escape(name)}</a><span class="dt"></span>'
    d = html_mod.escape(desc)
    if tag: d += f' <span class="tag">{tag}</span>'
    line += f'<span class="ds">{d}</span>'
    if lang: line += f'<span class="lg">{html_mod.escape(lang)}</span>'
    line += '</div>\n'
    return line


# ── Individual project pages (canonical at /projects/{slug}.html) ──
def build_project_page(slug, canonical_path):
    data = all_writeups[slug]
    repo_name = SLUG_TO_REPO.get(slug)
    repo_url = f"https://github.com/EricSpencer00/{repo_name}" if repo_name else None
    body_html = md_to_html(data["body"])
    desc = data["description"] or f"{data['title']} — project by Eric Spencer."
    title = data["title"]
    keywords = ", ".join([title, "Eric Spencer", "project"])
    article_meta = {"date": data.get("date","2026-01-01")}
    h = seo_head(title, desc, canonical_path, og_type="article",
                 keywords=keywords, article_meta=article_meta)
    h += f'<pre class="banner">{BANNER}</pre>\n'
    h += '<div class="sub cursor">eric&nbsp;spencer &nbsp;//&nbsp; formal methods &middot; large language models &middot; systems</div>\n'
    h += f'<nav class="top">{nav("projects")}</nav>\n'
    h += '<hr>\n'
    h += f'<p class="back">&larr; <a href="/">back to index</a></p>\n'
    h += f'<h2>{html_mod.escape(title)}<span class="ln"></span></h2>\n'
    if desc: h += f'<p class="meta">{html_mod.escape(desc)}</p>\n'
    if repo_url: h += f'<p class="meta">repo: <a href="{repo_url}" target="_blank" rel="noopener">{repo_url}</a></p>\n'
    h += '<hr class="dash">\n'
    h += body_html
    h += page_foot()
    return h


# Make projects directory
os.makedirs(f"{OUT}/projects", exist_ok=True)

for slug in FULL_PAGE_SLUGS:
    canonical_path = f"/projects/{slug}.html"
    html = build_project_page(slug, canonical_path)
    with open(f"{OUT}/projects/{slug}.html","w") as f: f.write(html)
    # Mirror at old Hugo path
    if slug in SLUG_TO_YEAR:
        old_dir = f"{OUT}/projects/{SLUG_TO_YEAR[slug]}/{slug.lower()}"
        os.makedirs(old_dir, exist_ok=True)
        with open(f"{old_dir}/index.html","w") as f: f.write(html)
    elif slug in misc_content:
        old_dir = f"{OUT}/miscellaneous/{slug.lower()}"
        os.makedirs(old_dir, exist_ok=True)
        with open(f"{old_dir}/index.html","w") as f: f.write(html)

print(f"Generated {len(FULL_PAGE_SLUGS)} project pages with mirrors")


# ── Section repos (ordered: best first within each section) ───────
SECTIONS = [
    ("Formal Methods & Verification", "formal-methods", [
        ("Resilient", "Statically-typed compiled language for safety-critical embedded systems with Z3-verified contracts.", "Rust"),
        ("rubix-snake-puzzle", "Formal verification (Coq + TLA+) of Rubik's-Snake state reachability.", "Rocq Prover"),
        ("interactive-microwave-tla", "Browser-based TLA+ microwave — a gentle first model-checking demo.", "Java"),
        ("FormaLLM", "Toolkit for evaluating LLMs on formal-specification synthesis.", "TLA", "fork"),
        ("chattla-dataset-anon", "Anonymized dataset release for the ChatTLA+ paper.", ""),
        ("Resilient-examples", "Mission-critical example programs for Resilient.", "Shell"),
        ("tla-formal-generation", "Pipeline for generating TLA+ specs from natural language.", "Python"),
        ("tla-walk-in-oven", "TLA+ specification of a walk-in-oven control system.", "TLA"),
        ("tla-dexcom-g7", "TLA+ specification of Dexcom G7 CGM session lifecycle.", "TLA"),
        ("c4-fmitf", "TLA+ formal model of Connect-4 game mechanics.", "TLA"),
        ("tla-laptop", "TLA+ model of laptop power/state transitions.", "TLA"),
        ("fm-cb-game", "Formally-modeled combinatorial board game in TLA+.", "TLA"),
        ("TLAJVM", "Experiments running TLA+ / TLC tooling on the JVM.", "Java"),
        ("rocq", "Playground for the Rocq (Coq) proof assistant.", "Coq"),
        ("goldbach-conj", "Brute-force verification of the strong Goldbach conjecture to 1e9.", "Python"),
    ]),
    ("AI, LLMs & Machine Learning", "ai-llms", [
        ("GluCoPilot", "OpenAI Hackathon '25 — LLM copilot over Dexcom glucose data.", "Swift"),
        ("reelforge", "macOS app: Claude writes the script, ffmpeg burns the captions.", "TypeScript"),
        ("als-signature-reversal", "Reverse-signature drug repurposing for ALS on iPSC RNA-seq data.", "Jupyter Notebook"),
        ("ascii-llm-training", "Training a small LM purely on ASCII text.", "Python"),
        ("comp388-llm", "Coursework: LLM systems (COMP 388).", "Python"),
        ("llmjammer", "Python source obfuscator built to confuse code-scraping LLMs.", "Python"),
        ("TerminalGPT", "Terminal-native LLM chat through OpenRouter.", "Python"),
        ("ai-conversation", "Two LLMs debate philosophy with each other.", "Python"),
        ("ITS-RAG-bot", "Retrieval-augmented assistant for an IT-service knowledge base.", "Python"),
        ("Claude-architect-quiz", "Free flashcards + practice quiz for the Anthropic architect exam.", "CSS"),
        ("yeat-llm", "Lyric-style language model experiment.", "Python"),
        ("ollama-vibecode", "Local Ollama-driven code generation experiments.", "Python"),
        ("ai-os", "Experimental LLM-driven operating-shell concept.", "Python"),
        ("connect-4", "Chess-engine-style analyzer for Connect-4.", "Python"),
        ("rl-agent-c4", "Reinforcement-learning agent for Connect-4.", "Python"),
        ("rvc-artist", "Retrieval-based voice-conversion pipeline.", "Python"),
        ("Intro-to-tts", "Minimal text-to-speech in Python.", "Python"),
        ("Handwriting", "Handwriting-recognition experiment.", "Python"),
        ("fortnite-oneshot", "One-shot scripting experiment.", "JavaScript"),
        ("oneshot-hm2016", "One-shot generation experiment.", "JavaScript"),
        ("audio-tabula-rasa", "Audio processing experiment.", "Python"),
    ]),
    ("macOS, iOS & Desktop", "mac-ios", [
        ("tunes2tube-mac", "macOS app: cover art + audio in, MP4 music videos out.", "Swift"),
        ("DexcomNavBarIcon-macos", "macOS menu-bar widget surfacing live Dexcom readings.", "Python"),
        ("Gesture", "Proof-of-concept Jarvis-style gesture control for macOS.", "Python"),
        ("ChessStats", "Pulls and displays Chess.com statistics.", "Python"),
        ("youtubeDL", "Personal CLI / localhost YouTube audio+video downloader.", "Python"),
        ("iOS-soundboard", "iOS soundboard app.", "Swift"),
        ("apple-music-widget", "Now-playing Apple Music web widget.", "JavaScript"),
        ("ReserveLibraryRoom", "Automates Loyola library-room reservations.", "Python"),
        ("WindowBlockerForTDX-MacOS", "Safari script blocking the TDX ticketing pop-out on macOS.", "JavaScript"),
        ("DexVal", "Dexcom data validation / analysis utility.", "Python"),
        ("T-square", "Swift utility app.", "Swift"),
    ]),
    ("Systems, Languages & Tools", "systems", [
        ("git-key-guardian", "Pre-commit guard that blocks secret keys from being committed.", "Shell"),
        ("flatten-repo", "VS Code extension: flattens a repository into a single LLM-ready file.", "JavaScript"),
        ("notify-agent-done", "Desktop notification when a long-running agent finishes.", "TypeScript"),
        ("UDP-server-binary", "Binary-protocol UDP server in C++.", "C++"),
        ("itch-parser", "C parser for ITCH-format market data.", "C"),
        ("itch-parser-eric", "Hand-rolled C variant of the ITCH market-data parser.", "C"),
        ("reverse-xoroshiro128plusplus", "Recovering xoroshiro128++ PRNG state from output.", "Python"),
        ("mc-carspot", "Rust online-parking-spot simulator with switching costs.", "Rust"),
        ("cubed-pack-solve", "Solver for a 3-D cube-packing puzzle.", "Python"),
        ("auto-decode", "Heuristic auto-detection and decoding of encoded text.", "JavaScript"),
        ("palindrome-sentence-generator", "Generates whole paragraphs that read as palindromes.", "Python"),
        ("grade-public-commits", "Auto-grades student work from public commit history.", "Python"),
        ("roman-numeral-converter", "Roman-numeral <-> integer converter.", "Java"),
        ("etl-demo", "Small ETL pipeline demonstration.", "Python"),
        ("fg-scrape", "Targeted web-scraping utility.", "Python"),
        ("EmailExtraction", "Bulk email-address extraction utility.", "Python"),
        ("scala-workshop", "Scala workshop materials and exercises.", "Scala"),
        ("scala-hello-world", "Scala starter project.", "Scala"),
        ("copilot-cli-test", "Copilot CLI evaluation sandbox.", "Shell"),
    ]),
    ("Web & Front-End", "web", [
        ("EricSpencer00.github.io", "Source of this site.", "HTML"),
        ("pitch", "Pitch-deck site.", "HTML"),
        ("fb-clone", "Systems-analysis Facebook clone (GraceNook).", "TypeScript"),
        ("design-skill", "Single-page editorial rendition of the personal site.", "HTML"),
        ("ai4fm", "Source for the Loyola FMitF / AI4FM research-group website.", "Python"),
        ("dev.EricSpencer00.github.io", "Public dev/staging of the personal site.", "HTML"),
        ("archaic-radio-frontend", "Front-end for a retro internet-radio player.", "HTML"),
        ("caterpillar", "Static / interactive web piece.", "HTML"),
        ("gcf-de", "Svelte data-engineering front end.", "Svelte"),
        ("margaux-website", "Personal client website.", ""),
        ("DailyTask-web", "Daily-task tracker web app.", "HTML"),
        ("bio-ops-web", "Bioinformatics ops web dashboard.", "JavaScript"),
        ("sneaker-run", "Browser endless-runner game.", "JavaScript"),
        ("slot-machine", "Browser slot-machine game.", "JavaScript"),
        ("spa-web", "Single-page web app scaffold.", "HTML"),
        ("cone-site", "Static site project.", "HTML"),
        ("uzzGenerator", "Procedurally generates 'uzz'.", "Python"),
        ("EricSpencer00", "GitHub profile README.", "HTML"),
    ]),
    ("Coursework, Hackathons & Misc", "coursework", [
        ("HackIllinois26", "HackIllinois 2026 hackathon project.", "TypeScript"),
        ("MLB-Hackathon", "Google Cloud x MLB hackathon — Hall of Fame predictor.", "Python"),
        ("LoyolaHACK", "CTA Transit Tracker — Loyola hackathon.", "HTML"),
        ("Serenity", "WildHacks 2024 project.", "JavaScript"),
        ("HealthUp-", "COMP 322 semester-long mobile health app.", "JavaScript"),
        ("AoC2025", "Advent of Code 2025 solutions.", "Python"),
        ("comp371-team8-activity", "Programming languages (COMP 371).", "Scala"),
        ("Comp272Projects", "Data structures (COMP 272).", "Java"),
        ("COMP330Group5", "Coursework group project (COMP 330).", "Java"),
        ("BlackJackGame", "Blackjack game.", "Python"),
        ("AnagramSolverV1", "Anagram solver.", "Java"),
        ("Chat", "Java chat application.", "Java"),
    ]),
]

LUC_AI4FM = [
    ("ChatTLA", "Fine-tuning open-source LLMs to generate verifiable TLA+ formal specs.", "Python"),
    ("FormaLLM", "Toolkit for evaluating LLMs on formal-specification synthesis.", "TLA"),
    ("eric-paper", "ICSOFT paper: ChatTLA+ fine-tuning for verifiable TLA+ specifications.", "TeX"),
    ("chattla-spec-gen-paper", "ChatTLA+ NeurIPS 2026 paper.", "TeX"),
    ("chattla-gpt-oss-paper", "Fine-tuning gpt-oss-20b for verifiable TLA+ specs.", "TeX"),
    ("TLA-Extraction", "Extracting TLA+ specifications from research papers.", "Python"),
    ("tla-dataset-pipeline", "Dataset pipeline for TLA+ specification data.", "Python"),
    ("tla_benchmark", "Benchmark suite for TLA+ spec generation.", ""),
    ("tla_description", "TLA+ description corpus for LLM training.", ""),
    ("ralph-tla", "Ralph TLA+ experiments.", ""),
    ("paper-parse", "Research paper parsing utilities.", "Python"),
    ("webpage", "AI4FM research group website source.", "HTML"),
]

FROM_AMERICA = [
    ("instxnt.xyz", "Visual AI-powered storefront builder.", "TypeScript"),
    ("instxnt-mcp", "MCP server for instxnt.xyz — create storefronts through Claude, ChatGPT, Gemini.", "TypeScript"),
    ("picai", "AI photo platform.", "TypeScript"),
    ("StockGenie", "Stock analysis iOS app.", "JavaScript"),
    ("stockgenie-web", "StockGenie static site: Privacy & Terms.", "HTML"),
    ("fair-share", "Receipt scanner and bill splitter iOS app.", "Jupyter Notebook"),
    ("FreeLock", "iOS app.", "Swift"),
    ("ealing-capital", "Ealing Capital site redesign (Astro + Tailwind).", "Astro"),
    ("wildhacks-26", "WildHacks 2026 entry.", "Swift"),
    ("glucopilot-v2", "GluCoPilot v2 iOS app.", "Swift"),
    ("cs-glucopilot", "GluCoPilot case study.", "Python"),
    ("DailyTask", "iOS daily task tracker.", "Swift"),
    ("ai-headshots", "AI headshot generator.", "TypeScript"),
    ("arb-bot-live", "Live arbitrage bot.", "C++"),
    ("autotrade", "Automated trading system.", "Python"),
    ("b-slang", "Language experiment.", "TypeScript"),
    ("suno-ipad", "Suno iPad interface.", "Swift"),
    ("chambr-web", "Chambr website: privacy, terms, landing page.", "HTML"),
    ("splithound-web", "SplitHound web presence.", "HTML"),
    ("FreeLock-web", "FreeLock web presence.", "HTML"),
    ("Panda-Roll", "iOS game app.", "Swift"),
    ("HideAndSeek", "iOS game.", "Swift"),
    ("Rogue", "iOS game.", "Swift"),
    ("Private-Whisper", "Private speech-to-text iOS app.", "Swift"),
    ("idle-fish", "iOS idle game.", "Swift"),
    ("IdleHeroes", "iOS idle game.", "Swift"),
    ("famous.moji", "Emoji app.", "CSS"),
    ("from-america.github.io", "FROM AMERICA LLC corporate site.", "HTML"),
]
FA_PAGES = {
    "instxnt.xyz":"https://instxnt.xyz","stockgenie-web":"https://stockgenie.app",
    "picai":"https://picai.us","FreeLock":"https://fromamerica-llc.com/FreeLock/",
    "FreeLock-web":"https://fromamerica-llc.com/FreeLock-web/",
    "splithound-web":"https://fromamerica-llc.com/splithound-web/",
    "chambr-web":"https://fromamerica-llc.com/chambr-web/",
    "suno-ipad":"https://fromamerica-llc.com/suno-ipad/",
    "ealing-capital":"https://ealing-capital.pages.dev",
    "from-america.github.io":"https://fromamerica-llc.com",
}

FORKS = [
    ("Whisky", "A modern Wine wrapper for macOS built with SwiftUI.", "Swift"),
    ("BrowserOS", "BrowserOS — an open-source agentic web browser.", "Python"),
    ("vscode", "Visual Studio Code.", "TypeScript"),
    ("tlaplus", "TLC model checker for TLA+.", "Java"),
    ("typescript-go", "Native port of TypeScript.", "Go"),
    ("cli-github", "GitHub's official command line tool.", "Go"),
    ("linguist", "Language Savant.", "Ruby"),
    ("Examples", "A collection of TLA+ specifications.", "TLA"),
    ("CSAPP-Lab", "Solutions to CSAPP & CMU 15-213 labs.", "C"),
    ("harvard-cs50w-2020", "CS50's Web Programming.", "HTML"),
    ("trash-alloy", "Filesystem trash example from Alloy 6 book.", "Alloy"),
    ("Sign-Language-Recognition", "Spring 2025 Sign Language Recognition Model.", "Python"),
    ("MovieRec-F24", "Fall 2024 movie rec project.", "Python"),
    ("March-Madness-ML", "Machine-learned bracketology.", "Python"),
    ("simpleconcurrency-tla", "TLA+ concurrency example.", "TLA"),
    ("echotest-scala", "Scala echo test.", "Scala"),
    ("shapes-oo-scala", "Scala OO shapes example.", "Scala"),
    ("argon-design-system-angular", "Argon design system port.", "SCSS"),
    ("claude-architect-exam-prep", "Architect exam prep materials.", ""),
    ("Hello-World", "First repo on GitHub.", ""),
]

# Misc content: short writeups or interactive demos that live in backup-site
MISC_DEMOS = [
    ("Game of Life", f"{BACKUP_URL}/miscellaneous/gameoflife/", "Conway's Game of Life — canvas demo.", "JavaScript"),
    ("BlackJack", f"{BACKUP_URL}/miscellaneous/blackjack/", "Browser blackjack with fake money.", "JavaScript"),
    ("Chess.com Stats", f"{BACKUP_URL}/miscellaneous/chess-stats/", "Pulls and visualizes Chess.com stats.", "Python"),
    ("Pixel Profile", f"{BACKUP_URL}/miscellaneous/pixel-profile/", "GitHub profile-picture generator.", "JavaScript"),
    ("Wiki Race", f"{BACKUP_URL}/miscellaneous/wiki-race/", "Wikipedia speed-run game.", "JavaScript"),
    ("Chess Game", f"{BACKUP_URL}/miscellaneous/chess/", "Browser chess game.", "JavaScript"),
    ("Skeuomorphic Desk", "/projects/skeuomorphism.html", "An editorial / skeuomorphic project desk.", "HTML"),
    ("Song Recommender", "/projects/song-recommender.html", "Python recommender that beats Spotify's mid suggestions.", "Python"),
    ("How to tell if it's AI", "/projects/tell-ai.html", "Heuristic essay on spotting AI-generated text.", ""),
    ("My ~/.zshrc", "/projects/my-zshrc.html", "Annotated walkthrough of my shell config.", "Shell"),
    ("AoC 2025", "/projects/aoc2025.html", "Advent of Code 2025 notes.", "Python"),
    ("ChatTLA+ Dataset", "/projects/chattla-dataset.html", "Notes on the ChatTLA+ dataset release.", ""),
]


# ── INDEX.HTML (single page with everything) ──────────────────────
def gen_index():
    h = seo_head(
        "Eric Spencer — formal methods, LLMs, systems",
        "Eric Spencer, undergraduate researcher at Loyola University Chicago. Formal methods, large language models, systems. ChatTLA+, the Resilient compiler, AI4FM.",
        "/",
        keywords="Eric Spencer, EricSpencer00, formal methods, TLA+, LLM, ChatTLA+, Loyola University Chicago, AI4FM, Resilient, AI researcher"
    )
    h += f'<pre class="banner">{BANNER}</pre>\n'
    h += '<div class="sub cursor">eric&nbsp;spencer &nbsp;//&nbsp; formal methods &middot; large language models &middot; systems</div>\n'
    h += f'<nav class="top">{nav("index")}</nav>\n'
    h += '<hr>\n\n'

    # Bio
    h += '<p class="lead">I am an undergraduate researcher at <b>Loyola University Chicago</b> working at the intersection of formal methods and large language models &mdash; asking whether machines can write specifications a model checker will actually accept.</p>\n'
    h += '<p>With the <a href="https://ai4fm.cs.luc.edu/" target="_blank" rel="noopener">AI4FM / FMitF group</a> under Prof. Konstantin L&auml;ufer, I built the first systematic evaluation of LLM-generated <span class="mono">TLA+</span>, trained the <a href="https://huggingface.co/EricSpencer00/chattla-20b" target="_blank" rel="noopener">chattla-20b</a> model, and presented <b>ChatTLA+</b>. Outside the lab I write compilers (<a href="/projects/resilient.html">Resilient</a>), ship macOS/iOS apps, and keep <b>116+</b> repositories on the go.</p>\n'
    h += '<div class="linkrow">\n'
    h += '&#9656; <a href="https://github.com/EricSpencer00" target="_blank" rel="noopener">github</a> &middot;\n'
    h += '<a href="https://huggingface.co/EricSpencer00" target="_blank" rel="noopener">huggingface</a> &middot;\n'
    h += '<a href="https://www.linkedin.com/in/ericspencer00/" target="_blank" rel="noopener">linkedin</a> &middot;\n'
    h += '<a href="https://ai4fm.cs.luc.edu/" target="_blank" rel="noopener">ai4fm.cs.luc.edu</a> &middot;\n'
    h += '<a href="mailto:eric@ericspencer.us">email</a>\n'
    h += '</div>\n\n'

    # News
    h += '<h2 id="news">News<span class="ln"></span></h2>\n'
    news_items = [
        ("2026-04-17", 'Presented <b>ChatTLA+</b> at Loyola\'s Undergraduate Research &amp; Engagement Symposium.', "https://ai4fm.cs.luc.edu/posts/chattla-presentation-2026/"),
        ("2026-04", 'Paper <i>Can LLMs Write Correct TLA+ Specifications?</i> <b>accepted to ICSOFT 2026</b> (Porto).', "https://ai4fm.cs.luc.edu/papers/llm-tla-evaluation/"),
        ("2026-04-11", 'Co-author on the GSIRS 2026 poster &mdash; first systematic eval of LLM&rarr;TLA+ synthesis.', "https://ai4fm.cs.luc.edu/posts/gsirs-llm-tla-poster-2026/"),
        ("2026-03", 'Released <b>chattla-20b</b> on Hugging Face &mdash; 4,000+ downloads.', "https://huggingface.co/EricSpencer00/chattla-20b"),
        ("2025", 'Awarded the <b>Mulcahy Scholar</b> stipend for LLM-based TLA+ research.', "https://ai4fm.cs.luc.edu/posts/eric-spencer-mulcahy-scholar-2025/"),
    ]
    for date, text, link in news_items:
        h += f'<div class="news"><span class="d">{date}</span><span class="t">{text} <a href="{link}" target="_blank" rel="noopener" class="pill">[link]</a></span></div>\n'

    # Selected Work
    h += '\n<h2 id="selected">Selected Work<span class="ln"></span></h2>\n'
    selected = [
        ("chattla-20b", "https://huggingface.co/EricSpencer00/chattla-20b", "Fine-tuned 20B model (SFT+GRPO on gpt-oss-20b) for TLA+ generation.", ""),
        ("Resilient", "/projects/resilient.html", "Statically-typed compiled language for safety-critical embedded systems.", "Rust"),
        ("ChatTLA+ paper", "https://ai4fm.cs.luc.edu/papers/llm-tla-evaluation/", "First systematic evaluation of LLM-generated TLA+ — accepted to ICSOFT 2026.", ""),
        ("rubix-snake-puzzle", "/projects/rubix-snake-puzzle.html", "Formal verification (Coq + TLA+) of Rubik's-Snake state reachability.", "Rocq Prover"),
        ("als-signature-reversal", "https://github.com/EricSpencer00/als-signature-reversal", "Reverse-signature drug repurposing for ALS on iPSC RNA-seq data.", "Jupyter Notebook"),
        ("reelforge", "https://github.com/EricSpencer00/reelforge", "macOS app: Claude writes the script, ffmpeg burns the captions.", "TypeScript"),
        ("FormaLLM", "https://github.com/EricSpencer00/FormaLLM", "Toolkit for evaluating LLMs on formal-specification synthesis.", "TLA"),
        ("GluCoPilot", "/projects/glucopilot.html", "OpenAI Hackathon '25 — LLM copilot over Dexcom glucose data.", "Swift"),
    ]
    for name, href, desc, lang in selected:
        tgt = "_blank" if href.startswith("http") else ""
        h += proj_line(name, href, desc, lang, target=tgt)

    # Full project listing — categorized
    for section_title, anchor, repos in SECTIONS:
        h += f'\n<h2 id="{anchor}">{section_title} <span class="pill">({len(repos)})</span><span class="ln"></span></h2>\n'
        for item in repos:
            name, desc, lang = item[0], item[1], item[2]
            tag = item[3] if len(item) > 3 else ""
            href, tgt = resolve_link(name)
            h += proj_line(name, href, desc, lang, tag, tgt)

    # LUC-AI4FM
    h += f'\n<h2 id="luc-ai4fm">LUC-AI4FM <span class="pill">({len(LUC_AI4FM)})</span><span class="ln"></span></h2>\n'
    h += '<p class="small">Research repos from the <a href="https://ai4fm.cs.luc.edu/" target="_blank" rel="noopener">AI4FM / FMitF group</a> at Loyola.</p>\n'
    for name, desc, lang in LUC_AI4FM:
        h += proj_line(name, f"https://github.com/LUC-AI4FM/{name}", desc, lang, target="_blank")

    # FROM AMERICA
    h += f'\n<h2 id="from-america">FROM AMERICA <span class="pill">({len(FROM_AMERICA)})</span><span class="ln"></span></h2>\n'
    h += '<p class="small">Products and experiments under <a href="https://fromamerica-llc.com" target="_blank" rel="noopener">FROM AMERICA LLC</a>.</p>\n'
    for name, desc, lang in FROM_AMERICA:
        href = FA_PAGES.get(name, f"https://github.com/from-america/{name}")
        h += proj_line(name, href, desc, lang, target="_blank")

    # Misc & Demos
    h += f'\n<h2 id="misc">Misc &amp; Demos <span class="pill">({len(MISC_DEMOS)})</span><span class="ln"></span></h2>\n'
    h += '<p class="small">Smaller writeups and interactive web demos.</p>\n'
    for name, href, desc, lang in MISC_DEMOS:
        tgt = "_blank" if href.startswith("http") else ""
        h += proj_line(name, href, desc, lang, target=tgt)

    # Papers
    h += '\n<h2 id="papers">Papers<span class="ln"></span></h2>\n'
    h += '<div class="news"><span class="d">2026</span><span class="t"><b>Can LLMs Write Correct TLA+ Specifications?</b> Accepted to <b>ICSOFT 2026</b> (Porto). <a href="https://ai4fm.cs.luc.edu/papers/llm-tla-evaluation/" target="_blank" rel="noopener" class="pill">[link]</a> <a href="https://github.com/LUC-AI4FM/eric-paper" target="_blank" rel="noopener" class="pill">[repo]</a></span></div>\n'
    h += '<div class="news"><span class="d">2026</span><span class="t"><b>ChatTLA+ spec-gen paper</b> (NeurIPS 2026 submission). <a href="https://github.com/LUC-AI4FM/chattla-spec-gen-paper" target="_blank" rel="noopener" class="pill">[repo]</a></span></div>\n'
    h += '<div class="news"><span class="d">2026</span><span class="t"><b>ChatTLA+ gpt-oss paper</b> &mdash; fine-tuning gpt-oss-20b for verifiable TLA+ specs and TLAPS proofs. <a href="https://github.com/LUC-AI4FM/chattla-gpt-oss-paper" target="_blank" rel="noopener" class="pill">[repo]</a></span></div>\n'

    # Models & Datasets
    h += '\n<h2 id="models">Models &amp; Datasets<span class="ln"></span></h2>\n'
    h += '<div class="news"><span class="d">2026-03</span><span class="t"><b>chattla-20b</b> on Hugging Face &mdash; fine-tuned 20B model (SFT+GRPO on gpt-oss-20b) for TLA+. 4,000+ downloads. <a href="https://huggingface.co/EricSpencer00/chattla-20b" target="_blank" rel="noopener" class="pill">[model]</a></span></div>\n'
    h += '<div class="news"><span class="d">2026</span><span class="t"><b>chattla-dataset-anon</b> &mdash; anonymized dataset for the ChatTLA+ paper. <a href="https://github.com/EricSpencer00/chattla-dataset-anon" target="_blank" rel="noopener" class="pill">[repo]</a></span></div>\n'

    # Awards
    h += '\n<h2 id="awards">Awards<span class="ln"></span></h2>\n'
    h += '<div class="news"><span class="d">2025</span><span class="t">Awarded the <b>Mulcahy Scholar</b> stipend for LLM-based TLA+ research. <a href="https://ai4fm.cs.luc.edu/posts/eric-spencer-mulcahy-scholar-2025/" target="_blank" rel="noopener" class="pill">[link]</a></span></div>\n'

    # Forks (collapsed at the bottom)
    h += f'\n<h2 id="forks">Contributions &amp; Forks <span class="pill">({len(FORKS)})</span><span class="ln"></span></h2>\n'
    h += '<p class="small">Course materials, upstream tools, and projects I\'ve forked or contributed to.</p>\n'
    for name, desc, lang in FORKS:
        h += proj_line(name, f"https://github.com/EricSpencer00/{name}", desc, lang, target="_blank")

    h += page_foot()
    return h


# ── /projects.html and /research.html: thin focused sub-pages ──────
def gen_projects_page():
    """Projects-only listing — no bio, news, or research sections."""
    h = seo_head(
        "Projects", "Every repo and writeup by Eric Spencer — formal methods, LLMs, systems.",
        "/projects.html",
        keywords="Eric Spencer, projects, GitHub, TLA+, LLM, Resilient"
    )
    h += f'<pre class="banner">{BANNER}</pre>\n'
    h += '<div class="sub cursor">eric&nbsp;spencer &nbsp;//&nbsp; formal methods &middot; large language models &middot; systems</div>\n'
    h += f'<nav class="top">{nav("projects")}</nav>\n'
    h += '<hr>\n'
    h += '<p class="lead">Every public repository from <a href="https://github.com/EricSpencer00" target="_blank" rel="noopener">github.com/EricSpencer00</a> plus org work at <a href="https://github.com/LUC-AI4FM" target="_blank" rel="noopener">LUC-AI4FM</a> and <a href="https://github.com/from-america" target="_blank" rel="noopener">FROM AMERICA</a>.</p>\n'

    for section_title, anchor, repos in SECTIONS:
        h += f'<h2 id="{anchor}">{section_title} <span class="pill">({len(repos)})</span><span class="ln"></span></h2>\n'
        for item in repos:
            name, desc, lang = item[0], item[1], item[2]
            tag = item[3] if len(item) > 3 else ""
            href, tgt = resolve_link(name)
            h += proj_line(name, href, desc, lang, tag, tgt)

    h += f'<h2 id="luc-ai4fm">LUC-AI4FM <span class="pill">({len(LUC_AI4FM)})</span><span class="ln"></span></h2>\n'
    for name, desc, lang in LUC_AI4FM:
        h += proj_line(name, f"https://github.com/LUC-AI4FM/{name}", desc, lang, target="_blank")

    h += f'<h2 id="from-america">FROM AMERICA <span class="pill">({len(FROM_AMERICA)})</span><span class="ln"></span></h2>\n'
    for name, desc, lang in FROM_AMERICA:
        href = FA_PAGES.get(name, f"https://github.com/from-america/{name}")
        h += proj_line(name, href, desc, lang, target="_blank")

    h += f'<h2 id="misc">Misc &amp; Demos <span class="pill">({len(MISC_DEMOS)})</span><span class="ln"></span></h2>\n'
    for name, href, desc, lang in MISC_DEMOS:
        tgt = "_blank" if href.startswith("http") else ""
        h += proj_line(name, href, desc, lang, target=tgt)

    h += f'<h2 id="forks">Contributions &amp; Forks <span class="pill">({len(FORKS)})</span><span class="ln"></span></h2>\n'
    for name, desc, lang in FORKS:
        h += proj_line(name, f"https://github.com/EricSpencer00/{name}", desc, lang, target="_blank")

    h += page_foot()
    return h


def gen_research_page():
    """Research-only focused page."""
    h = seo_head(
        "Research", "Papers, presentations, models, and awards by Eric Spencer.",
        "/research.html",
        keywords="Eric Spencer, research, TLA+, LLM, ChatTLA+, AI4FM, ICSOFT 2026, formal methods"
    )
    h += f'<pre class="banner">{BANNER}</pre>\n'
    h += '<div class="sub cursor">eric&nbsp;spencer &nbsp;//&nbsp; formal methods &middot; large language models &middot; systems</div>\n'
    h += f'<nav class="top">{nav("research")}</nav>\n'
    h += '<hr>\n'
    h += '<p class="lead">Papers, talks, and tools from my work at the <a href="https://ai4fm.cs.luc.edu/" target="_blank" rel="noopener">AI4FM / FMitF group</a> at Loyola University Chicago, under Prof. Konstantin L&auml;ufer.</p>\n'

    h += '<h2 id="papers">Papers<span class="ln"></span></h2>\n'
    h += '<div class="news"><span class="d">2026</span><span class="t"><b>Can LLMs Write Correct TLA+ Specifications?</b> Accepted to <b>ICSOFT 2026</b> (Porto). <a href="https://ai4fm.cs.luc.edu/papers/llm-tla-evaluation/" target="_blank" rel="noopener" class="pill">[link]</a> <a href="https://github.com/LUC-AI4FM/eric-paper" target="_blank" rel="noopener" class="pill">[repo]</a></span></div>\n'
    h += '<div class="news"><span class="d">2026</span><span class="t"><b>ChatTLA+ spec-gen paper</b> (NeurIPS 2026 submission). <a href="https://github.com/LUC-AI4FM/chattla-spec-gen-paper" target="_blank" rel="noopener" class="pill">[repo]</a></span></div>\n'
    h += '<div class="news"><span class="d">2026</span><span class="t"><b>ChatTLA+ gpt-oss paper</b> &mdash; fine-tuning gpt-oss-20b for verifiable TLA+ specs and TLAPS proofs. <a href="https://github.com/LUC-AI4FM/chattla-gpt-oss-paper" target="_blank" rel="noopener" class="pill">[repo]</a></span></div>\n'

    h += '<h2 id="talks">Presentations &amp; Posters<span class="ln"></span></h2>\n'
    h += '<div class="news"><span class="d">2026-04-17</span><span class="t">Presented <b>ChatTLA+</b> at Loyola\'s Undergraduate Research &amp; Engagement Symposium. <a href="https://ai4fm.cs.luc.edu/posts/chattla-presentation-2026/" target="_blank" rel="noopener" class="pill">[link]</a></span></div>\n'
    h += '<div class="news"><span class="d">2026-04-11</span><span class="t">Co-author on the <b>GSIRS 2026</b> poster &mdash; first systematic eval of LLM&rarr;TLA+ synthesis. <a href="https://ai4fm.cs.luc.edu/posts/gsirs-llm-tla-poster-2026/" target="_blank" rel="noopener" class="pill">[link]</a></span></div>\n'

    h += '<h2 id="models">Models &amp; Datasets<span class="ln"></span></h2>\n'
    h += '<div class="news"><span class="d">2026-03</span><span class="t"><b>chattla-20b</b> on Hugging Face &mdash; fine-tuned 20B model (SFT+GRPO on gpt-oss-20b) for TLA+. 4,000+ downloads. <a href="https://huggingface.co/EricSpencer00/chattla-20b" target="_blank" rel="noopener" class="pill">[model]</a></span></div>\n'
    h += '<div class="news"><span class="d">2026</span><span class="t"><b>chattla-dataset-anon</b> &mdash; anonymized dataset for the ChatTLA+ paper. <a href="https://github.com/EricSpencer00/chattla-dataset-anon" target="_blank" rel="noopener" class="pill">[repo]</a></span></div>\n'

    h += '<h2 id="tools">Tools<span class="ln"></span></h2>\n'
    h += '<div class="news"><span class="d">2026</span><span class="t"><b>FormaLLM</b> &mdash; toolkit for evaluating LLMs on formal-specification synthesis. <a href="https://github.com/LUC-AI4FM/FormaLLM" target="_blank" rel="noopener" class="pill">[repo]</a></span></div>\n'
    h += '<div class="news"><span class="d">2025</span><span class="t"><b>TLA-Extraction</b> &mdash; extracting TLA+ specs from research papers. <a href="https://github.com/LUC-AI4FM/TLA-Extraction" target="_blank" rel="noopener" class="pill">[repo]</a></span></div>\n'

    h += '<h2 id="awards">Awards<span class="ln"></span></h2>\n'
    h += '<div class="news"><span class="d">2025</span><span class="t">Awarded the <b>Mulcahy Scholar</b> stipend for LLM-based TLA+ research. <a href="https://ai4fm.cs.luc.edu/posts/eric-spencer-mulcahy-scholar-2025/" target="_blank" rel="noopener" class="pill">[link]</a></span></div>\n'

    h += page_foot()
    return h


# ── Write main pages ──────────────────────────────────────────────
with open(f"{OUT}/index.html","w") as f: f.write(gen_index())
with open(f"{OUT}/projects.html","w") as f: f.write(gen_projects_page())
with open(f"{OUT}/research.html","w") as f: f.write(gen_research_page())


# ── 404.html: smart JS router for any old Hugo URL ─────────────────
# Catches paths that aren't real files and redirects to backup-site.
def gen_404():
    h = seo_head("404 — Not Found", "Page not found.", "/404.html")
    h += f'<pre class="banner">{BANNER}</pre>\n'
    h += '<div class="sub cursor">eric&nbsp;spencer &nbsp;//&nbsp; formal methods &middot; large language models &middot; systems</div>\n'
    h += f'<nav class="top">{nav("index")}</nav>\n'
    h += '<hr>\n'
    h += '<h2>Looking for something?<span class="ln"></span></h2>\n'
    h += '<p>This page doesn\'t exist on the current site. If you followed an older link, try the <a id="archive-link" href="/ericspencer-site-backup/">archive of the old site</a> &mdash; the same path is likely there.</p>\n'
    h += '<p>Or jump to: <a href="/">index</a> &middot; <a href="/projects.html">projects</a> &middot; <a href="/research.html">research</a>.</p>\n'
    # JS: rewrite archive link to mirror the requested path so the user
    # lands on the same content one hop away
    h += """<script>
(function(){
  var p = window.location.pathname;
  // strip trailing index.html, normalize leading slash
  p = p.replace(/index\\.html$/,'').replace(/^\\/+/,'/');
  var target = 'https://ericspencer.us/ericspencer-site-backup' + p;
  var link = document.getElementById('archive-link');
  if(link) link.href = target;
  // auto-redirect after a short pause so the user sees context
  setTimeout(function(){ window.location.replace(target); }, 1500);
})();
</script>
"""
    h += page_foot()
    return h


with open(f"{OUT}/404.html","w") as f: f.write(gen_404())
print("Wrote 404.html (smart router)")


# ── SITEMAP ───────────────────────────────────────────────────────
urls = [
    (f"{PROD}/", "1.0", "weekly"),
    (f"{PROD}/projects.html", "0.9", "weekly"),
    (f"{PROD}/research.html", "0.9", "weekly"),
]
for slug in sorted(FULL_PAGE_SLUGS):
    urls.append((f"{PROD}/projects/{slug}.html", "0.8", "monthly"))
mirrored_paths = set()
for slug in FULL_PAGE_SLUGS:
    if slug in SLUG_TO_YEAR:
        mirrored_paths.add(f"projects/{SLUG_TO_YEAR[slug]}/{slug.lower()}/")
    elif slug in misc_content:
        mirrored_paths.add(f"miscellaneous/{slug.lower()}/")
for old_path in sorted(mirrored_paths):
    urls.append((f"{PROD}/{old_path}", "0.6", "monthly"))

sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
for url, prio, freq in urls:
    sitemap += f"  <url>\n    <loc>{url}</loc>\n    <lastmod>{TODAY}</lastmod>\n    <changefreq>{freq}</changefreq>\n    <priority>{prio}</priority>\n  </url>\n"
sitemap += '</urlset>\n'
with open(f"{OUT}/sitemap.xml","w") as f: f.write(sitemap)
print(f"Wrote sitemap.xml with {len(urls)} URLs")


# ── ROBOTS.TXT ────────────────────────────────────────────────────
robots = f"""User-agent: *
Allow: /

Sitemap: {PROD}/sitemap.xml
"""
with open(f"{OUT}/robots.txt","w") as f: f.write(robots)


print(f"\nDone — {len(FULL_PAGE_SLUGS)} canonical pages, "
      f"{len(mirrored_paths)} year-mirrors, smart 404 router catches everything else.")
