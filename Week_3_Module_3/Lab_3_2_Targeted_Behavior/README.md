# Lab 3.2: Targeted Behavior

## Status

Complete. The implementation is available in the `solution` folder.

## Objective

Apply different Claude Code behaviors based on code location and risk. This lab demonstrates path-specific rules, Plan mode for multi-file changes, and read-only exploration before modifying a money-critical module.

## Concepts Covered

- Path-specific `CLAUDE.md` rules
- Security-critical authentication rules
- Money-critical payment rules
- Claude Code Plan mode
- Read-only explorer subagent
- Multi-file migration with test verification

## Solution Approach

### Exercise 1: Path-Specific Rules

A typed `count_items()` helper and test were added to the ordinary `orders` module.

A request to weaken `verify_token()` under the security-critical `auth` module was rejected. A safe test-token helper was used instead, preserving strict production authentication.

### Exercise 2: Plan Mode Migration

Claude Code Plan mode was used before changing multiple files.

The approved plan:

1. Located all `verify_token_v1` references.
2. Migrated the Orders and Payments modules to `verify_token`.
3. Added valid-token and weak-token rejection tests.
4. Removed the deprecated `verify_token_v1` function.
5. Updated the project documentation.
6. Ran the complete test suite.

### Exercise 3: Explore Before Changing

The read-only explorer subagent mapped the Payments module using only Read, Grep, and Glob.

After exploration, `charge()` was updated to:

- Accept exactly `$10,000`
- Reject amounts greater than `$10,000`
- Raise a clear `ValueError`
- Preserve existing authentication and positive-amount validation

## Important Files

- `CLAUDE.md`
- `src/auth/CLAUDE.md`
- `src/orders/CLAUDE.md`
- `src/payments/CLAUDE.md`
- `.claude/agents/explorer.md`
- `src/auth/tokens.py`
- `src/orders/service.py`
- `src/payments/charges.py`
- `src/tests/test_services.py`

## Prerequisites

- Python 3.10 or later
- pytest
- Claude Code CLI
- Git

## Setup

```cmd
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt