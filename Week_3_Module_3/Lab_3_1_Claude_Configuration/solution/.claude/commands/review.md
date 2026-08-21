---
description: Review current changes against the project checklist
allowed-tools: Bash(git diff:*), Bash(git status:*), Read, Grep
argument-hint: "[optional path or scope]"
---

Review the current uncommitted changes using `git diff`.

Focus the review on: $ARGUMENTS

Apply this checklist:

1. Correctness: identify bugs, incorrect calculations, or broken behavior.
2. Testing: confirm every behavior change has appropriate tests.
3. Style: confirm public functions have type hints and a concise docstring.
4. Boundaries: confirm inputs and important boundary cases are validated.
5. Currency: confirm every public function that accepts or returns money states
   the currency explicitly in its docstring (for example, "USD").

Group each finding under one of:

- Blocker
- Suggestion
- Nit

Do not edit any files.

Finish with one concise verdict:

- Approved
- Needs changes: <number>