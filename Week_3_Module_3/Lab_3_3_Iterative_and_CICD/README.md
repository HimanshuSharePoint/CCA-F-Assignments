## Status

Complete. The implementation is available in the `solution` folder.

## Completion Summary

- Added the `opened` refund parameter using a test-first workflow.
- Applied a 15% restocking fee to opened items inside the return window.
- Preserved existing behavior using `opened=False`.
- Verified the red-to-green TDD cycle.
- Ran Claude Code in headless mode with JSON output.
- Generated a structured pull-request review.
- Verified the review gate with pass and fail exit codes.
- Added a GitHub Actions workflow for automated pull-request review.
- Final test result: 14 passed.
``