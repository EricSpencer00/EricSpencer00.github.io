:blogpost: true
:date: May 16, 2026
:author: AB
:category: Research Update
:tags: Formal Methods, TLA+, LLMs, Fine-Tuning, GRPO, DPO
:nocomments:

New Paper: TLA-Prover — Fine-Tuning LLMs for Verifiable TLA+ Specification Synthesis
======================================================================================

Building on our :doc:`evaluation study </posts/llm-tla-evaluation-2025>` that showed the best public LLMs
achieve only 8.6% semantic correctness on TLA+ specification generation, we present
**TLA-Prover**: a 20-billion-parameter model trained specifically for TLA+ specification synthesis.

TLA-Prover combines supervised fine-tuning (SFT) on verified examples with repair-based
group-relative policy optimization (GRPO), where the model learns to fix its own rejected
specifications. TLC model checking provides the reward signal directly — no learned reward
model is needed. A four-tier grading scheme (Bronze, Silver, Gold, Diamond) measures output
quality, with Diamond requiring that the model's correctness property is meaningful enough
for TLC to detect deliberate violations.

TLA-Prover achieves **30% pass@1 at Gold and Diamond** on a held-out 30-problem benchmark —
roughly **3.5× the 8.6% untuned baseline**. A DPO ablation trained from the same SFT
checkpoint reaches 20% at Diamond.

`Read the full paper details <../../papers/tla-prover/>`__

`See other posts <index.html>`__
