# Lab 3.1 — Configuring Claude Code (NorthPeak Pricing Service)

Starter project for **Lab 3.1: CLAUDE.md Hierarchy, Commands & Skills**.
Everything you need is already here — your job in the lab is to *understand,
run, and extend* this configuration inside Claude Code.

## What's in here

    CLAUDE.md                       project memory (@imports the rule modules)
    .claude/rules/style.md          modular style rules
    .claude/rules/testing.md        modular testing rules
    .claude/commands/test.md        the /test slash command
    .claude/commands/review.md      the /review slash command
    .claude/skills/changelog/       the changelog skill (auto-invoked)
    src/northpeak/pricing.py        the code under configuration
    src/tests/test_pricing.py       the pytest suite (4 tests, all green)

## Setup (do this before the session)

1. Open this folder in VS Code (File > Open Folder...).
2. Create a virtual environment and install the test dependency:

       python -m venv .venv && source .venv/bin/activate
       # Windows: .venv\Scripts\activate
       pip install -r requirements.txt

3. Confirm the suite is green:

       pytest -q          # expect: 4 passed

4. Start Claude Code **from this folder** so it finds CLAUDE.md and .claude/:

       claude             # or use the Claude Code extension panel

   The first time, Claude Code will ask you to sign in — follow the prompt.

This project is already a git repository with a committed baseline, so `/review`
and the changelog skill can see your edits via `git diff`. Make your changes,
then run the commands — no `git init` needed.
