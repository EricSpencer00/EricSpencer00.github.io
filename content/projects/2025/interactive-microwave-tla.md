---
title: "Web Based TLA Microwave"
date: 2025-05-10
description: "An interactive microwave in the browser to learn TLA+"
tags: ["tla", "formal methods", "spring-boot"]
categories: ["Projects"]
images: ["/images/avatar.jpeg"]
draft: false
---

[GitHub Repo](https://github.com/EricSpencer00/interactive-microwave-tla)

![picture of the microwave](/images/projects/microwave/fullpic.png)

If you ever wanted an introduction to TLA+, you can try this locally hosted microwave application to get familiar with state traces along with a simple intuitive microwave.

Built using Spring Boot (Java) and the very advanced framework Vaadin (also Java) you can boot up this program in a terminal and run it in your browser. The development process was straight-forward and took exactly 2 weeks from start to finish to get everything working. If you feel as if you could likely build a better, less ugly design for the microwave, please take a look at [https://github.com/EricSpencer00/interactive-microwave-tla/issues](https://github.com/EricSpencer00/interactive-microwave-tla/issues) and feel free to implement a new solution with a less archaic framework (maybe something that encourages the use of HTML and CSS).

Turn on the power button mode to see an additional parameter of the state traces.

Turn on dangerous mode to allow the microwave to operate while the door is open.

Violating the Microwave's SAFE configuration will be caught by the mock TLC checker and will let you know that your actions resulted in an unsafe state. In a real TLC checker, the application explores all states and executions of the microwave for you and will tell you if there is a possibility of the microwave being in an unsafe state.

![picture of the violated state trace](/images/projects/microwave/failstatetrace.png)

Also, see the interactive guide on the left for a full tutorial on how to use the application along with a short introduction to TLA+ syntax and what to make of the state traces.

![picture of the guide of the microwave](/images/projects/microwave/guide.png)

```
  ---- MODULE Microwave ----
EXTENDS Integers, TLC

VARIABLES door, time, radiation

CONSTANTS OPEN, CLOSED, ON, OFF

Init ==
/\ door = CLOSED
/\ time = 0
/\ radiation = OFF

IncrementTime ==
/\ UNCHANGED <>
/\ time' = time + 3

Start ==
/\ time > 0
/\ door = CLOSED
/\ radiation' = ON
/\ UNCHANGED <>

Tick ==
/\ time > 0
/\ time' = time - 1
/\ UNCHANGED <>
/\ radiation' = IF time' = 0 THEN OFF ELSE radiation

Cancel ==
/\ time' = 0
/\ radiation' = OFF
/\ UNCHANGED <>

CloseDoor ==
/\ door = OPEN
/\ door' = CLOSED
/\ UNCHANGED <>

OpenDoor ==
/\ door = CLOSED
/\ door' = OPEN
/\ radiation' = OFF
/\ UNCHANGED <>

Next == IncrementTime \/ Start \/ Tick \/ Cancel \/ CloseDoor \/ OpenDoor

Safe == ~(radiation = ON /\ door = OPEN)

Spec == Init /\ [][Next]_<>

====
```

Once you have defined your .tla and .cfg file you can run a TLC checker against it which will look something like below. This example is from our interactive microwave, so it won't be exactly like running an TLC checker.

```
\* <Initial line 10, col 3 to line 13, col 36 of module Microwave>
STATE_1 ==
/\ door = "closed"
/\ timeRemaining = 0
/\ radiation = "off"

(* Power Button ENABLED *)
\* <TogglePower line 15, col 3 to line 18, col 36 of module Microwave>
STATE_3 ==
/\ door = "closed"
/\ timeRemaining = 0
/\ radiation = "off"
/\ power = "on"
\* <TogglePower line 15, col 3 to line 18, col 36 of module Microwave>
STATE_4 ==
/\ door = "closed"
/\ timeRemaining = 0
/\ radiation = "off"
/\ power = "off"
\* <Cancel line 35, col 3 to line 38, col 36 of module Microwave>
STATE_5 ==
/\ door = "closed"
/\ timeRemaining = 0
/\ radiation = "off"
/\ power = "off"
\* <OpenDoor line 40, col 3 to line 43, col 36 of module Microwave>
STATE_6 ==
/\ door = "open"
/\ timeRemaining = 0
/\ radiation = "off"
/\ power = "off"
\* <CloseDoor line 45, col 3 to line 48, col 36 of module Microwave>
STATE_7 ==
/\ door = "closed"
/\ timeRemaining = 0
/\ radiation = "off"
/\ power = "off"
\* IncrementTime Violation Attempt - Power is OFF
\* <TogglePower line 15, col 3 to line 18, col 36 of module Microwave>
STATE_9 ==
/\ door = "closed"
/\ timeRemaining = 0
/\ radiation = "off"
/\ power = "on"
\* <IncrementTime line 20, col 3 to line 23, col 36 of module Microwave>
STATE_10 ==
/\ door = "closed"
/\ timeRemaining = 3
/\ radiation = "off"
/\ power = "on"
\* <IncrementTime line 20, col 3 to line 23, col 36 of module Microwave>
STATE_11 ==
/\ door = "closed"
/\ timeRemaining = 6
/\ radiation = "off"
/\ power = "on"
\* <Start line 25, col 3 to line 28, col 36 of module Microwave>
STATE_12 ==
/\ door = "closed"
/\ timeRemaining = 6
/\ radiation = "on"
/\ power = "on"
\* <Tick line 30, col 3 to line 33, col 36 of module Microwave>
STATE_13 ==
/\ door = "closed"
/\ timeRemaining = 5
/\ radiation = "on"
/\ power = "on"
\* <Tick line 30, col 3 to line 33, col 36 of module Microwave>
STATE_14 ==
/\ door = "closed"
/\ timeRemaining = 4
/\ radiation = "on"
/\ power = "on"
\* <Tick line 30, col 3 to line 33, col 36 of module Microwave>
STATE_15 ==
/\ door = "closed"
/\ timeRemaining = 3
/\ radiation = "on"
/\ power = "on"
\* <Tick line 30, col 3 to line 33, col 36 of module Microwave>
STATE_16 ==
/\ door = "closed"
/\ timeRemaining = 2
/\ radiation = "on"
/\ power = "on"
\* <Tick line 30, col 3 to line 33, col 36 of module Microwave>
STATE_17 ==
/\ door = "closed"
/\ timeRemaining = 1
/\ radiation = "on"
/\ power = "on"
\* <Tick line 30, col 3 to line 33, col 36 of module Microwave>
STATE_18 ==
/\ door = "closed"
/\ timeRemaining = 0
/\ radiation = "off"
/\ power = "on"

(* Mode changed to DANGEROUS *)

(* Mode changed to SAFE *)

(* Power Button DISABLED *)
\* <Power Button Disabled line 50, col 3 to line 53, col 36 of module Microwave>
STATE_22 ==
/\ door = "closed"
/\ timeRemaining = 0
/\ radiation = "off"
```