Large Language Models (LLM) and Temporal Logic of Actions (TLA): How Effective are LLMs for Verification Systems
===================================================================================================================

:Status: Presented
:Venue: GSIRS 2026 - Graduate School Interdisciplinary Research Symposium, April 11, 2026, Loyola University Chicago
:Authors: Brian Ortiz, Arslan Bisharat, Mohammed Abuhamad, Konstantin Läufer, Eric Spencer, Khushboo Bhadauria, George K. Thiruvathukal, TaiNing Wang
:Institution: Loyola University Chicago


Abstract
--------

TLA+ has supported industrial verification at companies such as Amazon and Microsoft,
yet writing correct TLA+ specifications from natural language still requires time and
expertise, which limits adoption. LLMs show promise, but no prior study measures whether
they produce semantically correct TLA+ specifications from natural language.

This paper presents the first systematic evaluation of LLM-based TLA+ specification
synthesis from natural language. Our study evaluates 30 LLMs across eight families on a
curated dataset of 205 TLA+ specifications: 25 open-weight models across four prompting
strategies (2,600 runs) and 5 proprietary models under few-shot prompting (130 runs),
all validated by the SANY parser and TLC model checker. LLMs achieve up to 26.6%
syntactic correctness but only 8.6% semantic correctness, with successes exclusive to
progressive prompting. Results show that model size does not predict quality, and
code-specialized models consistently underperform due to negative transfer from mainstream
language training.


Based On
--------

This poster is based on the paper `Can LLMs Write Correct TLA+ Specifications? Evaluating Natural-Language-to-TLA+ Generation <llm-tla-evaluation/>`__, currently under submission.


Citation
--------

Brian Ortiz, Arslan Bisharat, Mohammed Abuhamad, Konstantin Läufer, Eric Spencer,
Khushboo Bhadauria, George K. Thiruvathukal, and TaiNing Wang,
*Large Language Models (LLM) and Temporal Logic of Actions (TLA): How Effective are LLMs for Verification Systems*,
GSIRS 2026, April 11, 2026.
