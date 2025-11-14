This repository uses GitHub Actions to deploy a Hugo site to GitHub Pages.

Disabled workflows:
- `.github/disabled/process-highscore-issue.yml`
- `.github/disabled/update-highscore.yml`

Rationale:
- The high score workflows were specific to a small interactive feature (Blackjack high scores). They have been disabled and the scripts moved to `tools/` to remove them from active CI while preserving the implementation for local testing or future use.

If you want to re-enable the workflows, move the files from `.github/disabled/` back to `.github/workflows/` and restore the scripts from `tools/` if needed.
