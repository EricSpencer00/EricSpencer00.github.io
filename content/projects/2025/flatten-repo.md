---
title: "flatten-repo VSC Extension"
date: 2025-03-28
description: "A VS Code extension I made when I kept running out of Copilot credits — flattens a repo into one .txt file you can paste into a free LLM."
tags: ["LLM", "AI", "AI-written"]
categories: ["Projects"]
image: "/previews/flatten-repo.png"
draft: false
---

I made this when I kept burning through my monthly Copilot allotment and wanted to drop a whole project into a free Gemini or Claude session without copy-pasting twenty files one by one.

It's a VS Code extension. You point it at your workspace, run `Flatten Project to TXT` from the command palette, and it dumps the whole codebase into a single `.txt` file under `/flattened/`. If the repo is too big for one LLM's context window, it splits into chunks based on a configurable token limit (~4 chars per token, rough but fine). Each chunk starts with a directory tree, then the files in `=== FILE: path/to/file.ext ===` blocks. It also auto-adds `/flattened` to your `.gitignore` so you don't accidentally commit the dumps.

The actually-useful part is the filtering. You don't want `node_modules` in there. You probably don't want test files or `.env` either. Everything gets configured through a single `.flatten_ignore` at the project root, which the extension generates for you on first run. Glob-based, with three sections — `global` for things you always want out, `whitelist` for narrowing down to specific paths, and `blacklist` for specific exceptions. There's also a `settings:` section for per-project token caps.

A sample `.flatten_ignore` looks like this:

```txt
# Ignore rules
global:
node_modules
.git
dist

# Whitelist (optional)
whitelist:
src/**/*.js

# Blacklist (optional)
blacklist:
**/*.test.js
.env

# Settings (optional)
settings:
maxTokenLimit: 50000
maxTokensPerFile: 25000
```

You can also stick the same kind of config in `.vscode/settings.json` if you'd rather keep it with the rest of your VS Code stuff:

```json
"flattenRepo.includeExtensions": [".ts", ".tsx", ".js", ".jsx", ".py", ".html", ".css"],
"flattenRepo.ignoreDirs": ["node_modules", ".git", "dist"],
"flattenRepo.maxChunkSize": 200000
```

That's basically it. It's command-only — no UI for picking files interactively, which I'd like to add at some point — and it doesn't try to flatten binaries or images. Honestly, what I use it for most is dropping a flattened repo into a free model when I've already spent my paid credits for the month on something dumb.

[GitHub Repo](https://github.com/EricSpencer00/flatten-repo) — feel free to open issues or send a PR if you want to take a swing at the file-picker UI.

---

*Written with AI.*
