#!/usr/bin/env node
/**
 * build-blog.js
 * Compile blog/posts/*.md → blog/*.html and regenerate blog/index.html
 *
 * Frontmatter (YAML-style, between --- delimiters):
 *   title: My Post Title
 *   date: 2026-07-12
 *   description: A short summary shown in the index.
 *   slug: my-post-title        # optional; defaults to filename without .md
 *   draft: true                # optional; skip this post entirely
 *
 * Usage:
 *   node scripts/build-blog.js
 */

import { readFileSync, writeFileSync, readdirSync, mkdirSync, existsSync } from 'fs';
import { join, basename, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, '..');
const POSTS_DIR = join(ROOT, 'blog', 'posts');
const BLOG_DIR = join(ROOT, 'blog');

// ---------------------------------------------------------------------------
// Minimal Markdown → HTML converter (no deps)
// ---------------------------------------------------------------------------
function mdToHtml(md) {
  let html = md;

  // Fenced code blocks  ```lang\n...\n```
  html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) => {
    const escaped = escapeHtml(code.trimEnd());
    const cls = lang ? ` class="language-${lang}"` : '';
    return `<pre><code${cls}>${escaped}</code></pre>`;
  });

  // Inline code `...`
  html = html.replace(/`([^`\n]+)`/g, (_, c) => `<code>${escapeHtml(c)}</code>`);

  // Images  ![alt](src)
  html = html.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1">');

  // Links  [text](url)
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');

  // Headings (must come before bold/italic)
  html = html.replace(/^#{6}\s+(.+)$/gm, '<h6>$1</h6>');
  html = html.replace(/^#{5}\s+(.+)$/gm, '<h5>$1</h5>');
  html = html.replace(/^#{4}\s+(.+)$/gm, '<h4>$1</h4>');
  html = html.replace(/^###\s+(.+)$/gm, '<h3>$1</h3>');
  html = html.replace(/^##\s+(.+)$/gm, '<h2>$1</h2>');
  html = html.replace(/^#\s+(.+)$/gm, '<h1>$1</h1>');

  // Horizontal rule
  html = html.replace(/^[-*_]{3,}\s*$/gm, '<hr>');

  // Blockquotes
  html = html.replace(/^>\s+(.+)$/gm, '<blockquote><p>$1</p></blockquote>');

  // Bold + italic ***text***
  html = html.replace(/\*{3}(.+?)\*{3}/g, '<strong><em>$1</em></strong>');
  // Bold **text** or __text__
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/__(.+?)__/g, '<strong>$1</strong>');
  // Italic *text* or _text_
  html = html.replace(/\*([^*\n]+)\*/g, '<em>$1</em>');
  html = html.replace(/_([^_\n]+)_/g, '<em>$1</em>');

  // Unordered lists (-, *, +)
  html = html.replace(/((?:^[-*+] .+\n?)+)/gm, (block) => {
    const items = block.trim().split('\n').map(l => `  <li>${l.replace(/^[-*+] /, '').trim()}</li>`).join('\n');
    return `<ul>\n${items}\n</ul>\n`;
  });

  // Ordered lists
  html = html.replace(/((?:^\d+\. .+\n?)+)/gm, (block) => {
    const items = block.trim().split('\n').map(l => `  <li>${l.replace(/^\d+\. /, '').trim()}</li>`).join('\n');
    return `<ol>\n${items}\n</ol>\n`;
  });

  // Paragraphs: wrap consecutive non-empty, non-block lines
  html = html.replace(/^(?!<[a-z]|$)(.+)$/gm, (line) => {
    // Don't double-wrap already-tagged lines
    if (/^<(h[1-6]|ul|ol|li|blockquote|pre|hr|img)/.test(line.trim())) return line;
    return `<p>${line}</p>`;
  });

  // Clean up blank lines
  html = html.replace(/\n{3,}/g, '\n\n');

  return html.trim();
}

function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// ---------------------------------------------------------------------------
// Frontmatter parser
// ---------------------------------------------------------------------------
function parseFrontmatter(raw) {
  const match = raw.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  if (!match) return { meta: {}, body: raw };

  const meta = {};
  for (const line of match[1].split('\n')) {
    const idx = line.indexOf(':');
    if (idx === -1) continue;
    const key = line.slice(0, idx).trim();
    const val = line.slice(idx + 1).trim().replace(/^['"]|['"]$/g, '');
    meta[key] = val;
  }
  return { meta, body: match[2] };
}

// ---------------------------------------------------------------------------
// HTML template for a single post
// ---------------------------------------------------------------------------
function renderPost({ title, date, description, slug, body }) {
  const safeTitle = escapeHtml(title);
  const safeDesc = escapeHtml(description || '');
  return `<!doctype html><html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${safeTitle} | Eric Spencer</title>
<meta name="description" content="${safeDesc}">
<meta name="author" content="Eric Spencer">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://ericspencer.us/blog/${slug}.html">
<meta property="og:type" content="article">
<meta property="og:title" content="${safeTitle} | Eric Spencer">
<meta property="og:description" content="${safeDesc}">
<meta property="og:url" content="https://ericspencer.us/blog/${slug}.html">
<meta property="og:site_name" content="Eric Spencer">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap">
<style>
:root{--paper:oklch(0.978 0.006 80);--ink:oklch(0.11 0.015 60);--accent:oklch(0.30 0.13 22);--dim:oklch(0.52 0.01 70);--rule:oklch(0.87 0.005 80)}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:var(--paper);color:var(--ink);font-family:"Plus Jakarta Sans",-apple-system,BlinkMacSystemFont,sans-serif;font-size:16px;line-height:1.7;-webkit-font-smoothing:antialiased}
.wrap{max-width:680px;margin:0 auto;padding:56px 24px 100px}
nav.top{font-size:14px;font-weight:500;color:var(--dim);margin:0 0 32px}
nav.top a{color:inherit;text-decoration:none;border:0;padding:0 2px}
nav.top a:hover{color:var(--ink)}
hr{border:0;border-top:1px solid var(--rule);margin:28px 0}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline;text-decoration-thickness:1px;text-underline-offset:3px}
h1{font-size:clamp(24px,4vw,36px);font-weight:700;letter-spacing:-0.025em;line-height:1.1;margin:0 0 8px}
.meta{font-family:"IBM Plex Mono",monospace;font-size:12px;color:var(--dim);margin:0 0 32px}
h2{font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:0.07em;color:var(--dim);margin:40px 0 12px}
h3{font-size:18px;font-weight:600;letter-spacing:-0.01em;margin:28px 0 6px}
p{margin:14px 0;font-size:16px;line-height:1.75}
code,kbd,pre{font-family:"IBM Plex Mono",ui-monospace,monospace}
code{background:oklch(0.94 0.005 80);padding:1px 5px;border-radius:4px;font-size:13px}
pre{background:oklch(0.12 0.01 240);color:oklch(0.85 0.02 80);padding:14px 18px;border-radius:6px;overflow-x:auto;font-size:13px;line-height:1.6;margin:16px 0}
pre code{background:none;padding:0;color:inherit}
blockquote{margin:16px 0;padding:8px 18px;border-left:2px solid var(--rule);color:var(--dim);font-style:italic}
ul,ol{margin:12px 0;padding-left:24px}li{margin:5px 0}
img{max-width:100%;border-radius:6px;margin:16px 0}
footer{margin-top:60px;border-top:1px solid var(--rule);padding-top:16px;font-size:13px;color:var(--dim);display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px}
@media(max-width:560px){.wrap{padding:36px 18px 80px}}
</style></head><body><div class="wrap">

<nav class="top"><a href="/">index</a> &nbsp;·&nbsp; <a href="/blog/">&larr; blog</a></nav>

<h1>${safeTitle}</h1>
<div class="meta">${date || ''}</div>
<hr>

${body}

<footer>
<span>&copy; ${new Date().getFullYear()} Eric Spencer &middot; Chicago, IL</span>
<span><a href="mailto:eric@ericspencer.us">eric@ericspencer.us</a></span>
</footer>
</div></body></html>`;
}

// ---------------------------------------------------------------------------
// Regenerate blog/index.html post list
// ---------------------------------------------------------------------------
function rebuildIndex(posts) {
  const indexPath = join(BLOG_DIR, 'index.html');
  let html = readFileSync(indexPath, 'utf8');

  // Build rows HTML (newest first)
  const sorted = [...posts].sort((a, b) => (b.date || '').localeCompare(a.date || ''));
  let rows;
  if (sorted.length === 0) {
    rows = `\n<p style="color:var(--dim);font-size:14px;font-style:italic">No posts yet.</p>\n`;
  } else {
    rows = '\n' + sorted.map(p => {
      const desc = p.description ? `\n<div class="post-desc">${escapeHtml(p.description)}</div>` : '';
      return `<div class="post-row"><div class="post-d">${p.date || ''}</div><div class="post-body"><div class="post-title"><a href="/blog/${p.slug}.html">${escapeHtml(p.title)}</a></div>${desc}</div></div>`;
    }).join('\n') + '\n';
  }

  // Replace everything between <!-- POSTS:START --> and <!-- POSTS:END --> markers
  if (html.includes('<!-- POSTS:START -->')) {
    html = html.replace(/<!-- POSTS:START -->[\s\S]*?<!-- POSTS:END -->/, `<!-- POSTS:START -->${rows}<!-- POSTS:END -->`);
  } else {
    // First run: insert markers around whatever placeholder is there now
    html = html.replace(
      /<h2>Posts<\/h2>\n[\s\S]*?(?=\n<footer)/,
      `<h2>Posts</h2>\n<!-- POSTS:START -->${rows}<!-- POSTS:END -->`
    );
  }

  writeFileSync(indexPath, html, 'utf8');
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------
if (!existsSync(POSTS_DIR)) {
  mkdirSync(POSTS_DIR, { recursive: true });
  console.log('Created blog/posts/ — drop .md files there.');
}

const mdFiles = readdirSync(POSTS_DIR).filter(f => f.endsWith('.md') && !f.startsWith('_'));
if (mdFiles.length === 0) {
  console.log('No .md files found in blog/posts/. Nothing to build.');
  process.exit(0);
}

const built = [];

for (const file of mdFiles) {
  const raw = readFileSync(join(POSTS_DIR, file), 'utf8');
  const { meta, body } = parseFrontmatter(raw);

  if (meta.draft === 'true') {
    console.log(`  skip (draft)  ${file}`);
    continue;
  }

  const slug = meta.slug || basename(file, '.md');
  const title = meta.title || slug;
  const date = meta.date || '';
  const description = meta.description || '';

  const htmlBody = mdToHtml(body);
  const page = renderPost({ title, date, description, slug, body: htmlBody });

  const outPath = join(BLOG_DIR, `${slug}.html`);
  writeFileSync(outPath, page, 'utf8');
  console.log(`  built  blog/${slug}.html`);

  built.push({ slug, title, date, description });
}

rebuildIndex(built);
console.log(`\nDone. ${built.length} post(s) compiled. blog/index.html updated.`);
