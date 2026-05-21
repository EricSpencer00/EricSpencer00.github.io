---
title: "Claude Architect Quiz"
date: 2026-05-14
description: "Free flashcards and practice quiz for the Anthropic Claude Certified Architect exam."
tags: ["Web", "JavaScript", "AI", "AI-written"]
categories: ["Projects"]
draft: false
image: "/previews/default-project.png"
---

Anthropic put out the Claude Certified Architect — Foundations (CCA-F) exam, and the official study material is a Skilljar course plus scattered docs. There were a few community study repos floating around, mostly raw markdown lists of questions. I wanted something I could actually drill on between meetings, on my phone, without signing up for anything — so I built one.

Live at [ericspencer.us/Claude-architect-quiz](https://ericspencer.us/Claude-architect-quiz/). It's 115 flashcards across 7 weighted domains: agentic architecture, tool design and MCP, Claude Code workflows, prompt engineering, context management, cross-cutting topics, and a Q&A bank that mirrors `avidevelops/claude-architect-exam-prep` so the well-known practice questions are in there too. The domain weights match the exam guide, so if you cram you're cramming on roughly the right stuff.

There are three modes. **Cards** is the standard flip-and-mark-known loop. **Quiz** is multiple choice with explanations and a per-domain score breakdown at the end, so you can see which area you should go back and read on the Anthropic docs site. **Cram** auto-cycles and weights toward the cards you marked for review, which is the one I actually use the most.

The whole thing is a static site — plain HTML, CSS, and JavaScript, no build step, no framework. `data/flashcards.json` is the single source of truth. Each card is just:

```json
{
  "id": "unique-slug",
  "type": "multiple-choice",
  "question": "...",
  "options": ["A", "B", "C", "D"],
  "answer": "text of correct option",
  "explanation": "Why this is correct + common gotchas",
  "difficulty": "medium",
  "tags": ["..."]
}
```

Progress lives in `localStorage`. Nothing gets sent anywhere — there's no backend to send it to. If you clear your browser data, your "known" pile resets. That felt like the right tradeoff for a thing you use for two weeks before an exam and then never again.

The one design choice I cared about was making it keyboard-first. If I'm grinding through 115 cards I do not want to be moving my mouse between every card. `C` jumps to cards, `Q` to quiz, `R` to cram, `S` to stats. `Space` reveals the answer, `J` marks for review, `K` marks as known, `1`–`9` picks a multiple-choice option, `?` opens the help overlay. You can run a full study session without touching the trackpad, which is what I wanted from the other study sites and never found.

Content was compiled from publicly available sources — the two community repos linked in the README, the Anthropic Academy program overview, the actual platform docs for prompt caching / tool use / batches / MCP, and a few longer write-ups on Dev.to and Medium. Not affiliated with Anthropic in any way, and I make a point of saying so on the site. Always cross-check against the official exam guide before you take the thing.

If you spot a wrong answer or a domain that's underweighted, the source is right there — open a PR on [the repo](https://github.com/EricSpencer00/Claude-architect-quiz) or just file an issue. I'll keep updating the cards as Anthropic updates the exam.

---

*Written with AI.*
