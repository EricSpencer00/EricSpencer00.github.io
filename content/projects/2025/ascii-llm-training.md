---
title: "Training an LLM on ASCII"
date: 2025-09-03
description: "A toy transformer that reads pyfiglet ASCII art and tries to spit the original word back out. Calling it an LLM is generous."
tags: ["AI", "LLM", "Python", "AI-written"]
categories: ["Projects"]
draft: false
---

I wanted to see what would happen if I trained a small transformer on ASCII art. Not generating it — reading it. You give the model a chunk of `pyfiglet`'s blocky text rendering of some random word, and it has to recover the word. So less of an LLM and more of a text-only OCR experiment with a transformer encoder bolted on. But "training an LLM on ASCII" sounds way cooler than "training a character classifier on pyfiglet output," so that's what I called the repo.

The pipeline is four scripts. `ascii_generator.py` picks a random lowercase word between 3 and 12 characters long, runs it through `pyfiglet` in a chosen FIGlet font (default `standard`, or sample from a curated list of fonts like `slant`, `3-d`, `doh`, `isometric1`, `bubble` if you pass `--multi-font`), and dumps the (word, art, font) triples into a JSONL file. `data_prep.py` builds two tiny vocabularies — one for the characters that show up in the rendered art, one for the 26 lowercase letters plus a `<pad>` token — and converts everything into padded numpy arrays. `train.py` runs the transformer. `evaluate.py` loads a checkpoint and prints predictions.

The model itself is small. PyTorch's `nn.TransformerEncoder` over the flattened ASCII art token sequence, default 4 layers, `d_model=192–256`, 8 heads, 512-dim feedforward. The flattened sequence can be ~1200 tokens long because ASCII art is wide. The encoder outputs get mean-pooled into one vector, which gets projected to `target_vocab_size * MAX_WORD_LEN` and reshaped — so it predicts all 12 character positions at once instead of decoding autoregressively. Cross-entropy with `ignore_index=PAD` on the target side. Mostly because I wanted to keep the model simple and not deal with a decoder loop for what should be an easy task.

```python
self.classifier = nn.Linear(d_model, target_vocab_size * max_word_len)
# ...
pooled = enc_out.mean(dim=1)
logits = self.classifier(pooled).view(-1, self.max_word_len, self.target_vocab_size)
```

For the `standard` font on single-font data, this works pretty well — the model converges in a handful of epochs and gets high per-character accuracy on held-out words it has never seen. Which makes sense, because the standard FIGlet font is a deterministic letter-by-letter rendering, so the model is basically learning to segment the art into per-letter columns and then classify each column. It's not really doing language modeling, it's doing very fancy template matching.

Where it falls apart is multi-font. Once you mix `doh` and `isometric1` and `banner3-D` into the same dataset, the model has to learn each font's quirks (variable letter width, ASCII characters that bleed across positions, fonts that draw the same letter completely differently) and a 4-layer encoder with a few thousand samples just isn't enough. Exact-match accuracy drops hard. The right move would be a proper sequence-to-sequence decoder, or CTC loss so the model doesn't need to know where each letter starts and ends, or just way more data and a bigger model. I noted all of that in the README's "Future Ideas" section and then didn't do any of it.

This was a one-weekend curiosity project. It does not produce a usable model and it does not generate ASCII art (the inverse direction is much harder and much more interesting — maybe next time, when I have extra Claude credits to burn). But it was a fun excuse to write a small transformer from scratch with PyTorch and remember how `TransformerEncoderLayer` works.

[GitHub Repo](https://github.com/EricSpencer00/ascii-llm-training) — fork it if you want to try the seq2seq version.

---

*Written with AI.*
