---
title: "ChatTLA+ Dataset"
date: 2026-05-13
description: "The dataset release for the ChatTLA+ paper — SFT corpus and benchmark for TLA+ spec generation, posted anonymized for blind review."
tags: ["AI", "LLM", "TLA+", "Research", "AI-written"]
categories: ["Miscellaneous"]
draft: false
image: "/previews/default-project.png"
---

This is the dataset release that goes with the ChatTLA+ paper I submitted to ICSOFT 2026. The paper is currently under double-blind review, so the repo is up under an anonymized name with author info and the sibling training-code repo withheld until the review window closes. Once the camera-ready lands, I'll point this page at the real repo.

The dataset has two parts. The first is `corpus/diamond_sft.jsonl`, which is 209 rows of supervised fine-tuning data — each row is an OpenAI-style chat list (developer/user/assistant) where the assistant turn is a TLA+ spec that TLC actually validated. Every row carries semantic metadata: how many distinct states TLC explored, what fraction of declared actions got exercised, whether the spec caught at least one mutation of its invariant, and how many invariants were checked. The `_source: opus_subagent` tag means an Opus-family model drafted the seed and TLC verified it — that's a methodology marker, not an author hint.

The second part is a 30-problem held-out benchmark in `benchmark/`, split into six domains: consensus/election, data structures, classical puzzles, scheduling/resources, transactions/databases, and workflows/state machines. Five problems per domain. Each benchmark entry has a natural-language description, an ordinal 1-5 difficulty, the invariants the spec must declare, and a module-name pointer to the closest reference spec in the public [`tlaplus/examples`](https://github.com/tlaplus/examples) repository. I deliberately didn't redistribute any verbatim files from `tlaplus/examples` — just pointers — so the licensing stays clean. The dataset itself is CC-BY-4.0.

There's also a small `eval.jsonl` (four prompts) used as a generation eval during training.

If you want context on what ChatTLA+ actually does, I have a [short presentation up](/miscellaneous/chattlaplus/) from the earlier version of this work. The dataset is the artifact that makes the paper reproducible — without it, the RL/SFT pipeline numbers are just claims. The companion repo with the TLC validator harness, reward-shaping config, and the GRPO/SFT scripts will go public alongside the camera-ready.

Anonymized repo: [chattla-dataset-anon](https://github.com/EricSpencer00/chattla-dataset-anon).

---

*Written with AI.*
