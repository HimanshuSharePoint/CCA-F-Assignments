# Lab 3.2 — Targeted Behavior (NorthPeak Services Monorepo)

Starter project for **Lab 3.2: Path-Specific Rules & Plan Mode Workflows**.
Everything you need is already here — your job in the lab is to make Claude
Code's caution scale with the risk of each module.

## What's in here

    CLAUDE.md                       general rules + how path-specific rules work
    src/auth/CLAUDE.md              SECURITY-CRITICAL rules for auth/
    src/orders/CLAUDE.md            order conventions for orders/
    src/payments/CLAUDE.md          MONEY-CRITICAL rules for payments/
    .claude/agents/explorer.md      read-only explorer subagent (Read, Grep, Glob)
    src/auth/tokens.py              verify_token (strict)
    src/orders/service.py           place_order (calls verify_token)
    src/payments/charges.py         charge (calls verify_token)
    src/tests/conftest.py           make_test_token() helper + good_token fixture
    src/tests/test_smoke.py         pytest suite (12 tests, all green)

The suite starts at 4 tests and grows as you work. It currently sits at 12:
Exercise 1 added count_items and its test (-> 5), the Exercise 2 migration
deleted the deprecated verify_token_v1 and added two tests proving both
callers now reject weak tokens, plus a bad-amount rejection test for charge
(-> 10, including auth-shape coverage added
alongside the make_test_token helper).

## Setup (do this before the session)

1. Get this bundle onto your Blue Labs VM and enter it.
2. Create a virtual environment and install the test dependency:

       python -m venv .venv && source .venv/bin/activate
       # Windows: .venv\Scripts\activate
       pip install -r requirements.txt

3. Confirm the suite is green:

       pytest -q          # expect: 4 passed (baseline, before any exercises)

4. Start Claude Code **from this folder** so it finds the root CLAUDE.md and the
   per-module ones under src/:

       claude

   The first time, Claude Code will ask you to sign in — follow the prompt.

This project is already a git repository with a committed baseline, so you can
review your changes with `git diff` or undo an experiment with `git restore`.
