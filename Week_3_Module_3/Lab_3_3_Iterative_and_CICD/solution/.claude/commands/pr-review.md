---
description: Review the current Git changes and return a strict JSON verdict
allowed-tools: Bash(git diff:*), Bash(git status:*), Read, Grep
---

Review the current uncommitted Git changes.

Check for:

1. Incorrect refund calculations or broken behavior.
2. Missing tests for behavior changes.
3. Tests that were weakened, removed, or changed to hide a defect.
4. Missing input validation.
5. Backward-compatibility problems.
6. Security or financial risks.

Return ONLY valid JSON using this exact structure:

{
  "decision": "approve",
  "issues": []
}

The decision must be either:

- `approve`
- `request_changes`

Each issue must use this structure:

{
  "severity": "blocker",
  "message": "Clear description of the issue."
}

Allowed severities:

- `blocker`
- `warning`
- `nit`

Do not use Markdown fences.
Do not include any text before or after the JSON.
Do not modify any files.