---
title: "Git Key Guardian"
date: 2025-09-14
description: "Protect sensitive keys from accidentally being uploaded to your git history at any point."
tags: ["git", "security", "devtools"]
categories: ["Projects"]
draft: false
---

Git Key Guardian is a lightweight pre-commit hook and helper toolkit that scans staged changes for common secret patterns and your own personal keys, helping you catch accidental commits of API keys, tokens, and credentials before they land in your git history.

## Why this project

Developers frequently commit secrets by accident — API keys, SSH keys, cloud credentials, and other sensitive strings can slip into commits or CI logs. Git Key Guardian provides a small, opt-in guardrail that runs locally (as a shared hook) and reports matches to a configurable set of regex patterns and a personal key list.

The tool is deliberately simple and conservative: it scans only staged changes, uses maintainable regex patterns, and supports exact-string matches for keys you care about tracking.

## Features

- Scans only staged (cached) changes to avoid noisy results from the working tree.
- Configurable regex-based patterns stored in `patterns/common_patterns.txt` (one per line, inline comments allowed).
- Exact-string matching against a per-user personal key file at `$HOME/.git-key-guardian/personal_keys.txt`.
- Interactive prompt when matches are detected — inspect matches and choose to abort or proceed with the commit.
- Installer script to wire the hook globally via `core.hooksPath` so it can protect all your local repos.

## How it works (short)

- On `git commit`, the pre-commit hook captures the staged diff with zero context and extracts newly added lines (those starting with a single `+`).
- The hook runs two checks:
  1. Grep-style regex checks using the patterns in `patterns/common_patterns.txt` (comments and blanks are ignored).
  2. Fixed string checks against your personal keys file (`$HOME/.git-key-guardian/personal_keys.txt`).
- If any matches are found the hook prints a sample of matching lines and prompts you to either abort the commit or continue.

## Install

Clone the repo and run the installer script. The installer copies the `pre-commit` hook to a shared hooks directory and configures `git` to use it globally.

```bash
git clone https://github.com/EricSpencer00/git-key-guardian.git
cd git-key-guardian
chmod +x ./scripts/install.sh
./scripts/install.sh
```

The installer will copy patterns to `$HOME/.git-key-guardian/patterns/common_patterns.txt` and install the hook under `$HOME/.git-key-guardian/hooks/pre-commit`. It also creates an editable `personal_keys.txt` file for your own keys.

To uninstall, remove the shared hooks directory or run:

```bash
git config --global --unset core.hooksPath
```

## Usage

- Stage changes as usual with `git add`.
- Run `git commit` — the hook will automatically scan staged changes.
- If the hook finds potential secrets you'll be shown sample matches and prompted to continue or abort.

### Test locally without installing

If you want to test the hook behavior without changing your global git configuration, create a temporary repo and run a commit as described in `CONTRIBUTING.md`:

```bash
mkdir /tmp/gkg-test && cd /tmp/gkg-test && git init -q
cat > test.txt <<'EOS'
ess kay _ live_1234567890abcdefghijklmn
not_a_key AKIAABCDEFGHIJKLMNOP
random text
EOS

git add test.txt
GIT_DIR=.git GIT_WORK_TREE=. git commit -m "test" || true
```

You should see the hook report any matches and prompt to proceed.

## Patterns and Personal Keys

- Update the shipped regex list at `patterns/common_patterns.txt`. Rules:
  - One regex per line, no `/.../` delimiters.
  - Inline comments after whitespace `#` are allowed.
  - Avoid catastrophic backtracking (prefer anchored subpatterns and bounded repetition).

Example patterns included by default:

- `sk_live_[0-9a-zA-Z]{24}` (Stripe live keys)
- `sk-[A-Za-z0-9]{48}` (Older OpenAI key format)
- `AKIA[0-9A-Z]{16}` (AWS Access Key ID)
- `ssh-rsa\s+[A-Za-z0-9+/=]+` (SSH public keys)

- Add exact personal secrets to `$HOME/.git-key-guardian/personal_keys.txt`. Lines beginning with `#` are ignored.

## Implementation notes

- The hook uses POSIX-compatible tools (bash, sed, grep, awk) and aims to be lightweight and portable.
- Patterns file is preprocessed by the hook to strip comments and blank lines before running `grep -En -f` to search staged additions.
- Personal keys are searched as fixed strings using `grep -Fn -f` after removing comment/blank lines.
- The hook only inspects added lines in the staged diff (`git diff --cached --unified=0` + awk filter for `^+[^+]`).

## Contributing

Contributions are welcome — follow the guidance in `CONTRIBUTING.md`:

- Keep regexes focused and fast.
- Provide positive/negative examples in `examples/` when adding or changing patterns.
- Test patterns locally before opening a PR.

## Caveats & best practices

- This tool is a helper, not a substitute for secret management. Rotate keys, use environment variables and secret stores, and audit logs and CI outputs.
- False positives are possible; use the personal keys file to reduce noise for known values.
- The hook runs locally and doesn't scan remote or CI logs — consider adding complementary server-side scanning in CI if needed.

## Links

- Git repository: https://github.com/EricSpencer00/git-key-guardian
- Installer script: `scripts/install.sh`
- Hook file: `hooks/pre-commit`
- Default patterns: `patterns/common_patterns.txt`
- Contribution guide: `CONTRIBUTING.md`

---

If you want any part shortened for a project page summary, or expanded with screenshots and example outputs from the hook, I can add them next.