---
title: "COMP 388 LLM Homework"
date: 2026-04-23
description: "Two homeworks from Loyola's special-topics LLMs class: prompting GPT-2 and comparing base vs instruction-tuned Qwen."
tags: ["AI", "LLM", "Python", "AI-written"]
categories: ["Projects"]
draft: false
image: "/previews/default-project.png"
---

COMP 388 at Loyola is the special-topics CS course — whatever the professor wants to teach that semester. The Spring 2026 version was on large language models, which lined up nicely with the TLA+ and fine-tuning work I've been doing at ai4fm. So most of the homework felt less like homework and more like a structured excuse to poke at things I was already curious about. This repo holds the two assignments I actually saved.

### HW1 — prompting GPT-2 and a tiny evaluation

The first assignment was the "hello world" of loading a Hugging Face model and running it. The script (`llm_prompt.py`) loads `gpt2` via `transformers`, takes a prompt off the command line, and does manual token-by-token generation instead of calling `.generate()`. The reason for that is annoying: on my M1 Mac, calling `.generate()` would crash with a bus error half the time, and so would single-word prompts. I ended up forcing CPU-only, setting `PYTORCH_ENABLE_MPS_FALLBACK=1`, and writing my own sampling loop just to get reliable runs.

Then the assignment asked for a "simple evaluation," which I did two ways:

- A hand-rolled True/False dataset of 10 Wikipedia-style facts (`evaluate_wiki_tf.py`). GPT-2 got 6/10. Every one it got wrong was a false statement that it confidently called true.
- BoolQ from Hugging Face datasets, 20 examples, run twice — once with the supporting passage and once without (`evaluate_boolq.py`). Both runs got 45.0%. Identical. Looking at the outputs, GPT-2 was basically answering "yes" to everything, so the passage didn't matter.

Not a deep result, but it was the first time I'd watched a small model fail in a clearly characterizable way rather than just "be bad."

### HW2 — base vs instruction-tuned, and few-shot

The second assignment was the more interesting one. The task was to pick a small open model that ships both a base and an instruction-tuned variant, compare them, and then try few-shot prompting on the base model. I used Qwen2.5-0.5B and Qwen2.5-0.5B-Instruct — same architecture, same tokenizer, only difference is the instruction-tuning step.

The base-vs-chat comparison was textbook: the base model treats your prompt like a document to continue ("What is the capital of France?" → it generates more questions or bullet points), and the chat model just answers "The capital of France is Paris." Fine.

The evaluation was on SNLI (natural language inference), 100 examples, greedy decoding:

| Configuration            | Accuracy |
|--------------------------|----------|
| Chat model (zero-shot)   | 61%      |
| Base model (zero-shot)   | 64%      |
| Base model (few-shot)    | 61%      |

The base model beating the chat model zero-shot was not the expected outcome. And few-shot made it *worse*, not better. My read is that at 0.5B the instruction tuning is overfitting to chatty response shapes that hurt on a constrained-label task like NLI, and the few-shot prompts inflate the context enough that the small model loses the plot. I also hit CPU/memory ceilings on the few-shot run because the in-context examples triple the prompt length — a GPU or a quantized model would've finished cleanly.

### What it's good for

It's coursework, not a product. But the HW2 result — small instruction-tuned model getting beaten by its base on a classification task — has stuck with me and is the kind of thing I think about when picking models for the ai4fm fine-tuning work. The whole repo is honest about the constraints: pinned to Python 3.11, macOS M1, CPU-only, hardcoded paths because the assignment template wanted it that way.

[GitHub Repo](https://github.com/EricSpencer00/comp388-llm)

---

*Written with AI.*
