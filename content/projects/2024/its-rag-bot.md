---
title: "Loyola ITS RAG Bot"
date: 2026-01-24
description: "A voice-first RAG chatbot trained on Loyola's ITS knowledge base, built after two years of answering the same tickets."
tags: ["AI", "LLM", "RAG", "Python"]
categories: ["Projects"]
draft: false
image: "/previews/its-rag-bot.png"
---

I worked at Loyola's ITS Service Desk for two years (2024-2025), which means I have a fairly accurate mental picture of what an ITS ticket looks like. Roughly 70% of them are the same five questions — how do I connect to LUC-Secure, my Duo push isn't coming through, I can't get into Sakai, my printer credits don't show up, Outlook keeps re-asking me to sign in. The answers are all sitting in the public TeamDynamix knowledge base. People just don't read it, because reading a KB article when your laptop won't connect to the wifi is the last thing you want to do. You want to ask a person.

So I built a person. Or close enough — a voice-first RAG chatbot that pulls from Loyola's actual ITS KB and answers spoken questions out loud.

The stack is Python/FastAPI, FAISS for the vector index, sentence-transformers for embeddings, and Ollama running a local `llama3.1:8b` for inference when I don't want to burn HuggingFace credits. Speech-to-text is faster-whisper (I started on Vosk and switched — more on that below). TTS is Microsoft Edge's free voices via `edge-tts`. The ingestion script crawls `services.luc.edu/TDClient/33/Portal/KB/`, strips boilerplate with `trafilatura`, chunks the article text at ~900 chars with 120 of overlap, embeds each chunk, and dumps it all into a FAISS index that lives at `data/faiss/faiss.index`. Retrieval at query time is just a top-k similarity lookup that gets stuffed into the system prompt, no fancy reranker.

The whole thing runs in a Docker container. There's a `heroku.yml` for the deploy path I actually used — though Heroku can't run the local LLM, so on Heroku it falls back to a HuggingFace-hosted model (`tiiuae/zephyr-7b-instruct`) over the HF Inference API.

A few things were harder than I expected.

**Speech-to-text on technical jargon is rough.** Vosk handled normal English fine, but the moment someone said "Duo" or "LUC-Secure" or "Sakai" it would transcribe "duel" or "luxor" or "ski." I switched to faster-whisper, which is heavier but actually gets the proper nouns right most of the time. The trade is that cold-start on a laptop CPU adds a couple of seconds of latency, which is noticeable in a voice conversation. I considered fine-tuning on a small domain vocabulary but never did.

**Picking a vector store.** I bounced between Chroma (easy, but I didn't want a separate server process), Pinecone (overkill, and not free at the scale I needed), and FAISS (no server, just a file on disk). FAISS won by being the simplest thing that could possibly work. The downside is no built-in metadata filtering, so if I want to filter by KB category I have to do it in Python after the search.

**Local LLM latency on my MacBook is the bottleneck.** llama3.1:8b on Ollama answers in maybe 4-8 seconds for a typical query, which feels long when the user is sitting there listening for the speaker to start. The HuggingFace remote path is faster but rate-limited, and I didn't want to assume people had API keys. I added an engine dropdown so you can pick.

The last rabbit hole was a full-duplex voice mode using NVIDIA's PersonaPlex 7B speech-to-speech model. The idea was no separate STT/TTS step — the model just hears you and talks back. It's the kind of thing that's amazing when it works and a giant pain otherwise. I got it loading on Apple Silicon via MPS, then tried `moshi-mlx`, then ran into the fact that the `moshi-personaplex` package pins `torch<2.5` which means you're locked to Python 3.11. The commits from April are mostly me trying to make it work — "wait personaplex won't work" is a real commit message. It's still in the repo as an optional engine, and the cascaded mode (Whisper → LLM → Edge TTS) is the default.

It did not get adopted by ITS. I didn't actually pitch it — by the time I had a version I was proud of, I had graduated and was no longer on the team. It's a personal project that solves a problem I lived inside for two years, which is its own kind of useful. If a current student desker wanted to fork it and pitch it to Loyola, the ingestion script will pick up whatever's currently on the TDX portal — the KB hasn't changed structure since I left.

What's next, if I come back to it: scoping the retrieval to a single school (e.g. only return Sakai articles when the question is clearly about Sakai), better handling of the "I need a human" escape hatch, and possibly a hosted demo so people can try it without `pip install`-ing 15 GB of torch wheels.

[GitHub Repo](https://github.com/EricSpencer00/ITS-RAG-bot)
