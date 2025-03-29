+++
title = "Binary Bomb Puzzle"
date = 2023-11-01
description = "Solving the infamous Binary Bomb Lab for extra credit."
draft = true
images = ["/images/bomb/bbomb.gif"]
+++

![Bomb GIF](/images/bomb/bbomb.gif)

## Overview

During my Fall 2023 semester, I had an extra credit assignment for my Introduction to Computer Systems class that had me solve a Binary Bomb Puzzle. This led me to gain skills such as debugging assembly, converting it into high-level code, and tracking data in registers.

📄 [Bomb Lab Instructions (Carnegie Mellon)](http://csapp.cs.cmu.edu/public/bomblab.pdf)

---

## Phase 1

Commands used:
- `strings`
- `objdump`
- `gdb`
- `disas`
- `nexti`
- `info registers` / `i r`

Run:

    strings bomb > strings.txt

[Notable Strings](/images/strings.txt.html)

![Phase 1 Strings](/images/bomb/BBPhase1Strings.png)

Then:

    objdump -d bomb > bomb.asm

![Assembly Output](/images/bomb/BBPhase1Assembly.png)

Use GDB and:

    disas

![GDB Debug 1](/images/bomb/BBPhase1GDBDebug1.png)  
![GDB Debug 2](/images/bomb/BBPhase1GDBDebug2.png)

Save answer:

    echo "Verbosity leads to unclear, inarticulate things." >> answers.txt
    run answers.txt

---

## Phase 2

Key function: `read_six_numbers`

Answer:

    1 2 6 24 120 720

![Phase 2 Assembly](/images/bomb/BBPhase2Assembly.png)  
![Read Six Numbers](/images/bomb/BBPhase2ReadSixNumbers.png)  
![Phase 2 Complete](/images/bomb/BBPhase2Complete.png)

---

## Phase 3

Answer format: two integers

    3 811

![Phase 3 Assembly](/images/bomb/BBPhase3Assembly.png)  
![Info Reg](/images/bomb/BBPhase3InfoReg.png)  
![Register Data](/images/bomb/BBPhase3Register.png)

📚 [Side-channel attacks](https://en.wikipedia.org/wiki/Side-channel_attack)

---

## Phase 4

Single integer input:

    15

---

## Phase 5

    55 93

---

## Phase 6

Permutations of `1 2 3 4 5 6`

![Phase 6 Assembly](/images/bomb/BBPhase6Assembly.png)  
![Helper Function](/images/bomb/BBPhase6FuncAssembly.png)

⛔ Got through ~45% of 720 possible combos before my brain melted.

![Brain Rot](/images/bomb/BrainRot.png)

---

## Secret Phase

Triggered by `austinpowers` (after Phase 6)

More in [strings.txt](strings.txt.html)

---

## Final Answers

1. Verbosity leads to unclear, inarticulate things.  
2. 1 2 6 24 120 720  
3. 3 811  
4. 15  
5. 55 93
