# News history sources

The homepage stays curated in `content/news.txt`. `content/news-history.json`
adds milestones only to `/news/`; its `updates` enrich existing entries by URL
without duplicating them. New homepage entries automatically join the history.
Every added event has a source. Dates retain the precision supported by it.

Reviewed 2026-09-09:

- Live archived CV: https://ericspencer.us/ericspencer-site-backup/resume/
  (also preserved in `backup-site/resume/`). This supplies the earlier jobs,
  club leadership, education, and founder timeline.
- Current homepage and `content/experience.txt` supply HorneSci and the
  Microsoft marketing CX study. The latter is described as a study, not
  recast as a software job at Microsoft.
- First Loyola research role: archive says April 2023, current experience
  says May. The timeline uses the supported year, 2023.
- FROM AMERICA: archived CV explicitly dates the studio to October 2025;
  current experience says May 2026. Use the archived start of building apps
  under the studio, not a claim about its legal incorporation date.
- Loyola help desk appears twice in the archive (July 2024 and August 2025).
  Keep one starting milestone, not two apparent new employers.
- Project dates use the site's dated writeups, rounded to the month where
  a publication date would otherwise imply an exact product launch date.
  Resilient is explicitly described as a research project.
- Hugging Face API dates chattla-20b to March 6, 2026. Do not repeat the old
  13,500-download number as if it were a lifetime count; download figures vary.
  https://huggingface.co/api/models/EricSpencer00/chattla-20b
- AI4FM dates the GSIRS poster to April 11 and ChatTLA+ talk to April 17.
  https://ai4fm.cs.luc.edu/posts/gsirs-llm-tla-poster-2026/
  https://ai4fm.cs.luc.edu/posts/chattla-presentation-2026/
- TLA+-Bench's first arXiv submission is July 26, 2026.
  https://arxiv.org/abs/2607.23425

Paper attachments are actual first-page renders, not generated mock covers.
The three arXiv PDFs use version 1, matching the initial announcements. The
poster comes from figshare item 31988706 and the slides from AI4FM. Original
PDF URLs, preview dimensions, and captions are in `news-history.json`.
Run `python3 scripts/build_news_previews.py` with Pillow and Poppler installed
to refresh the local WebP files. The regular site build does not download PDFs.

Excluded: duplicate role entries, individual classes and Dean's List semesters,
minor project commits, undocumented job endings, and an unsupported separate
best-paper award claim. The history is editorial, not a dump of every repo.

The timeline copy is first-person text-message prose. Keep the `source` field
for provenance even when a job or personal update has no public-facing link.
Visible links show their URL. Attachment captions are filenames. The homepage
retains its original curated wording and formatting.

`assets/js/news-scroll.js` opens fresh visits at the latest message. It respects
explicit fragments and back/forward restoration, and stops repositioning after
user input. Image dimensions reserve attachment space before lazy images load.
