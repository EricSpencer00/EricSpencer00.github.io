TLA+ for All: Running Model Checking in a Python Notebook
=========================================================

:Status: Published
:Venue: figshare, February 2025
:Authors: Konstantin Laufer, George K. Thiruvathukal
:DOI / PDF: `10.6084/m9.figshare.28376276.v1 <http://dx.doi.org/10.6084/m9.figshare.28376276.v1>`__


Overview
--------

TLA+ is a powerful formal specification language for designing and verifying concurrent
and distributed systems. But for many students and practitioners, the ecosystem has felt
inaccessible - requiring specialized tooling, complex installation steps, and the
perception that formal methods are only for specialists.

This project changes that by embedding TLA+ model checking directly into a Python
notebook environment. Anyone who can open a browser can now write specifications,
run the TLC model checker, explore counterexamples, and visualize system behaviors.


The Problem: Accessibility Barriers in Formal Methods
------------------------------------------------------

Despite decades of success in verifying critical systems, TLA+ adoption remains limited.
The barriers are real:

- The TLC model checker requires a local Java installation and command-line setup
- The TLA+ Toolbox IDE is unfamiliar to students used to notebook-based workflows
- No standard way exists to combine specifications, narrative, and results in a
  reproducible and shareable format
- Workshop and classroom use requires every participant to install and configure tooling

These barriers disproportionately affect students encountering formal methods for the
first time and instructors at institutions without dedicated systems support.


The Solution: TLA+ in a Notebook
----------------------------------

By integrating TLA+ into a Python notebook environment (Jupyter/JupyterLite):

.. list-table::
   :header-rows: 1

   * - Feature
     - Description
   * - In-browser TLC execution
     - Run TLA+ model checker without installing anything
   * - Literate specifications
     - Mix TLA+ code, prose, and results in one notebook
   * - Trace visualization
     - Explore counterexamples and behaviors interactively
   * - Reproducibility
     - Share a URL and anyone can re-run the full analysis
   * - No setup friction
     - Classroom and workshop ready - open a link and start


Use Cases
----------

**Teaching and workshops** - No setup friction. Students open a URL and start writing specs.

**Research documentation** - Executable specifications embedded in research papers and reports.

**Exploratory modeling** - Engineers sketch system designs and check properties without
committing to a full tool installation.

**Tutorials and onboarding** - New team members explore a codebase's formal model
before touching the implementation.


Citation
--------

Konstantin Laufer and George K. Thiruvathukal,
*TLA for All: Model Checking in a Python Notebook*,
figshare, February 2025.
http://dx.doi.org/10.6084/m9.figshare.28376276.v1
