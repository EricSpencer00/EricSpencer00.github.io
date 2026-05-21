---
title: "Rubik's Snake — Formally Verified"
date: 2026-05-20
description: "Coq (Rocq) and TLA+ specifications of the Rubik's Snake state space — 4^23 configurations, formally"
tags: ["Formal Methods", "Coq", "TLA+", "AI-written"]
categories: ["Projects"]
draft: false
image: "/previews/default-project.png"
---

[GitHub Repo](https://github.com/EricSpencer00/rubix-snake-puzzle)

I bought a Rubik's Snake at some point and spent way too long folding it into a ball, a dog, and then back into a stick. It is 24 right-triangular prisms strung together on a chain, with 23 joints between them, and each joint clicks into one of four positions (0°, 90°, 180°, 270°). That gives you 4^23 = 70,368,744,177,664 possible configurations if you ignore physics, and somewhere around 13.4 trillion if you actually require that the wedges not pass through each other. Peter Aylett did the exhaustive backtracking search in C in 2011 (and patched it in 2022). I wanted to ask the same question with formal methods instead of brute force, partly because I've been pulling on the AI-for-formal-methods thread for a while and partly because nobody had done it.

This repo is the first formal verification of the Rubik's Snake puzzle in any proof assistant — Coq, Lean, Isabelle, Alloy, TLA+, none of them. That was honestly the most surprising thing I found while writing the related-work section. The puzzle has a Wikipedia page and a small academic literature (Hou/Chen/Li wrote a couple of papers on it in *J. Mechanisms and Robotics*, and the Luxembourg group has a nice characterization of which Eulerian paths give you planar configurations), but the formal-methods community had not touched it.

## What's in the repo

Two specifications and a Python reference enumerator:

- **`coq/`** — Coq (now Rocq) formalization. Defines wedges as triangular prisms in a 3D integer grid, joints as one of four rotations, and the validity predicate (`no_collision`) that says no two wedges occupy overlapping voxels. Proves structural properties — decidability of equality on rotations, completeness of the rotation enumeration, well-formedness of the snake-construction function. The interesting work is the geometry: an `apply_rotation` that takes a `Direction` (one of six axis-aligned 3D directions) and a `Rotation` and gives you the next wedge's position and orientation.
- **`tla/`** — TLA+ spec that models the snake as a state machine. Each action is "pick a joint and rotate it." The invariant is `NoSelfIntersection`. You can run TLC on small instances (8-wedge snakes finish in seconds; the full 24 is way past what TLC can model-check, which is part of the point — you need Coq for the general claim and TLA+ for the small concrete confidence-building).
- **`python/`** — A reference enumerator I used to sanity-check the formal specs against Aylett's numbers. For 8 wedges I get the same valid-configuration count he does, which made me feel less likely to have a bug in the wedge geometry.

The Coq file opens with this, which I think is the cleanest summary of what's going on:

```coq
(* Each joint has 4 possible rotations: 0°, 90°, 180°, 270° around the shared edge. *)
Inductive Rotation : Type :=
  | R0   (* 0°   — straight *)
  | R90  (* 90°  — right angle *)
  | R180 (* 180° — folded back *)
  | R270 (* 270° — left angle *).
```

The whole thing is built on a 3D integer grid with 6 axis-aligned directions, which means I do not have to deal with floating-point rotation matrices in the proof — everything is `Z`-arithmetic, and Lia can close most of the arithmetic obligations.

## What I did not do (yet)

I have not proved the count. Aylett's number (13,446,591,920,995 valid configurations) is established by exhaustive search, and proving it formally in Coq would require either reflecting the enumerator into Gallina and computing it (impractical — the search took weeks of CPU time in C) or finding a clever combinatorial argument that nobody has found yet. What I have is the formal *specification* of what a valid configuration is. The bridge from spec to count is still empirical.

I also have not fully worked out the symmetry quotient (mirror + cyclic) that Aylett applies to drop the count from 13.4T to 6.7T. The TLA+ spec does not have it at all; the Coq side has a stub.

## Why this exists

It's a hobby-scale formal verification project. Small enough to actually finish, weird enough to be the first of its kind, and connected to the AI-for-formal-methods (ai4fm) work I've been doing on the side. If you wanted a project to learn Coq on that is not yet another "verify insertion sort," the geometry of a physical puzzle is a nice change of pace. The state space is huge but every individual piece of reasoning is concrete — you can hold the puzzle in your hand and check the math.

If you want to play with it, the README has build instructions for Coq 8.18+ / Rocq and the TLA+ Toolbox. PRs welcome, especially on the symmetry reduction or if you have an idea for how to prove the count without exhaustive search.

---

*Written with AI.*
