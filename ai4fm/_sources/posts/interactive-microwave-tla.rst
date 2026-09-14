:blogpost: true
:date: April 17, 2026
:author: Eric Spencer
:category: Research Update
:tags: Formal Methods, TLA+, Stuttering, Liveness
:nocomments:

Interactive Microwave: TLA+ in the Browser
==========================================

We published a browser-native version of the
`interactive-microwave-tla <https://github.com/EricSpencer00/interactive-microwave-tla>`_
simulator. It mimics a Java microwave runtime and a small TLA+ model checker
that is a literal transcription of the project's ``Microwave.tla`` spec, so
students can experiment with the state machine — including the stuttering
liveness failure from Laufer, Mertin, and Thiruvathukal,
`arXiv:2407.21152 <https://arxiv.org/abs/2407.21152>`_ — without installing
Java, Maven, or TLC.

The stuttering failure, made visible
------------------------------------

Section IV.C of the paper introduces a liveness property and its stuttering
counterexample:

.. code-block:: text

   HeatLiveness == (radiation = ON) ~> (radiation = OFF)

   Spec == Init /\ [][Next]_<<door, time, radiation, power>>

Under this original ``Spec``, TLA+ permits behaviors where every step after the
microwave begins radiating is a stutter (``vars' = vars``). The tick never
fires, the time never decrements, and ``radiation = ON`` holds forever —
violating ``HeatLiveness``. The fix (Exercise 3b) is weak fairness on ``Tick``:

.. code-block:: text

   Spec == Init /\ [][Next]_<<door, time, radiation, power>> /\ WF_vars(Tick)

Our previous web demo did not model any of this — neither the liveness
property, nor the stuttering failure, nor the fairness condition. It merely
happened to tick unconditionally in Java and therefore looked correct without
explaining why.

What the new build does
-----------------------

The browser port re-implements the spec literally in TypeScript and exposes
both the failure and its fix:

- A **Weak fairness on Tick** toggle in the sidebar switches the tick loop
  between the paper's original (unfair) spec and the fixed spec with
  ``WF_vars(Tick)``.
- With fairness off, the engine lets stutters run even when ``Tick`` is
  enabled. A runtime liveness detector surfaces the trap: after a short window
  of stutter-while-radiating, the UI flags ``HeatLiveness`` as violated and
  shows a 🔥 overlay — a runtime witness of Figure 7.
- With fairness on, the engine forces ``Tick`` to fire whenever it is
  continuously enabled. ``HeatLiveness`` holds and the overlay clears.

An exhaustive safety check enumerates every state reachable from ``Init`` via
the ``Next`` relation and confirms zero ``DoorSafety`` violations (matching
Exercise 2b).

Try it
------

.. raw:: html

   <div id="microwave-root" style="min-height: 560px;"></div>
   <link rel="stylesheet" href="../_static/demos/microwave/assets/index.css" />
   <script type="module" src="../_static/demos/microwave/assets/index.js"></script>

Reproduce the paper's Figure 7 by pressing **Power**, **+3s**, **Start**, and
then turning off **Weak fairness on Tick**. The ``Tick`` action stops firing,
the radiation indicator stays lit, and the liveness signal flips to
*violated*.

Source and details
------------------

- `Repository <https://github.com/EricSpencer00/interactive-microwave-tla>`_
- `Design spec <https://github.com/EricSpencer00/interactive-microwave-tla/blob/main/docs/superpowers/specs/2026-04-17-web-port-design.md>`_
- `Browser port (web/) <https://github.com/EricSpencer00/interactive-microwave-tla/tree/main/web>`_
- Laufer, Mertin, Thiruvathukal. *WIP: An Engaging Undergraduate Intro to
  Model Checking in Software Engineering Using TLA+.*
  `arXiv:2407.21152 <https://arxiv.org/abs/2407.21152>`_, 2024.
