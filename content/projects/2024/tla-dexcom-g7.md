---
title: "TLA+ Model of Dexcom G7"
date: 2025-11-12
description: "A formal TLA+ specification of the Dexcom G7 continuous glucose monitor's behavior and safety properties."
tags: ["formal methods", "TLA+"]
categories: ["Projects"]
draft: false
image: "/previews/default-project.png"
---

I'm a type 1 diabetic and I wear a Dexcom G7. It's the small white disc on the back of my arm that reads my blood sugar every five minutes and yells at my phone when something's wrong. I've already built a bunch of stuff around it — DexVal, GluCoPilot, a macOS menu bar icon that just shows the current number — but I'd never actually tried to write down what the device is *supposed* to do. So I wrote a TLA+ spec for it.

This is one of three TLA+ specs I put together alongside my [walk-in oven]({{< ref "/projects/2024/tla-walk-in-oven" >}}) and [laptop]({{< ref "/projects/2024/tla-laptop" >}}) models. If you've never touched TLA+ before, my [interactive microwave]({{< ref "/projects/2025/interactive-microwave-tla" >}}) page is a friendlier on-ramp.

[GitHub Repo](https://github.com/EricSpencer00/tla-dexcom-g7)

## What the spec models

The G7 is a sensor plus a transmitter that lives on your arm for ten days. There's a 30-minute warmup after you insert it, then it samples your glucose every five minutes, transmits over BLE to a receiver (your phone, usually), and the receiver decides whether to fire a high or low alert. After 10 days the sensor enters a 12-hour grace period and then expires.

`g7.tla` models all of that as a state machine. The state variables look like:

```
VARIABLES
  now,            \* elapsed minutes since sensor insertion
  sensorState,    \* "NotInserted" | "Warmup" | "Active" | "Expired"
  lastSample,     \* most recent sample produced by the sensor
  receiverStore,  \* sequence of samples stored on the receiver
  connected,      \* BLE connection status
  alerts          \* { high: BOOL, low: BOOL }
```

The actions are the things the device can do: `InsertSensor`, `FinishWarmup`, `ProduceSample`, `ConnectOrDisconnect`, `TransmitSample`, `UpdateAlerts`, `ClearAlerts`, `ExpireSensor`, and a `Tick` that just advances `now` by one minute. Transmission is nondeterministic — packets can be delivered or dropped — because in real life my phone is in the other room half the time and the BLE link is a guess at best.

There are two config files. `g7.debug.cfg` shrinks everything (lifetime = 10 minutes, glucose values 80–82) so TLC can finish in a second. `g7.realistic.cfg` uses real numbers: 30-minute warmup, 10-day lifetime, 12-hour grace, glucose range 40–400. The realistic one explodes the state space, as you'd expect.

## The invariant that actually matters

The safety property I care about is `NoReadingsAfterExpiry`:

```
NoReadingsAfterExpiry ==
  \A i \in 1..Len(receiverStore) :
     receiverStore[i].time <= LIFETIME_MINS + GRACE_MINS
```

In English: nothing should ever land in the receiver's store with a timestamp past the sensor's expiration. That matters because a stale or post-expiration reading isn't just useless — if my CGM tells me I'm at 110 when I'm actually at 50, I won't eat anything, and a 50 with no alert is how diabetics end up in the ER. False-negative readings are the failure mode you have to design out, not the false positives.

Running TLC against the debug config actually catches this — the model surfaces a state where `lastSample` gets produced and stored after the sensor should have moved to `Expired`, because `ExpireSensor` and `ProduceSample` race on the same tick. Which is exactly the point of writing the spec — the invariant isn't satisfied by the current model, and the trace tells you where to tighten it.

## What's missing

A lot. The spec doesn't model calibration (the G7 mostly doesn't need it, but the API surface still exists). It doesn't model the "signal loss" state when the transmitter and receiver are out of range for too long. It doesn't model the difference between the sensor producing a sample and the *transmitter* actually packaging it for BLE. Alerts are a single high/low flag instead of the actual hysteresis the device uses — Dexcom won't refire the low alert if you're already in low territory and haven't climbed back out. And there's no model of the predictive "you'll be low in 20 minutes" alerts, which are the most clinically useful thing the device does.

If you've worked with TLA+ and want to take a swing at any of those, the spec is small enough to fork and extend in an afternoon. PRs welcome — it's the kind of project that's more useful the more eyes are on it, especially eyes that also wear one of these things.
