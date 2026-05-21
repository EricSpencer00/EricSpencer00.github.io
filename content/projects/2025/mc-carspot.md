---
title: "mc-carspot: Online Parking Simulation in Rust"
date: 2025-08-22
description: "A tiny Rust simulator for the online parking-spot problem with switching costs."
tags: ["Rust", "AI-written"]
categories: ["Projects"]
draft: false
---

[GitHub Repo](https://github.com/EricSpencer00/mc-carspot)

This is a small Rust program I wrote in one sitting to play with the online parking-spot problem — you're parked somewhere on a street, closer spots open up as time goes on, and every time you decide to move the car you eat a switching cost. The question is whether the walk you save is worth the move, and over a sequence of events what policy minimizes total cost. It's a classic toy from the online algorithms / metrical task systems world, which is where the "mc" in the name comes from (metrical cost). Felt like a more fun way to revisit the material than rereading lecture notes.

The whole thing is about 70 lines in `src/main.rs`. There's an `Env` struct that holds the number of spots, the per-step walk cost, the move cost, and a vector of distances. Each tick, some spots randomly become available (`rng.gen_bool(0.3)`), and the policy decides whether to stay or move to the closest open one. The default policy is a threshold rule: move only if `(dist_cur - dist_new) * walk_cost * expected_uses > move_cost`. In other words, the expected walking savings has to clear the move cost. It also includes the trivial baselines — always stay, always move — so you can compare.

Only dependency is `rand`. The whole `Cargo.toml` is six lines. It prints a little table to stdout showing the spot, the action, the per-step cost, and the running total. That's it — no plotting, no CSV export, no fancy policies. Configuration is "edit `src/main.rs` and recompile," which is honest about what this is.

If I came back to it I'd probably add a couple more policies (dynamic programming for the offline optimum, maybe a small RL agent for comparison) and dump runs to CSV so I could plot regret curves in Python. Right now it's really just a sandbox — one commit, one file, no tests — but it does what it says on the tin. If you want to drop in your own policy and see how it stacks up, the `should_move` function is the obvious place to start.

---

*Written with AI.*
