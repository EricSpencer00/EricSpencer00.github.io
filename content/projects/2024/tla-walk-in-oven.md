---
title: "TLA+ Model of a Walk-In Oven"
date: 2025-12-12
description: "A formal TLA+ specification of a walk-in industrial oven with a focus on safety interlocks."
tags: ["formal methods", "TLA+", "AI-written"]
categories: ["Projects"]
draft: false
image: "/previews/default-project.png"
---

This is one of a handful of small TLA+ specs I wrote while picking real-world industrial control systems and asking "what's the minimum state machine that makes this thing not kill someone?" It sits next to my [laptop power-state spec](/projects/2024/tla-laptop/) and my [Dexcom G7 spec](/projects/2024/tla-dexcom-g7/) — same flavor, different system. A walk-in oven is the one I find most fun to think about because the failure mode is so concrete: a person physically walks inside a room-sized oven, and then the oven heats up.

If you've never seen TLA+ before, the [interactive microwave](/projects/2025/interactive-microwave-tla/) page is a gentler introduction. The short version: you describe a system as a set of variables, a set of actions that change those variables, and an invariant that should hold in every reachable state. Then the TLC model checker explores every possible execution and tells you whether the invariant ever breaks. The win is that "every possible execution" includes the weird ones a human would never think to test — the off-by-one ordering of events that turns out to be the bug.

## What the spec actually models

A walk-in oven (the kind used for curing coatings, drying lumber, baking large food batches) is essentially a room with a heating element and a door. The dangerous configuration is straightforward: a human is inside, and the temperature is above ambient. The spec tracks three variables — `temp`, `door`, and `inside` — and six actions: `Heat`, `Cool`, `OpenDoor`, `CloseDoor`, `Enter`, `Exit`.

The interlock that does the real work is on `Enter`:

```
Enter ==
    /\ door = "open"
    /\ inside = FALSE
    /\ temp = MinTemp
    /\ inside' = TRUE
    /\ UNCHANGED <<temp, door>>
```

A person can only step inside if the door is open AND the oven is at `MinTemp`. And then the safety invariant the model checker is actually trying to falsify is:

```
Inv4 == inside => temp = MinTemp
```

If at any reachable state someone is `inside` and the temperature is above minimum, TLC reports a counterexample with the exact trace that got there. With this spec as written, it doesn't — `Heat` is guarded on `inside = FALSE`, so the heating element can never even turn on while someone is in the chamber. That's the whole point: encode the interlock and let the checker confirm no path violates it.

## The unsafe sequence it's catching

The real-world bad story this is modeling is the obvious one: tech walks in to check or clean the chamber, door swings shut, controller resumes its program, and the chamber heats while someone is inside. Walk-in ovens have actual physical interlocks and lockout-tagout procedures to prevent this. What the spec does is express those interlocks at the level of "no reachable state has `inside` true and `temp` above minimum" and let TLC prove it. If you weaken any of the guards — say, drop the `inside = FALSE` precondition on `Heat` — the checker will immediately produce a trace showing exactly how a person ends up cooked.

## Scope, honestly

This is a study spec, not a verified industrial controller. The temperature is a single integer ticking up and down by one, there's no notion of multiple people, no ventilation, no emergency stop, no temperature sensor failure, no door-stuck-open behavior. The config (`TargetTemp = 20`, `MaxTemp = 100`, `MinTemp = 0`) is dimensionless — the point is to give TLC a finite state space to actually explore, not to model real Celsius. The whole module is under 90 lines and the README is one sentence long. I wrote it as part of the same arc of work that led into my [ai4fm research](https://ai4fm.cs.luc.edu) on getting LLMs to generate TLA+, and it doubles as one of the example systems I keep in my back pocket when explaining to someone what TLA+ actually buys you on a system they can picture.

The repo is at [EricSpencer00/tla-walk-in-oven](https://github.com/EricSpencer00/tla-walk-in-oven) — the spec is [Oven.tla](https://github.com/EricSpencer00/tla-walk-in-oven/blob/main/Oven.tla) and the config that feeds it to TLC is [Oven.cfg](https://github.com/EricSpencer00/tla-walk-in-oven/blob/main/Oven.cfg). If you have the TLA+ Toolbox or `tla2tools.jar` installed, it runs in seconds.

---

*Written with AI.*
