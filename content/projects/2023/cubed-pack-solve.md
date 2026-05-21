---
title: "Cubed Pack Solver"
date: 2025-12-26
description: "A solver for packing 54 T-tetracubes into a 6x6x6 cube using Knuth's Dancing Links algorithm."
tags: ["Python", "Three.js", "Algorithms"]
categories: ["Projects"]
draft: false
image: "/previews/default-project.png"
---

This is one of those projects I pick up when I have extra Claude Credits lying around and feel like burning them on something that has no business being useful. The whole thing started because I bought [this wooden puzzle on Amazon](https://www.amazon.com/dp/B09H28271W) — 54 identical T-shaped blocks that supposedly pack into a 6×6×6 cube. I got it apart, failed to get it back together, and decided the dignified response was to write a solver instead of trying again.

A T-tetracube is four unit cubes arranged in a T. Fifty-four of them is exactly 216 unit cells, which is exactly a 6×6×6 cube, so the arithmetic at least lines up. The hard part is everything else.

I solved it using [Knuth's Dancing Links](https://en.wikipedia.org/wiki/Dancing_Links) — also called DLX, or Algorithm X. The short version: you turn the packing question into a giant binary matrix where rows are "this piece in this position and orientation" and columns are "this cell of the cube must be covered exactly once." Then you recursively pick rows that cover all the columns without overlap, using a doubly-linked list trick that lets you remove and reinsert rows and columns in O(1). It's one of those algorithms that feels like cheating the first time you implement it.

For this puzzle the DLX matrix is 1440 rows by 216 columns. The T-tetracube has 12 distinct 3D orientations (you'd expect 24 from the cube rotation group, but the T's own symmetry collapses half of them), and each orientation has somewhere on the order of a hundred legal anchor positions inside the cube. A valid solution is any 54 rows that cover every column exactly once.

The annoying part of any combinatorial puzzle like this is that the solver will happily count the same arrangement 24 times — once for each rotation of the cube itself. So for every solution it finds, I rotate it through the full 24-element cube rotation group, take the lexicographically smallest version as the canonical form, and dedupe against that. What you're left with is the count of *genuinely distinct* tilings, modulo rotational symmetry.

On my machine it churns out something like 40 solutions per second before dedup, and I'll be honest, I haven't let it run to completion. Full enumeration is hours-to-days and I have not had the spare CPU budget (or the patience) to find out exactly how many there are.

The other half of the project is a Three.js viewer that loads the precomputed solutions and lets you orbit around the cube, explode the pieces apart, toggle wireframe, and walk through solutions one at a time. It's the part that's actually fun to look at. You can try it here: [ericspencer00.github.io/cubed-pack-solve](https://ericspencer00.github.io/cubed-pack-solve/).

Source is on GitHub: [https://github.com/EricSpencer00/cubed-pack-solve](https://github.com/EricSpencer00/cubed-pack-solve). If you've got a free weekend and want to let it run to completion, please tell me how many solutions there actually are.
