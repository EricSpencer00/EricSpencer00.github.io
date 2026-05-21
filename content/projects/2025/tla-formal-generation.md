---
title: "TLA+ Formal Generation"
date: 2025-09-21
description: "Early exploratory repo for generating TLA+ specs from natural-language requirements with an LLM, with a TLC harness wired in. The scaffold that eventually grew into ChatTLA+."
tags: ["TLA+", "AI", "LLM", "Formal Methods", "Research"]
categories: ["Projects"]
draft: false
---

This is the first thing I built when I started poking at "can an LLM write TLA+ for you" inside the ai4fm research thread at Loyola. It's small, scrappy, and very much a scaffold — the point was to get an end-to-end loop running (English requirement -> generated `.tla` module -> TLC actually checks it) before worrying about whether the generations were any good. The polished version of this idea is the [ChatTLA+ dataset and paper](/miscellaneous/chattla-dataset/) I shipped later. This repo is what came first.

The shape of it: a tiny [benchmark](https://github.com/EricSpencer00/tla-formal-generation/blob/main/data/benchmark.jsonl) of three NL-to-invariant examples (semaphore non-negativity, boolean domain, upper-bound counter), a template `.tla` file with `{{module}}` / `{{vars}}` / `{{invariant}}` holes, a Python generator that fills those holes either with a real LLM call or a deterministic stub, and an evaluator that runs the resulting module through TLC and reports whether the invariant held, was violated, or the toolchain blew up. Plus a shell script that downloads `tla2tools.jar` so you can actually run TLC locally without fighting with Java for an afternoon.

The generator is honest about its limits. If `OPENAI_API_KEY` is set, it calls GPT-4 with a one-shot prompt — `"Translate this English requirement into a TLA+ invariant expression only"` — and uses whatever comes back. If the key isn't set, it falls back to `stub_generate`, which just returns the ground-truth invariant from the benchmark row. That stub is not cheating, it's a feature: it lets the rest of the pipeline (template rendering, TLC invocation, eval) be tested deterministically without an API call. But it also makes the "evaluation" results not mean much when the stub is on, which is most of the time.

```python
def stub_generate(item):
    if 'expected_invariant' in item:
        return item['expected_invariant']
    nl = item.get('nl', '').lower()
    if 'semaphore' in nl or 'counter' in nl:
        if 'below 0' in nl or 'non-neg' in nl:
            return 'counter >= 0'
    ...
```

The eval is similarly naive — string-equality between the generated invariant and the expected one, plus a "did TLC say `Invariant Inv is violated` or `No error has been found`" check. That works for three examples. It does not scale to anything you'd actually want to claim. I knew that going in. The goal was to convince myself that "generate a `.tla`, run TLC on it, parse the verdict" was a tractable feedback loop, because if it wasn't, the whole RL-on-spec-generation idea was dead.

It was tractable. Which is why a few months later I rebuilt the whole thing properly — a real 209-row SFT corpus filtered by TLC-verified outputs, a 30-problem held-out benchmark across six domains, semantic reward shaping (state coverage, action coverage, mutation-kill rate), and the GRPO/SFT pipeline that became ChatTLA+. That work is under double-blind review at ICSOFT 2026; the [anonymized dataset repo](/miscellaneous/chattla-dataset/) is up.

Looking at this older repo, the things it got right and the things it got wrong are both useful. Right: separating "render TLA from a template" from "call the LLM" from "run TLC and parse output," so you can swap any one of those without touching the other two. Right: shelling out to a real `tla2tools.jar` instead of trying to fake TLC's behavior — TLC's verdicts are the whole point, you don't want to mock the oracle. Wrong: a 3-row benchmark with hand-written ground-truth invariants encourages you to test on the same problems you'd solve by lookup, and the deterministic stub will happily exploit that. Wrong: matching invariant strings instead of checking semantic equivalence under TLC — `counter >= 0` and `counter \in Nat` are the same property but `==` says no. The ChatTLA+ work fixed both of those by validating against TLC directly and scoring by behavioral metrics rather than string match.

If you want to see the pipeline, it's at [EricSpencer00/tla-formal-generation](https://github.com/EricSpencer00/tla-formal-generation). It's a useful starting point if you're building something similar — the structure of `generate -> template -> TLC -> parse` is the right one — but the benchmark and the eval need to be much heavier before you can say anything real with it.
