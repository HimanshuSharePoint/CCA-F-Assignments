# Lab 3.1 Reflection Answers

## 1. Where does project memory live and how does `@import` work?

Project memory lives in the root `CLAUDE.md`. Its `@import` lines include focused rule modules such as `.claude/rules/style.md` and `.claude/rules/testing.md`.

## 2. Why use modular rules?

Modular files keep each rule category focused, make maintenance and reuse easier, keep the root file short, and provide clearer Git history.

## 3. What memory levels were demonstrated?

The lab used user-level memory in `~/.claude/CLAUDE.md`, project memory in the repository root, and imported project rule modules.

## 4. What did the user-level rule demonstrate?

The rule required Claude to explain a change before editing. After restarting Claude Code, the loyalty-points task showed the rule layered with project style and testing rules.

## 5. Why was the temporary loyalty-points change discarded?

It existed only to demonstrate memory layering. Git restored the original baseline before the slash-command exercise, returning the suite to four tests.

## 6. How is a slash command defined?

A Markdown file in `.claude/commands` defines a command, and the filename determines its name. `test.md` becomes `/test`, and `review.md` becomes `/review`.

## 7. What frontmatter fields were used?

The commands used `description`, `allowed-tools`, and `argument-hint`. `$ARGUMENTS` inserted the optional scope supplied after the command.

## 8. What did `/test` demonstrate?

`/test` ran the real pytest suite and summarized pass or failure results without modifying files.

## 9. Why was `/review` read-only?

A review should inspect evidence, not change it. Limiting tools to Git diff, Git status, Read, and Grep follows least privilege.

## 10. What did the initial review identify?

The incomplete `gift_wrap_fee()` lacked a test, type hint, docstring, named constant, and currency documentation. The command returned a Needs changes verdict without editing files.

## 11. How was the checklist customized?

The review command was updated to require public monetary functions to state their currency in the docstring. The rerun applied the new team rule.

## 12. What is a skill and how does it differ from a slash command?

A slash command is invoked explicitly. A skill is auto-invoked when user intent matches its description. The changelog skill responded to “Update the changelog for this change.”

## 13. Why does skill description quality matter?

A narrow description may fail to trigger, while a broad one may trigger incorrectly. Good descriptions include concrete requests such as changelog entry, release notes, and user-facing change summary.

## 14. What did the changelog skill do?

It inspected Git changes, identified the user-facing gift-wrap feature, and added a concise entry under `## [Unreleased]` in `CHANGELOG.md`.

## 15. Why was a Git baseline necessary?

Git diff powered both review and changelog workflows, while Git restore enabled safe rollback of demonstrations. A baseline was recreated because the starter archive omitted `.git` metadata.

## 16. What was the final result?

The completed helper used a named constant, type hint, USD docstring, and tests. The final suite passed seven tests, and the changelog contained the new feature entry.

## Key Takeaway

Repository-based memory, commands, and skills make team behavior visible, repeatable, reviewable, and version-controlled.
