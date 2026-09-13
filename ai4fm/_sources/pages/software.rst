Software and Datasets
=====================

AI4FM develops its research artifacts in the open. Our source code lives under the
`LUC-AI4FM GitHub organization <https://github.com/LUC-AI4FM>`__, and the trained
models and corpora produced by that code are published on
`Hugging Face <https://huggingface.co/EricSpencer00>`__ - available for reuse and
replication.

.. note::
   This page lists our publicly released repositories. Work that is still under
   submission or embargo is released once the associated paper is public.


Models and Fine-Tuning
----------------------

.. grid:: 1
   :gutter: 3

   .. grid-item-card::
      :margin: 0

      :octicon:`cpu;1em;sd-text-primary` **TLA-Prove (ChatTLA)**

      The training and evaluation code behind :doc:`TLA-Prover <../papers/tla-prover>`,
      accepted at ICSOFT 2026. The distinguishing choice is the training metric: success
      is measured by whether a generated specification passes the TLC model checker, not
      by perplexity. The resulting 20B model is derived from ``openai/gpt-oss-20b`` and
      released under Apache 2.0.

      `Repository <https://github.com/LUC-AI4FM/TLA-Prove>`__ |
      `Model on Hugging Face <https://huggingface.co/EricSpencer00/chattla-20b>`__

   .. grid-item-card::
      :margin: 0

      :octicon:`sync;1em;sd-text-primary` **ralph-tla**

      Experiments pairing the Ralph specification language with TLA+ in a self-correcting
      loop: the model drafts a specification, SANY and TLC check it, and the resulting
      errors are fed back to the model until the specification passes. A test of whether
      verifier feedback can substitute for human repair.

      `Repository <https://github.com/LUC-AI4FM/ralph-tla>`__


Released Models
---------------

The **ChatTLA** model family, fine-tuned from ``openai/gpt-oss`` base models for TLA+
specification synthesis. All are released under Apache 2.0 and are
`published on Hugging Face <https://huggingface.co/EricSpencer00>`__.

.. list-table::
   :header-rows: 1
   :widths: 30 12 58

   * - Model
     - Size
     - Description
   * - `chattla-20b <https://huggingface.co/EricSpencer00/chattla-20b>`__
     - 20B
     - The model behind :doc:`TLA-Prover <../papers/tla-prover>` (ICSOFT 2026), trained
       with supervised fine-tuning and GRPO. A
       `GGUF build <https://huggingface.co/EricSpencer00/chattla-20b-gguf>`__ is
       available for local inference via Ollama and llama.cpp.
   * - `chattla-v2-sft2 <https://huggingface.co/EricSpencer00/chattla-v2-sft2>`__
     - 20B
     - Retrained on the verifier-gated RFT corpus below, so every training example is
       one the model checker already accepted.
   * - `chattla-w4dg-120b <https://huggingface.co/EricSpencer00/chattla-w4dg-120b>`__
     - 117B
     - The largest model in the family, fine-tuned on the W4 diamond/gold corpus. Also
       published as a
       `LoRA adapter <https://huggingface.co/EricSpencer00/chattla-w4dg-120b-adapter>`__
       for use on top of the stock base model.
   * - `chattla-20b-prover-v3 <https://huggingface.co/EricSpencer00/chattla-20b-prover-v3>`__
     - 20B (LoRA)
     - Targets TLAPS *proof* construction rather than specification generation - the
       harder downstream task of proving a spec's invariants.


Released Datasets
-----------------

Training and evaluation corpora produced by the pipelines above. These are
**verifier-gated**: examples are kept only if SANY parses them and TLC accepts them,
so the corpora contain machine-checked specifications rather than merely plausible ones.

.. list-table::
   :header-rows: 1
   :widths: 34 12 54

   * - Dataset
     - Size
     - Description
   * - `tla-w4-diamond-gold <https://huggingface.co/datasets/EricSpencer00/tla-w4-diamond-gold>`__
     - 4,119 rows
     - Diamond- and gold-tier survivors of a cross-family verify-until-correct loop,
       exported as SFT text. The largest corpus in the set.
   * - `chattla-rft-corpora-v2 <https://huggingface.co/datasets/EricSpencer00/chattla-rft-corpora-v2>`__
     - 1K-10K rows
     - Rejection-sampling fine-tuning (RFT/STaR) corpus for specification generation.
       Used to train ``chattla-v2-sft2``.
   * - `chattla-tla-prover-corpora-v1 <https://huggingface.co/datasets/EricSpencer00/chattla-tla-prover-corpora-v1>`__
     - 1,125 SFT rows
     - Training and evaluation corpora for the TLAPS theorem-proving work.
   * - `chattla-tla-prover-108-108 <https://huggingface.co/datasets/EricSpencer00/chattla-tla-prover-108-108>`__
     - Artifact
     - A reproducible TLAPS proof artifact recording a 108/108 prover result.


Data Pipelines and Evaluation
-----------------------------

.. grid:: 1
   :gutter: 3

   .. grid-item-card::
      :margin: 0

      :octicon:`database;1em;sd-text-primary` **tla-dataset-pipeline**

      A pipeline that discovers TLA+ repositories across GitHub, extracts ``.tla``,
      ``.cfg``, and ``.tlaps`` files, parses them with LLM-based analysis, and archives
      the results to S3. Discovery runs nightly under CI with DVC-tracked state, so the
      corpus grows continuously rather than being frozen at collection time.

      `Repository <https://github.com/LUC-AI4FM/tla-dataset-pipeline>`__

   .. grid-item-card::
      :margin: 0

      :octicon:`checklist;1em;sd-text-primary` **tla_benchmark**

      The evaluation harness behind our LLM benchmarking work. Extracts real
      SANY-parsed ASTs, runs specifications through ``tla2tools``, and scores them on
      syntactic and semantic correctness alongside code-quality metrics. Includes a
      dashboard for reviewing runs.

      `Repository <https://github.com/LUC-AI4FM/tla_benchmark>`__


Generation Pipelines
--------------------

.. grid:: 1
   :gutter: 3

   .. grid-item-card::
      :margin: 0

      :octicon:`beaker;1em;sd-text-primary` **FormaLLM**

      A research pipeline for generating TLA+ specifications from natural language,
      orchestrated with ZenML and backed by OpenAI, Anthropic, or local Ollama models.
      Separates prompting, parsing, and evaluation into swappable pipeline steps so that
      backends and prompting strategies can be compared under identical conditions.

      `Repository <https://github.com/LUC-AI4FM/FormaLLM>`__

   .. grid-item-card::
      :margin: 0

      :octicon:`arrow-switch;1em;sd-text-primary` **FormaLLM-Reverse**

      The companion to FormaLLM, exploring the opposite direction: recovering readable
      natural-language documentation from existing formal models.

      `Repository <https://github.com/LUC-AI4FM/FormaLLM-Reverse>`__

   .. grid-item-card::
      :margin: 0

      :octicon:`file;1em;sd-text-primary` **paper-parse**

      Tooling for extracting structured data from research PDFs at scale, used to build
      the comment-ratio dataset supporting our empirical software engineering work.

      `Repository <https://github.com/LUC-AI4FM/paper-parse>`__


Contributing
------------

Our repositories are open to students and collaborators. If you are interested in
working on any of these projects, see :doc:`Get Involved <prospective-students>`.
