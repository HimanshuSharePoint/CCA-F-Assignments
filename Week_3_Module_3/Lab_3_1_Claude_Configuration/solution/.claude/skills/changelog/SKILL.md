---
name: changelog-entry
description: >
  Use when the user wants to update the changelog, add a CHANGELOG entry,
  write release notes, or summarize user-facing code changes.
---

# Changelog Entry Workflow

Create a concise Keep-a-Changelog-style entry for the current code changes.

## Steps

1. Inspect the current changes using `git diff` and `git status`.
2. Identify user-facing behavior changes.
3. Ignore formatting-only or internal changes that do not affect users.
4. Group changes under the appropriate headings:
   - Added
   - Changed
   - Fixed
   - Removed
5. Write each entry as a short, user-facing sentence.
6. Add or update the `## [Unreleased]` section in `CHANGELOG.md`.
7. Place the newest entry at the top of the changelog.
8. Do not invent changes that are not visible in the Git diff.

## Output Format

```text
## [Unreleased]

### Added

- Short user-facing description.