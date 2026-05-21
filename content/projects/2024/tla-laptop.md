---
title: "TLA+ Model of a Laptop"
date: 2025-11-27
description: "A formal TLA+ specification modeling a laptop's power states, battery, lid, thermals, and auto-suspend."
tags: ["formal methods", "TLA+"]
categories: ["Projects"]
draft: false
image: "/previews/default-project.png"
---

Another small TLA+ spec in the same family as the [walk-in oven](/projects/2024/tla-walk-in-oven/) and the [interactive microwave](/projects/2025/interactive-microwave-tla/) — if you've never touched TLA+, the microwave page is the gentler introduction. This one models a laptop. Not a real laptop, obviously, but a small mechanical abstraction of one: power button, lid, charger, display, brightness, wifi, bluetooth, CPU mode, temperature, fan, sleep timer. The point is to write down all the things that can change and all the rules for how they change, then ask TLC whether anything bad can happen.

The repo is at [https://github.com/EricSpencer00/tla-laptop](https://github.com/EricSpencer00/tla-laptop).

## What's in the spec

The state is twelve variables plus a `phase` flag that flips between `"user"` and `"tick"`. The phase split is a trick — user actions (pressing the power button, opening the lid, toggling wifi) only fire in the user phase, and the ambient ticks (battery draining, temperature rising, the auto-suspend countdown) only fire in the tick phase. Without it the model can do a user action and a thermal tick in the same step, which makes counterexamples annoying to read.

Power has three states: `off`, `on`, `suspend`. The interlocks I cared about:

- Closing the lid on a laptop that's `on` puts it into `suspend` and turns the display off.
- Opening the lid on a `suspend` laptop wakes it back to `on` and the display comes back on. If it was already `off`, the lid does nothing to power.
- Pressing the power button toggles between `off` and `on`, and `suspend` → `on`.
- If the laptop is `on` with the display `off`, the sleep timer counts up, and once it crosses `SleepTimeout` the `AutoSuspend` action fires.

Battery and thermals are the messy bits. `TickBatteryAndTimer` does battery accounting: charge if plugged in (capped at `BatteryMax`), drain by `DisplayDrain` if the display is on, `IdleDrain` if it's off but the laptop's on, `SuspendDrain` if suspended. `ThermalTick` makes temperature rise by 1–3 depending on CPU mode and fall by the fan speed, clamped at `ThermalMax`.

## What it's checking

Three invariants in `laptop.cfg`:

- `BatteryRange` — battery stays inside `0..BatteryMax`
- `TempRange` — temperature never exceeds `ThermalMax`
- `FanRange` — fan stays inside `0..FanMax`

And one liveness property left as an option in the config:

```
PROPERTY == <> (power = "on" /\ lid = "open" /\ display = "on")
```

i.e. eventually the laptop ends up in the "actually being used" state. Useful as a sanity check that I haven't written a spec where the only reachable behavior is the lid staying shut forever.

## Honest scope

This is a personal study spec, not class work and not part of any research. After doing the walk-in oven I wanted to try something with more variables and a non-trivial ambient process (the battery and thermal dynamics) instead of just safety interlocks. I left two configs in the repo: `laptop.cfg` is the full one and `laptop_small.cfg` cuts every constant down (`BatteryMax = 4`, `MaxBrightness = 3`, `FanMax = 2`) so TLC actually finishes in a reasonable time on a laptop modeling a laptop. The state space blows up fast once you start parameterizing brightness and fan speed as integers.

If you run it and get a counterexample I haven't seen, open an issue — half of why I keep doing these is to find the dumb action I forgot to constrain.
