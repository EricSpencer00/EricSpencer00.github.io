Research Papers
===============

Research outputs from the AI4FM group at Loyola University Chicago.

.. tab-set::

   .. tab-item:: Papers

      .. grid:: 1
         :gutter: 3

         .. grid-item-card::
            :margin: 0

            :octicon:`beaker;1em;sd-text-primary` **TLA-Prover: Verifiable TLA+ Specification Synthesis via Preference-Optimized Low-Rank Adaptation**

            *Accepted at ICSOFT 2026*

            A 20-billion-parameter model trained with SFT and repair-based GRPO for TLA+
            specification synthesis. TLC model checking provides the reward signal directly.
            Achieves 30% pass@1 at Gold and Diamond — roughly 3.5× the 8.6% untuned baseline.

            .. button-link:: tla-prover/
               :color: primary

               Full Details

         .. grid-item-card::
            :margin: 0

            :octicon:`beaker;1em;sd-text-primary` **Can LLMs Write Correct TLA+ Specifications? Evaluating Natural-Language-to-TLA+ Generation**

            *Accepted at ICSOFT 2026*

            The first systematic evaluation of LLM-based TLA+ specification synthesis from natural
            language. Evaluates 30 LLMs across eight families on 205 TLA+ specifications using the
            SANY parser and TLC model checker. LLMs achieve only 8.6% semantic correctness.
            Model size does not predict quality on formal languages.

            .. button-link:: llm-tla-evaluation/
               :color: primary

               Full Details

   .. tab-item:: Presentations

      .. grid:: 1
         :gutter: 3

         .. grid-item-card::
            :margin: 0

            :octicon:`video;1em;sd-text-primary` **ChatTLA+: Using LLMs for TLA+ Formal Specification Generation and Verification**

            *Undergraduate Research and Engagement Symposium, April 17, 2026* - Eric Spencer

            A presentation exploring the use of large language models for generating and verifying
            TLA+ formal specifications. Builds on the group's systematic evaluation research,
            extending to practical generation and verification pipelines.

            .. button-link:: chattla-2026/
               :color: primary

               Full Details

   .. tab-item:: Posters

      .. grid:: 1
         :gutter: 3

         .. grid-item-card::
            :margin: 0

            :octicon:`note;1em;sd-text-primary` **Large Language Models (LLM) and Temporal Logic of Actions (TLA): How Effective are LLMs for Verification Systems**

            *GSIRS 2026* - Ortiz, Bisharat, Abuhamad, Läufer, Spencer, Bhadauria, Thiruvathukal, Wang

            Presented at the Loyola University Chicago Graduate School Interdisciplinary Research
            Symposium, April 11, 2026. The first systematic evaluation of 30 LLMs on 205 TLA+
            specifications, validated with the SANY parser and TLC model checker.

            .. button-link:: gsirs-2026-tla-llm/
               :color: primary

               Full Details

         .. grid-item-card::
            :margin: 0

            :octicon:`note;1em;sd-text-primary` **Automating TLA+ Model Synthesis with LLMs and Formal Verification Pipelines**

            *GCASR 2025* - Ortiz, Abuhamad, Wang, Thiruvathukal, Läufer

            Presented at the 12th Greater Chicago Area Systems Research Workshop, May 8, 2025,
            Loyola University Chicago. Presents a pipeline for automating TLA+ model synthesis
            from natural language using LLMs, validated with SANY and TLC.

            .. button-link:: gcasr-2025-tla-llm/
               :color: primary

               Full Details

   .. tab-item:: Tools & Artifacts

      .. grid:: 1
         :gutter: 3

         .. grid-item-card::
            :margin: 0

            :octicon:`book;1em;sd-text-primary` **TLA+ for All: Running Model Checking in a Python Notebook**

            *figshare, February 2025* - Laufer, Thiruvathukal

            Integrates TLA+ model checking into Python notebook environments, making formal
            verification accessible without specialized tooling. Supports literate modeling,
            reproducibility, and barrier-free access for teaching and research.

            .. button-link:: tla-for-all/
               :color: primary

               Full Details
