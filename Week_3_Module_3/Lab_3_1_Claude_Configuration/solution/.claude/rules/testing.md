# Testing Rules

- Add or update tests for every behavior change.
- Use descriptive, sentence-style test names.
- Cover important boundaries and both sides of each boundary.
- Keep tests deterministic and independent.
- Never weaken or delete a valid test to make the suite pass.
- Fix the implementation when a valid test fails.
- Run `python -m pytest -q` before considering work complete.
- The complete test suite must pass.