# Lab 3.1: Configuring Claude Code

## Objective

Configure Claude Code with modular project memory, custom slash commands, a user-level rule, and an auto-invoked changelog skill.

## Concepts Covered

- Root and user-level `CLAUDE.md`
- Modular rule files loaded with `@import`
- Custom `/test` and `/review` commands
- Least-privilege command tools
- Skills triggered by description
- Git diff-based review and changelog workflows

## Solution Approach

The project root `CLAUDE.md` imports style and testing rules from `.claude/rules`. A user-level rule requires Claude to explain a change before editing. The `/test` command runs and summarizes pytest, while `/review` examines the Git diff without editing files. The review checklist was customized to require currency documentation for public monetary functions.

A changelog skill recognizes plain-language requests such as “Update the changelog for this change” and creates a Keep-a-Changelog-style entry under `[Unreleased]`.

## Important Files

- `CLAUDE.md`
- `.claude/rules/style.md`
- `.claude/rules/testing.md`
- `.claude/commands/test.md`
- `.claude/commands/review.md`
- `.claude/skills/changelog/SKILL.md`
- `src/northpeak/pricing.py`
- `src/tests/test_pricing.py`
- `CHANGELOG.md`

## Prerequisites

- Python 3.10 or later
- pytest
- Claude Code CLI
- Git

## Setup

```cmd
python -m venv .venv
.venv\Scriptsctivate
pip install -r requirements.txt
python -m pytest -q
claude
```

## How to Demonstrate

Inside Claude Code:

```text
What are this project's testing rules?
/test
/review pricing.py
Update the changelog for this change.
```

## Expected Results

- Imported testing and style rules are available automatically.
- User-level memory causes Claude to explain before editing.
- `/test` reports the actual pytest result.
- `/review` identifies missing tests, type hints, docstrings, and currency documentation without editing files.
- The changelog skill creates an `[Unreleased]` entry.
- The final test suite passes with seven tests.

## Key Learning

Repository-based memory, commands, and skills make team conventions repeatable, version-controlled, and available to every contributor.
