#############################################
 AI for Formal Methods
#############################################

Welcome to **AI4FM** - the AI for Formal Methods research group at
`Loyola University Chicago <https://luc.edu>`__, part of the
`Department of Computer Science <https://luc.edu/cs>`__.
We advance formal methods, rigorous system design, and reproducible tools at the
intersection of AI, logic, mathematics, and real-world computing.

Featured Research
-----------------

.. grid:: 1 1 2 2
   :gutter: 2

   .. grid-item-card::
      :margin: 0

      :octicon:`beaker;1em;sd-text-primary` **Can LLMs Write Correct TLA+ Specifications?**

      *Evaluating Natural-Language-to-TLA+ Generation* - Accepted at ICSOFT 2026

      The first systematic evaluation of LLM-based TLA+ specification synthesis from
      natural language. We evaluate 30 LLMs across eight families on a curated dataset of
      205 TLA+ specifications, validated by both the SANY parser and TLC model checker.
      LLMs achieve up to 26.6% syntactic correctness but only 8.6% semantic correctness.

      .. button-link:: papers/llm-tla-evaluation/
         :color: primary

         Read More

      .. button-link:: posts/llm-tla-accepted-2026/
         :color: secondary

         Research Update


   .. grid-item-card::
      :margin: 0

      :octicon:`beaker;1em;sd-text-primary` **TLA-Prover: Verifiable TLA+ Specification Synthesis**

      *Preference-Optimized Low-Rank Adaptation* - Accepted at ICSOFT 2026

      A 20-billion-parameter model trained with supervised fine-tuning and repair-based
      group-relative policy optimization (GRPO) for TLA+ specification synthesis.
      TLA-Prover achieves 30% semantic correctness — roughly 3.5× the 8.6% untuned
      baseline.

      .. button-link:: papers/tla-prover/
         :color: primary

         Read More

      .. button-link:: posts/tla-prover-accepted-2026/
         :color: secondary

         Research Update


Research Areas
--------------

.. grid:: 1 1 2 2
   :gutter: 2

   .. grid-item-card::
      :margin: 0

      :octicon:`beaker;1em;sd-text-primary` **Formal Specification and Verification**

      Building datasets, tooling, and infrastructure around **TLA+** and other formal
      specification languages. Making model checking accessible through open pipelines
      and notebook-based workflows.

   .. grid-item-card::
      :margin: 0

      :octicon:`cpu;1em;sd-text-primary` **LLMs for Formal Methods**

      Evaluating whether large language models can generate semantically correct formal
      specifications. Identifying where LLMs fail on rigorous specification tasks and why.

   .. grid-item-card::
      :margin: 0

      :octicon:`graph;1em;sd-text-primary` **Empirical Software Engineering**

      Studying software artifacts at scale: pre-trained model naming conventions,
      supply chain security, and development practices in real-world open-source systems.

   .. grid-item-card::
      :margin: 0

      :octicon:`shield;1em;sd-text-primary` **Security and Systems**

      IoT security research including signal injection attacks on pairing protocols,
      plus HPC education tools and agentic tutoring systems for parallel computing.


Meet the Team
-------------

.. grid:: 1 2 3 3
   :gutter: 2

   .. grid-item-card::
      :margin: 0
      :text-align: center
      :img-top: _static/images/people/abuhamad.jpg

      **Mohammed Abuhamad**

      Security, AI/ML, IoT

      `Website <https://abuhamad.cs.luc.edu/>`__

   .. grid-item-card::
      :margin: 0
      :text-align: center
      :img-top: _static/images/people/laufer.jpg

      **Konstantin Laufer**

      Programming Languages, Formal Methods

      `Website <https://laufer.cs.luc.edu/>`__

   .. grid-item-card::
      :margin: 0
      :text-align: center
      :img-top: _static/images/people/thiruvathukal.png

      **George K. Thiruvathukal**

      HPC, Software Engineering, AI

      `Website <https://gkt.sh/>`__

   .. grid-item-card::
      :margin: 0
      :text-align: center
      :img-top: _static/images/people/wang.jpg

      **TaiNing Wang**

      Databases, Formal Methods, AI/ML

      `Website <https://taining.github.io/>`__

   .. grid-item-card::
      :margin: 0
      :text-align: center
      :img-top: _static/images/people/bhadauria.jpeg

      **Khushboo Bhadauria**

      `Email <mailto:kbhadauria@luc.edu>`__

   .. grid-item-card::
      :margin: 0
      :text-align: center
      :img-top: _static/images/people/bisharat.png

      **Arslan Bisharat**

      LLM Evaluation, Formal Methods, Adversarial ML

      `Website <https://marslan.cs.luc.edu/>`__

   .. grid-item-card::
      :margin: 0
      :text-align: center
      :img-top: _static/images/people/ortiz.png

      **Brian Ortiz**

      DevSecOps, Secure Systems

      `GitHub <https://github.com/bortiz-101>`__

   .. grid-item-card::
      :margin: 0
      :text-align: center
      :img-top: _static/images/people/bsantos.png

      **Beatriz Santos**

      `GitHub <https://github.com/beatriz-baquerizo>`__

   .. grid-item-card::
      :margin: 0
      :text-align: center
      :img-top: _static/images/people/spencer.png

      **Eric Spencer**

      `Website <https://ericspencer.us>`__


.. grid:: 1 1 2 2
   :gutter: 2

   .. grid-item-card::
      :margin: 3 0 0 0
      :text-align: center

      :octicon:`file;1em` **Research Papers**

      .. button-link:: papers/
         :color: primary
         :expand:

         Browse Papers

   .. grid-item-card::
      :margin: 3 0 0 0
      :text-align: center

      :octicon:`repo;1em` **Open Source**

      .. button-link:: pages/software/
         :color: primary
         :expand:

         Software and Datasets


Research Updates
----------------

.. postlist:: 10
   :category: Research Update
   :date: %A, %B %d, %Y
   :format: {date}: {title}
   :excerpts:
   :expand: Read more ...

..
   Toctrees for the side bars

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Pages

   About <pages/about>
   Team <pages/people>
   Software and Datasets <pages/software>
   Funding <pages/funding>
   Get Involved <pages/prospective-students>

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Research Papers

   All Papers <papers/index>
   papers/tla-prover
   papers/llm-tla-evaluation
   papers/chattla-2026
   papers/gsirs-2026-tla-llm
   papers/gcasr-2025-tla-llm
   papers/tla-for-all

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Research Updates

   All Posts <posts/index>
   posts/tla-prover-accepted-2026
   posts/llm-tla-accepted-2026
   posts/tla-prover-2026
   posts/chattla-presentation-2026
   posts/gsirs-llm-tla-poster-2026
   posts/llm-tla-evaluation-2025
   posts/gcasr-2025-poster
   posts/eric-spencer-mulcahy-scholar-2025
   posts/tla-for-all-running-model-checking-in-a-python-notebook
