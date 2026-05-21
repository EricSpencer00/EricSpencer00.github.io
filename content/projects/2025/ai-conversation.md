---
title: "AIs Talking Philosophy"
date: 2025-07-31
description: "A toy where two local Ollama models loop on consciousness until one of them gives up"
tags: ["AI", "LLM", "Python"]
categories: ["Projects"]
draft: false
---

This is a toy. I wanted to see what would happen if I sat two local LLMs across from each other and made them talk about philosophy, so I wrote about 100 lines of Python that does exactly that. No agent framework, no fancy orchestration — just `ollama.chat` in a for loop.

Both AIs are the same model: `gemma:2b`, running locally through Ollama. I originally wanted to pair `llama2` and `mistral` so the "conversation" would actually have two voices, but they kept fighting for RAM on my laptop and one of them would die mid-turn, so I gave up and pointed both seats at gemma. There's still a `test_ollama.py` in the repo that hits both models with a hello — that's the leftover from when I thought this would be more sophisticated than it is.

The opening prompt is hardcoded: *"Hello, I am an AI. What are your thoughts on the nature of consciousness?"* From there one model answers, the other model gets a follow-up question shoved into its mouth (*"That's an interesting perspective. What do you think about the relationship between consciousness and intelligence?"*) and they trade for eight turns before the script exits. Transcripts get appended to a text file in `conversations/` named after the date.

The output is pretty much what you'd expect from a 2-billion-parameter model talking to itself about consciousness — a lot of "that's a fascinating question" and gentle re-statements of the previous turn. I don't want to oversell it. Gemma 2b is not Wittgenstein. But there's something funny about watching it loop, because the model genuinely doesn't seem to know it's the same model on both sides.

There's also a half-built pipeline in `chat.py` that was supposed to commit each day's transcript back to this repo at 3 AM UTC using PyGithub — so eventually the repo itself would be a slow-growing archive of two gemmas talking to themselves about qualia. I never actually deployed it anywhere with a `GITHUB_TOKEN` set, so the cron half is more aspiration than feature. If you want to run it on a Raspberry Pi for a week and PR the resulting transcripts, I would not stop you.

[GitHub Repo](https://github.com/EricSpencer00/ai-conversation)
