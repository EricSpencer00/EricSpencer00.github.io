Can LLMs Write Correct TLA+ Specifications?
============================================

Evaluating Natural-Language-to-TLA+ Generation

:Status: Accepted
:Venue: ICSOFT 2026 - International Conference on Software Technologies, Porto, Portugal
:Authors: AI4FM, Loyola University Chicago
:DOI / PDF: Available upon publication


Abstract
--------

TLA+ has supported industrial verification at companies such as Amazon and Microsoft,
yet writing correct TLA+ specifications from natural language still requires significant
time and expertise, which limits adoption. LLMs show promise, but no prior study measures
whether they produce semantically correct TLA+ specifications from natural language.

This paper presents the first systematic evaluation of LLM-based TLA+ specification
synthesis from natural language. Our study evaluates 30 LLMs across eight families on a
curated dataset of 205 TLA+ specifications: 25 open-weight models across four prompting
strategies (2,600 runs) and 5 proprietary models under few-shot prompting (130 runs),
all validated by the SANY parser and TLC model checker.


Key Results
-----------

.. list-table::
   :header-rows: 1

   * - Metric
     - Best Result
   * - Syntactic correctness (SANY)
     - **26.6%**
   * - Semantic correctness (TLC)
     - **8.6%**
   * - Prompting strategy enabling semantic success
     - Progressive prompting only


Surprising Findings
-------------------

**Model size does not predict quality.**
DeepSeek r1:8b outperforms its 70b variant across all prompting strategies.
This suggests that reasoning alignment for formal languages matters more than
raw parameter count.

**Code-specialized models consistently underperform.**
Models trained heavily on mainstream programming languages show negative transfer
when applied to TLA+. Familiarity with Python or Java does not generalize to
formal specification languages.

**Semantic success requires progressive prompting.**
Across all evaluations, semantic correctness - specifications that pass the TLC
model checker - was only achieved under progressive prompting strategies.
Direct and few-shot prompting failed to produce semantically valid outputs.


Why This Matters
----------------

TLA+ is not a niche language. It has been used to verify core distributed systems
at Amazon Web Services (DynamoDB, S3), Microsoft Azure, and other production environments.
If LLMs could reliably generate TLA+ from natural language, formal verification could
become far more accessible to engineers who understand their system but lack specification expertise.

This paper shows that current LLMs are not there yet. Reaching reliable TLA+ generation
will require targeted work on reasoning alignment, formal language training data,
and evaluation-driven prompting strategies - all active directions for AI4FM.


Citation
--------

.. note::
   Full citation will be available upon publication. The paper has been accepted.
