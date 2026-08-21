# Lab 3.1 Reflection Answers

## 1. Where does project memory live?

Project memory lives in the `CLAUDE.md` file at the project root.

Claude Code reads this file automatically when it starts from the project directory. The memory provides standing instructions such as coding conventions, testing expectations, and project-specific workflows.

The project root is important because starting Claude Code from another location may prevent the project memory and `.claude` configuration from loading.

## 2. How does `@import` work?

The root `CLAUDE.md` uses `@import` statements to include smaller rule files.

This project imported:

- `.claude/rules/style.md`
- `.claude/rules/testing.md`

The root file acts as a short index, while the detailed rules remain in separate, focused files.

This makes the configuration easier to maintain and reuse.

## 3. Why keep rules in modular files?

Modular rule files provide several advantages:

- Each file has one clear purpose.
- Style and testing rules can be updated independently.
- The root `CLAUDE.md` remains short and readable.
- Rule modules can be reviewed separately.
- Teams can reuse common rules across projects.
- Git history shows which rule category changed.

One large configuration file would be harder to navigate, review, and maintain.

## 4. What are the memory levels used in this lab?

The lab demonstrated three memory sources:

1. User-level memory in `~/.claude/CLAUDE.md`
2. Project-level memory in the repository `CLAUDE.md`
3. Modular project rules loaded through `@import`

User-level memory applies across projects, while project-level rules apply only to the current repository.

More specific project instructions should control project-specific behavior when rules overlap.

## 5. What user-level rule was added?

The following user-level rule was added:

`Always explain a change in one sentence before editing files.`

Claude Code was restarted after creating the file because user-level memory is loaded when a session begins.

When the `loyalty_points()` helper was requested, Claude explained the intended change before proposing edits.

## 6. How did the layering demonstration work?

The `loyalty_points()` task demonstrated all memory layers together.

The user-level rule caused Claude to explain the change before editing.

The project style rules caused Claude to add:

- A type hint
- A concise docstring
- Negative-input validation
- A small, testable helper

The testing rules caused Claude to add boundary tests and run the complete test suite.

This demonstrated that user and project instructions can work together.

## 7. Why was the temporary `loyalty_points()` change discarded?

The change was created only to demonstrate memory layering.

The lab required the project to return to its original four-test baseline before beginning the slash-command exercise.

Git made it possible to remove the demonstration safely using:

- `git restore .`
- `git clean -fd src`

After restoration, the original test suite passed and the working tree was clean.

## 8. How is a slash command defined?

A slash command is defined by a Markdown file inside:

`.claude/commands/`

The filename determines the command name.

For example:

- `test.md` becomes `/test`
- `review.md` becomes `/review`

The Markdown file contains frontmatter and the instructions Claude should follow when the command is invoked.

## 9. What frontmatter fields were used?

The command files used fields such as:

### `description`

Explains the command’s purpose and appears in the command menu.

### `allowed-tools`

Limits which tools the command is permitted to use.

### `argument-hint`

Shows the expected optional argument format.

The `/review` command also used `$ARGUMENTS` to receive the path or scope supplied after the command.

## 10. What is the purpose of `$ARGUMENTS`?

`$ARGUMENTS` inserts the text supplied after the slash command into the command instructions.

For example:

`/review pricing.py`

causes `pricing.py` to become the review scope.

This allows one shared command to review different files or areas without creating a separate command for each one.

## 11. What did the `/test` command demonstrate?

The `/test` command ran the real project test suite using:

`python -m pytest -q`

Claude then summarized:

- The number of passed tests
- The number of failed tests
- The names and likely causes of failures, if any

The command did not modify project files.

This converted a recurring testing task into a consistent one-word action.

## 12. Why was `/review` restricted to read-only tools?

The review command used read-only tools such as:

- `git diff`
- `git status`
- Read
- Grep

The command was not allowed to edit files.

This follows the principle of least privilege. A review operation should inspect and report findings, not silently modify the code being reviewed.

Restricting tools reduces the risk that a review command changes the evidence it is supposed to evaluate.

## 13. What did the first `/review pricing.py` identify?

An intentionally incomplete `gift_wrap_fee()` function was added without:

- A test
- A return type hint
- A docstring
- A named constant
- Currency documentation

The `/review pricing.py` command inspected the Git diff and identified these issues.

The findings were grouped by severity, and the final verdict was `Needs changes`.

The review made no edits.

## 14. How was the review checklist customized?

The review command was updated with an additional requirement:

Public monetary functions must clearly state their currency in the docstring.

After updating `.claude/commands/review.md`, the command was run again.

The second review applied the new rule and identified the missing USD documentation.

Because the command file is stored in the repository, the updated review behavior can be shared with the entire team.

## 15. Why store slash commands in the repository?

Repository-based commands provide:

- Consistent workflows across contributors
- Version-controlled updates
- Easier code review
- Shared team conventions
- Less repeated prompt writing
- A clear history of command changes

Without shared command files, each contributor might run a different testing or review process.

## 16. What is a Claude Code skill?

A skill is a folder containing a `SKILL.md` file.

The frontmatter description explains when Claude should use the skill. The body defines the workflow and expected output.

Unlike a slash command, a skill is not necessarily called by an explicit command name.

Claude can invoke a skill automatically when the user’s request matches its description.

## 17. How is a skill different from a slash command?

A slash command is invoked explicitly.

For example:

- `/test`
- `/review pricing.py`

A skill is triggered by user intent.

For example:

`Update the changelog for this change.`

Claude matched this request to the changelog skill’s description without the user naming the skill directly.

Slash commands are appropriate for deliberate, repeatable actions. Skills are appropriate for workflows Claude should recognize automatically from natural-language intent.

## 18. Why is the skill description important?

The skill description is the primary trigger for automatic invocation.

If the description is too narrow, Claude may fail to use the skill when it should.

If the description is too broad, Claude may invoke the skill for unrelated requests.

A good description includes concrete triggers such as:

- Update the changelog
- Add a changelog entry
- Write release notes
- Summarize user-facing changes

## 19. What did the changelog skill do?

The changelog skill:

1. Inspected `git status` and `git diff`.
2. Identified the user-facing gift-wrap change.
3. Ignored unrelated or formatting-only changes.
4. Grouped the change under the correct heading.
5. Created or updated `CHANGELOG.md`.
6. Added the entry under `## [Unreleased]`.

The entry described the new gift-wrap fee helper as a short user-facing sentence.

## 20. Why use Git diff for the review and changelog workflows?

Git diff provides a precise view of what changed relative to the committed baseline.

The review command used the diff to identify code-quality and testing issues.

The changelog skill used the same diff to identify user-facing behavior changes.

This prevents the workflows from inventing changes or summarizing unrelated existing code.

## 21. Why was a local Git baseline necessary?

The downloaded starter bundle did not contain its original `.git` metadata.

A local Git repository and baseline commit were created so that:

- `/review` could inspect uncommitted changes.
- The changelog skill could summarize the current diff.
- Demonstration changes could be restored safely.
- The completed lab could be committed with a clean history.

Without a baseline, `git diff` would not provide the intended comparison.

## 22. What was the final implementation result?

The final `gift_wrap_fee()` implementation included:

- A named constant
- A return type hint
- A concise docstring
- Explicit USD documentation
- Appropriate tests
- A passing complete test suite

The final result was:

**7 tests passed**

The changelog also contained the corresponding `[Unreleased]` entry.

## 23. What is the common benefit of storing configuration in the repository?

Repository-based configuration makes team practices:

- Visible
- Repeatable
- Reviewable
- Version-controlled
- Shareable
- Easier to improve through pull requests

Memory sets standing expectations, slash commands standardize deliberate actions, and skills package reusable workflows.

## Key Takeaway

The central lesson from this lab is that Claude Code can be configured as part of the project rather than treated as an unconfigured general assistant.

`CLAUDE.md` establishes standing rules, slash commands standardize recurring actions, and skills automate intent-based workflows. Keeping these resources in Git makes consistent behavior available to every contributor.