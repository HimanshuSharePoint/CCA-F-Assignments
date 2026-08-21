# Lab 3.3 Reflection Answers

## 1. What are the four stages of the test-driven development loop?

The test-driven loop used in this lab was:

1. Write the failing tests first.
2. Run the test suite and observe the failures.
3. Implement only the required behavior.
4. Run the complete suite again and confirm that all tests pass.

This is commonly described as:

`Write test → Red → Implement → Green`

The tests define the expected behavior before the implementation is written.

## 2. Why must the new tests fail before implementation?

Watching the tests fail proves that they exercise behavior that does not yet exist.

If a new test passes before the implementation changes, the test may be:

- Testing the wrong condition
- Repeating existing behavior
- Missing the intended code path
- Too weak to detect the missing feature

The red stage confirms that the test can detect the absence of the new requirement.

## 3. What new refund behavior was added?

The `refund_amount()` function was updated to accept an `opened` flag.

The new rule was:

- An unopened item inside the return window receives the normal refund.
- An opened item inside the return window receives 85% of its price.
- The remaining 15% is retained as a restocking fee.
- Any item outside the return window receives a refund of zero.

The behavior was added without changing the existing refund-window rule.

## 4. Why does `opened` default to `False`?

The default value preserves backward compatibility.

Existing callers that use:

`refund_amount(price, days_since_delivery)`

continue to behave exactly as before.

Only callers that explicitly use:

`opened=True`

receive the restocking-fee calculation.

Without a default, every existing caller would need to be updated immediately.

## 5. Why use a named restocking-fee constant?

A named constant communicates the business rule more clearly than a number embedded directly in the calculation.

For example:

`RESTOCKING_FEE_RATE = 0.15`

provides several benefits:

- The purpose of the value is clear.
- The rate is defined in one place.
- Future changes are easier.
- Tests and implementation can reference the same business concept.
- The code avoids an unexplained magic number.

## 6. Why should existing tests not be weakened to make the suite pass?

The tests are the executable specification of expected behavior.

Weakening, deleting, or changing a valid test to accommodate incorrect code changes the specification instead of fixing the implementation.

The correct TDD rule is:

**Never weaken a valid test to go green. Fix the code.**

This protects existing behavior from accidental regression.

## 7. What did the red stage show?

The new tests failed because `refund_amount()` did not accept the `opened` keyword argument.

This was the expected failure.

It proved that:

- The new tests reached the intended function.
- The new behavior was not already present.
- The tests would detect whether the implementation was added.
- The project had entered the red stage correctly.

## 8. What did the green stage show?

After adding the `opened` parameter and restocking-fee calculation, the complete test suite passed.

The final result was:

**14 tests passed**

This showed that:

- The opened-item rule was implemented.
- Items outside the window still returned zero.
- Existing unopened-item behavior remained valid.
- Backward compatibility was preserved.
- No original tests were weakened.

## 9. Why were more than two tests added?

The lab required two main scenarios:

- An opened item inside the return window receives 85%.
- An opened item outside the return window receives zero.

Additional tests provided broader boundary and compatibility coverage.

More tests are acceptable when they remain focused, deterministic, and relevant to the business rule.

The important requirement is that the tests fail before implementation and pass afterward without being weakened.

## 10. What is headless Claude execution?

Headless execution runs Claude once without opening an interactive session.

The command uses:

`claude -p "<prompt>"`

The `-p` or print mode sends the prompt, waits for the response, prints the result, and exits.

This behavior is suitable for automation because no human interaction is required during execution.

## 11. Why is headless mode necessary for CI/CD?

A CI runner does not provide an interactive terminal where a person can answer questions or approve prompts.

The process must:

- Start automatically
- Receive predefined input
- Produce a machine-readable result
- Finish with an exit status

Headless Claude satisfies these requirements by running as a one-shot command.

## 12. What did the local headless test demonstrate?

The local command asked Claude to summarize `refunds.py` in one sentence and requested JSON output.

Claude returned a JSON envelope containing fields such as:

- `type`
- `is_error`
- `result`

The assistant’s actual response appeared inside the `result` field.

This confirmed that Claude Code could run non-interactively and produce structured output for automation.

## 13. Why use `--output-format json`?

JSON is easier for software to parse reliably than free-form terminal text.

Structured output allows a later process to inspect fields such as:

- Whether the operation succeeded
- The assistant result
- The review decision
- The list of issues

This makes the output suitable for scripts and CI pipeline steps.

## 14. Why review only the pull-request diff?

The pull-request diff contains the changes introduced by the current branch.

Reviewing only the diff:

- Keeps the review focused
- Reduces unnecessary context
- Avoids reporting unrelated existing code
- Reduces token use
- Makes review feedback more relevant
- Improves review speed

The complete repository can still be read when context is required, but the review target should remain the proposed change.

## 15. Why does the checkout step use `fetch-depth: 0`?

A shallow checkout may not contain enough Git history to compare the pull-request branch with its base branch.

Using:

`fetch-depth: 0`

downloads the full history needed to generate a reliable comparison such as:

`git diff origin/<base>...HEAD`

Without the base history, the workflow may produce an incomplete or invalid diff.

## 16. Why should the Anthropic API key be stored as a GitHub Actions secret?

An API key is a sensitive credential.

Committing the key into the repository could expose it to:

- Repository viewers
- Git history
- Forks
- Logs
- Automated scanners

GitHub Actions secrets provide the key to the workflow at runtime without storing it in source control.

The workflow references:

`secrets.ANTHROPIC_API_KEY`

The actual value must never appear in the repository.

## 17. What did the `/pr-review` command do?

The `/pr-review` command inspected the current Git changes and returned a structured review verdict.

The expected contract was:

- `decision`
- `issues`

The decision was one of:

- `approve`
- `request_changes`

Each issue contained:

- Severity
- Clear message

The command returned JSON only and did not modify files.

## 18. Why return a strict `{decision, issues}` JSON object?

A CI gate must make an unambiguous pass-or-fail decision.

Prose can vary in wording and structure, making it fragile to parse.

A strict JSON contract provides predictable fields that automation can consume.

For example:

- `"decision": "approve"` means the gate can pass.
- `"decision": "request_changes"` means the gate must fail.

The `issues` list provides structured review details for humans and other tools.

## 19. What does `review_gate.py` do?

The review gate reads the structured review result and converts it into a process exit code.

The script handles:

- A bare review object
- A Claude JSON result envelope
- A JSON object stored as a string in `result`
- Accidental Markdown code fences

It then inspects the `decision` field.

## 20. How does the review decision map to an exit code?

The gate uses this mapping:

- `approve` produces exit code `0`
- `request_changes` produces exit code `1`

Exit code `0` means the CI step passed.

A non-zero exit code means the step failed.

This behavior lets the workflow block a pull request when the review requests changes.

## 21. Why use exit codes for the gate?

Exit codes are the standard mechanism used by operating systems and CI platforms to determine command success or failure.

GitHub Actions automatically treats:

- Exit code `0` as success
- A non-zero exit code as failure

This allows a Python script to control whether the pull-request workflow passes or blocks the merge.

## 22. What did the provided review samples demonstrate?

The passing sample contained an approval verdict.

The gate produced:

`PASS`

with exit code:

`0`

The failing sample contained a `request_changes` verdict.

The gate produced:

`FAIL`

with exit code:

`1`

This verified the gate without requiring a live API call.

## 23. Why should the gate tolerate multiple JSON shapes?

The review may arrive as:

- A direct review object
- A JSON envelope from `claude --output-format json`
- A JSON string nested inside the envelope’s `result` field
- Content surrounded by Markdown fences

Handling these expected variations makes the gate more robust without weakening the decision rules.

After normalization, the gate still requires a valid `decision`.

## 24. What did the live structured review demonstrate?

The live `/pr-review` run generated valid JSON and returned an approval decision with advisory issues.

The review gate processed the result and returned:

- `PASS`
- Exit code `0`

This demonstrated the complete path from AI review to deterministic pipeline decision.

## 25. What steps were included in the GitHub Actions workflow?

The workflow included:

1. Trigger on pull requests to `main`.
2. Check out the repository with full Git history.
3. Set up Python.
4. Install project dependencies.
5. Run the pytest suite.
6. Set up Node.js.
7. Install Claude Code.
8. Capture the pull-request diff.
9. Run Claude headlessly.
10. Produce JSON review output.
11. Run `review_gate.py`.
12. Pass or fail the workflow based on the review decision.

## 26. Why run tests before the Claude review?

Tests provide deterministic verification of expected behavior.

Running tests first means:

- Known regressions fail quickly.
- Claude reviews a change that already passed or failed objective checks.
- The workflow combines deterministic tests with AI-assisted review.
- Claude does not replace the test suite.

The two controls complement each other.

## 27. Does AI review replace human review?

No.

AI review can improve consistency and identify common risks, but it can still miss context or produce incorrect judgments.

A production workflow should combine:

- Automated tests
- Static analysis
- Structured AI review
- Deterministic gates
- Human approval for appropriate changes

The AI reviewer is one layer of the quality process.

## 28. What is the end-to-end workflow demonstrated by the lab?

The complete workflow was:

1. Write failing tests for new behavior.
2. Observe the red stage.
3. Implement the feature.
4. Confirm the green stage.
5. Generate a structured review.
6. Convert the review into a pass-or-fail exit code.
7. Run the same process automatically in GitHub Actions.

This connects disciplined local development with automated pull-request protection.

## Key Takeaway

The main lesson from this lab is that Claude Code can support both development and delivery workflows.

Test-driven development defines the expected behavior before implementation. Headless Claude allows AI-assisted review to run without human interaction. Structured JSON and exit codes turn that review into deterministic pipeline automation.

The strongest workflow combines tests, structured AI output, secure credential handling, and explicit CI gates.