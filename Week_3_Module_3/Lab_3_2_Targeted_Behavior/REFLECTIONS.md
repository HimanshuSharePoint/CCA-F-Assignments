# Lab 3.2 Reflection Answers

## 1. Where do path-specific rules live?

Path-specific rules live in a `CLAUDE.md` file inside the directory they govern.

This project used:

- `src/auth/CLAUDE.md`
- `src/orders/CLAUDE.md`
- `src/payments/CLAUDE.md`

The root `CLAUDE.md` provides general project instructions, while the nearest module-level `CLAUDE.md` adds rules that apply specifically to files under that path.

## 2. Why use path-specific rules instead of placing every rule in the root file?

Different parts of a project can have different levels of risk.

The authentication module is security-critical, the payments module is money-critical, and the orders module contains lower-risk application logic.

Path-specific rules provide several benefits:

- Strict rules apply only where needed.
- Ordinary modules are not burdened with irrelevant restrictions.
- Sensitive rules remain close to the code they protect.
- Developers can understand module-specific expectations easily.
- Changes to one module's rules do not create noise across the whole repository.

This allows Claude Code's caution to match the risk of the code being modified.

## 3. How does Claude decide which `CLAUDE.md` rules apply?

Claude Code loads the root project instructions and combines them with the instructions nearest to the file being edited.

For example:

- Work under `src/orders/` uses the root rules and `src/orders/CLAUDE.md`.
- Work under `src/auth/` uses the root rules and the stricter `src/auth/CLAUDE.md`.
- Work under `src/payments/` uses the root rules and the money-critical `src/payments/CLAUDE.md`.

The more specific path instructions provide the relevant additional constraints for that module.

## 4. What happened when a low-risk change was requested under `orders`?

Claude added a `count_items(items)` helper to the Orders module.

The change followed the Orders rules by including:

- A small and focused function
- A type hint
- A concise docstring
- An appropriate test
- A complete test-suite run

The change was accepted because it did not weaken security or alter a money-critical calculation.

## 5. What happened when an unsafe change was requested under `auth`?

The request asked Claude to make `verify_token()` accept any token longer than six characters.

Claude challenged the request because the change would weaken production authentication.

The proposed change would have removed important protections such as:

- The required `npk_` prefix
- The stronger minimum-length requirement
- The distinction between valid and arbitrary token strings

Claude did not weaken the production function.

## 6. Why was refusing the authentication change the correct behavior?

Authentication checks protect access to the application.

Weakening a production credential check to make testing easier would create a security vulnerability.

The correct response was to:

1. Refuse the unsafe production change.
2. Explain the security impact.
3. Offer a safe testing alternative.
4. Preserve strict production validation.

This demonstrated that path-specific rules can prevent an unsafe request from being applied blindly.

## 7. What safe alternative was used for authentication testing?

A test-token helper generated a valid-shaped fake token.

The helper produced a token that:

- Used the required `npk_` prefix
- Met the minimum-length requirement
- Contained no real secret
- Could be reused safely in tests

This allowed tests to exercise the real production validation without weakening the check.

## 8. What is Plan mode?

Plan mode allows Claude Code to inspect the repository and propose a detailed implementation plan before modifying files.

Claude waits for approval before executing the plan.

This introduces a review point between analysis and implementation.

Plan mode is useful for:

- Multi-file migrations
- Security-sensitive changes
- Changes with several dependent steps
- Work that requires call-site discovery
- Changes that must include verification and cleanup

## 9. Why was Plan mode appropriate for the token migration?

The migration affected multiple modules:

- `src/auth/tokens.py`
- `src/orders/service.py`
- `src/payments/charges.py`
- Related tests
- Project documentation

Editing immediately could have missed a caller, left a broken import, or removed the deprecated function too early.

Plan mode allowed the complete migration to be reviewed before any edit was made.

## 10. What did the approved migration plan include?

The approved plan included:

1. Grep for every `verify_token_v1` reference.
2. Update the Orders import and function call.
3. Update the Payments import and function call.
4. Add valid-token and weak-token rejection tests.
5. Confirm that no callers remained.
6. Remove the deprecated `verify_token_v1` function.
7. Update outdated documentation.
8. Run the complete test suite.

The plan included both implementation and verification.

## 11. Why migrate every caller before removing `verify_token_v1`?

Removing the deprecated function before updating its callers would break imports and application behavior.

The correct sequence was:

1. Find every caller.
2. Update all imports.
3. Update all function calls.
4. Add regression tests.
5. Verify no callers remain.
6. Remove the deprecated function.

This sequence preserves a valid codebase throughout the migration.

## 12. Why remove the deprecated function after the migration?

Leaving `verify_token_v1` in the repository would allow future code to use the weaker validation again.

Removing it:

- Completes the migration
- Reduces confusion
- Prevents accidental reuse
- Removes dead and unsafe code
- Makes the strict validation function the only supported path

Removal was part of completing the security migration, not optional cleanup.

## 13. Why were migration-specific tests added?

Migration tests proved that both business entry points use strict authentication behavior.

The tests confirmed that:

- A valid `npk_` token is accepted.
- A weak token such as `abc123` is rejected.
- Orders continue to work with valid authentication.
- Payments continue to work with valid authentication.

These tests protect against future regression to weak token validation.

## 14. Why was running the full test suite part of the plan?

A multi-file migration can affect behavior beyond the files that were edited.

Running the full suite verifies:

- Imports remain valid
- Existing behavior still works
- Strict authentication is enforced
- Orders and Payments continue functioning
- Newly added tests pass
- No unrelated regression was introduced

Verification should be an explicit plan step rather than an assumption.

## 15. What is the explorer subagent?

The explorer subagent is a specialized read-only agent for examining unfamiliar code.

Its definition allowed only:

- Read
- Grep
- Glob

The explorer reported:

- Relevant files
- Public APIs
- Dependencies
- Existing validation
- Tests
- Security and financial risks

The explorer could not edit or write files.

## 16. Why was the explorer subagent read-only?

Exploration should gather information without changing the system being studied.

Read-only tools provide several safety benefits:

- The explorer cannot make accidental edits.
- The reported repository state remains unchanged.
- Analysis and implementation stay separate.
- The main agent can review the report before proposing a change.
- Sensitive modules can be investigated safely.

This follows the principle of least privilege.

## 17. Why use a separate explorer instead of asking the main agent to read everything?

A separate explorer keeps discovery focused and isolated from the editing workflow.

The explorer can summarize:

- Module structure
- Public functions
- Dependencies
- Validation rules
- Risks

The main agent then uses the concise report to plan the change.

This reduces context usage and lowers the chance that the implementation begins before the module is understood.

## 18. What did the Payments exploration discover?

The explorer identified:

- `src/payments/charges.py` as the main source file
- `charge(token, amount)` as the public API
- `auth.tokens.verify_token` as an authentication dependency
- Existing rejection of invalid tokens
- Existing rejection of non-positive amounts
- Decimal-based monetary handling
- The absence of an upper transaction limit
- Money-critical testing requirements

No files were changed during exploration.

## 19. Why was an upper payment limit added?

The Payments module handles money-critical behavior.

Without an upper limit, an unexpectedly large charge could be accepted.

The new rule required:

- Amounts up to and including `$10,000` to be accepted
- Amounts above `$10,000` to be rejected
- A clear `ValueError` message
- Boundary tests for both accepted and rejected amounts

This reduces the risk of accidental or unauthorized high-value charges.

## 20. Why use `Decimal` for the payment limit?

Financial calculations should avoid binary floating-point precision issues.

The implementation used a value equivalent to:

`Decimal("10000.00")`

This provides an exact decimal representation of the monetary boundary.

Using `Decimal` makes comparisons and stored financial values more predictable.

## 21. Why test exactly `$10,000` and `$10,000.01`?

These values test both sides of the boundary.

- `$10,000` proves that the maximum allowed value is accepted.
- `$10,000.01` proves that a value immediately above the limit is rejected.

Testing both sides confirms the comparison operator is correct.

For this rule, the implementation must use greater than, not greater than or equal to.

## 22. What did the final test suite prove?

The final result was:

**12 tests passed**

The suite confirmed:

- The Orders helper works.
- Production token validation remains strict.
- Both callers use `verify_token`.
- Weak tokens are rejected.
- The deprecated token function is gone.
- The explorer phase changed no files.
- Exactly `$10,000` is accepted.
- `$10,000.01` is rejected.
- Existing application behavior remains valid.

## 23. How do the three targeted-behavior techniques work together?

Each technique controls a different risk:

### Path-specific rules

Control where stricter behavior applies.

### Plan mode

Controls when edits can begin by requiring plan approval first.

### Explorer subagent

Controls what information is gathered before editing and prevents changes during discovery.

Together, these techniques make Claude cautious in the right module, at the right stage, with the right context.

## Key Takeaway

The main lesson from this lab is that AI-assisted development should not apply the same behavior everywhere.

Risk-sensitive directories need local rules, multi-file changes need plan approval, and unfamiliar modules should be explored read-only before modification.

These controls make Claude Code safer without slowing down ordinary low-risk work.