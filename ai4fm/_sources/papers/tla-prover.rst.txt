TLA-Prover: Verifiable TLA+ Specification Synthesis via Preference-Optimized Low-Rank Adaptation
=================================================================================================

:Status: Published
:Venue: ICSOFT 2026 — 21st International Conference on Software Technologies, Porto, Portugal, July 16–18, 2026, pp. 627–636
:Authors: Eric Spencer, Arslan Bisharat, Brian Ortiz, Mujtaba Nazari, Khushboo Bhadauria, TaiNing Wang, George K. Thiruvathukal, Konstantin Läufer, Mohammed Abuhamad
:DOI / PDF: `10.5220/0015234600004088 <https://doi.org/10.5220/0015234600004088>`__ | `View published PDF <https://www.scitepress.org/PublishedPapers/2026/152346/152346.pdf>`__
:Google Scholar: `Citation record <https://scholar.google.com/scholar?cites=10942189414547579135&as_sdt=400005&sciodt=0,14&hl=en>`__


Abstract
--------

TLA+ is a formal specification language for verifying distributed systems and safety-critical
protocols. Large language models (LLMs) frequently produce TLA+ specifications that fail the TLC
model checker for semantic reasons. Across 25 LLMs, the best public baseline is 26.6% syntactic
parse and 8.6% semantic model-check. We present TLA-Prover, a 20-billion-parameter model for
TLA+ specification synthesis. Training combines supervised fine-tuning (SFT) on verified examples
with repair-based group-relative policy optimization (GRPO). In the GRPO stage, the model learns
to fix its own rejected specifications. We also train a direct preference optimization (DPO)
variant from the same SFT checkpoint as an ablation. TLC provides the reward signal directly,
with no learned reward model.

Four tiers grade each output: Bronze (parses), Silver (no warnings), Gold (passes TLC), and
Diamond. To reach Diamond, the model's correctness property is automatically altered in a small
way; TLC must then detect a violation. If TLC still passes, the property was always-true and
contributes nothing; the output fails Diamond. TLA-Prover reaches 9/30 (pass@1 = 30%) at both
Gold and Diamond on a held-out 30-problem benchmark. This is roughly 3.5× the 8.6% untuned
baseline. The DPO variant reaches 20% at Diamond. Gold and Diamond coincide at every checkpoint,
preventing the trivial-property failure mode.


Key Results
-----------

.. list-table::
   :header-rows: 1

   * - Metric
     - Result
   * - Syntactic correctness — best public baseline
     - 26.6%
   * - Semantic correctness — best public baseline (8.6% untuned)
     - 8.6%
   * - TLA-Prover Gold (passes TLC) pass@1
     - **30%**
   * - TLA-Prover Diamond pass@1
     - **30%**
   * - DPO variant Diamond pass@1
     - 20%
   * - Improvement over untuned baseline
     - ~3.5×


Training Approach
-----------------

**Supervised Fine-Tuning (SFT)**
The model is first trained on a curated set of verified TLA+ specifications to establish a
strong syntactic and semantic foundation.

**Group-Relative Policy Optimization (GRPO)**
In the GRPO stage, the model generates multiple candidate specifications per prompt. Rejected
outputs are used as repair targets, teaching the model to iteratively correct its own mistakes.
TLC model-checker output serves as the reward signal — no learned reward model is involved.

**Direct Preference Optimization (DPO) ablation**
A DPO variant is trained from the same SFT checkpoint to compare preference-optimization
strategies. It reaches 20% at Diamond, versus 30% for the GRPO variant.


Grading Tiers
-------------

.. list-table::
   :header-rows: 1

   * - Tier
     - Criterion
   * - Bronze
     - Specification parses (SANY)
   * - Silver
     - No parser warnings
   * - Gold
     - Passes TLC model checker
   * - Diamond
     - Gold, plus TLC detects a violation when the correctness property is deliberately mutated

Diamond prevents the trivial-property failure mode: a specification whose correctness
property is always true passes TLC by vacuity and contributes nothing meaningful. The
mutation test catches this. Gold and Diamond coincide at every checkpoint in TLA-Prover,
indicating the model never falls back to trivial properties.


Relationship to Prior Work
--------------------------

This paper extends the findings of our evaluation study
:doc:`Can LLMs Write Correct TLA+ Specifications? </papers/llm-tla-evaluation>`,
which established the 8.6% semantic correctness baseline across 25 LLMs. TLA-Prover
demonstrates that targeted fine-tuning with verifiable reward signals can close much
of that gap.


Citation
--------

Eric Spencer, Arslan Bisharat, Brian Ortiz, Mujtaba Nazari, Khushboo Bhadauria,
TaiNing Wang, George K. Thiruvathukal, Konstantin Läufer, and Mohammed Abuhamad,
*TLA-Prover: Verifiable TLA+ Specification Synthesis via Preference-Optimized
Low-Rank Adaptation*, Proceedings of the 21st International Conference on Software
Technologies (ICSOFT 2026), pp. 627–636, 2026.
https://doi.org/10.5220/0015234600004088
