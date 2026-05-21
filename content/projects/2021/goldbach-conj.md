---
title: "Goldbach Conjecture"
date: 2025-11-28
description: "Verifying the Goldbach Conjecture by brute force for every even number up to 1 billion."
tags: ["Python", "Math"]
categories: ["Projects"]
draft: false
image: "/previews/goldbach-conj.png"
---

Goldbach's conjecture is the kind of math problem that's easy to state and apparently impossible to prove. Every even integer greater than 2 is the sum of two primes. 4 = 2 + 2. 100 = 3 + 97. 1,000,000,000 = 3 + 999,999,997. It's been open since 1742 and nobody has cracked it. So I figured I'd at least watch a computer not find a counterexample.

This started over a long weekend in late November 2025. I'd been reading something that referenced the conjecture, realized I'd never actually checked it for myself, and decided to write a verifier from scratch. The plan was to start small — first a million, then see how far I could push it before my laptop or my patience gave out. I ended up at one billion.

The whole thing is two short Python files. The first, `goldbach_check.py`, builds a sieve of Eratosthenes as a `bytearray` and then walks every even number `n` from 4 to the cap, looking for any prime `p ≤ n/2` such that `n - p` is also prime. As soon as it finds one, it moves on. If it ever fails to find one, it prints the counterexample and bails out. The sieve part is the obvious trick — once you have a fast primality lookup, the rest is just a tight loop:

```python
for n in range(4, max_n + 1, 2):
    found = False
    for p in primes:
        if p > n // 2:
            break
        if prime_set[n - p]:
            found = True
            break
    if not found:
        # counterexample — this never fires
        return False
```

At 1,000,000 the verifier finishes in about 0.224 seconds and prints the first ten decompositions as a sanity check. Easy. The second file, `generate_thru_n.py`, reuses the same sieve but instead of stopping at a "yes/no" answer it writes out every decomposition it finds to a text file. That's the one I pushed to 1 billion. It took 470 seconds — call it just under eight minutes — and produced a 12.38 GB text file that VS Code politely refused to open. The screenshot in the repo is literally VS Code throwing up its hands at the file size while the progress log scrolls past in the terminal.

No counterexamples. Which is the boring expected outcome, because the conjecture has been computationally verified well past 4×10^18 by people with actual compute budgets. This is the point I want to be honest about: this is not a proof. It's a verification, and verification is not proof in number theory. The conjecture is still open. All I've done is confirm, on my own machine, that the first billion even integers all behave. Goldbach himself wrote about this in 1742 in a letter to Euler and nobody has closed it since. I'm not closing it either.

Why Python instead of something faster? Honestly, because I wanted to write it in one sitting and didn't want to fight a compiler. The sieve is the hot path and `bytearray` makes it cheap enough that the bottleneck for the 1B run is mostly disk I/O writing the output file. If I cared about pushing past 1B I'd skip writing the decompositions to disk and probably reach for Rust with parallelized segmented sieving. If anyone wants to fork this and grind it up to 10^10 or 10^11 — please do, the [repo is here](https://github.com/EricSpencer00/goldbach-conj) and the code is short enough to be its own spec.
