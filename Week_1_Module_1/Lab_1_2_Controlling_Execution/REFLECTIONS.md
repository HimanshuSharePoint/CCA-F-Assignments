# Lab 1.2 Reflection Answers

## 1. Why use deterministic hooks around tool calls?

Hooks inspect every proposed action before execution. Logging records the request, validation checks the arguments, and policy hooks enforce protected-asset rules. This prevents destructive operations from depending only on model judgment.

## 2. Why should logging run first?

Logging must record both allowed and blocked attempts. Running it first creates a complete audit trail containing the tool name, arguments, decision, and rejection reason.

## 3. Why validate arguments before applying policy?

Structural validation should identify malformed input before business policy evaluates it. This keeps errors such as an invalid IP address separate from protected-asset violations.

## 4. Why enforce protected assets outside the model?

Protected assets are hard business restrictions. Deterministic Python controls ensure the model cannot override them through retries, user instructions, or reasoning.

## 5. What did the standalone hook demonstration prove?

The standalone tests confirmed that safe actions were allowed, malformed inputs were rejected, protected production assets were blocked, and every attempt was written to the audit log without needing an AI model.

## 6. What did the live agent demonstration prove?

Claude-generated tool calls passed through the same deterministic hook chain. Claude could request an action, but the simulated tool executed only after every hook approved it.

## 7. What is fixed decomposition?

Fixed decomposition always follows a predefined sequence. The threat-intelligence workflow extracted indicators, matched them to assets, and produced an executive brief for every input.

## 8. What is adaptive decomposition?

Adaptive decomposition classifies the input and selects a specialist branch. The lab routed alerts to data-exfiltration, phishing, or brute-force workflows according to alert type.

## 9. When should each decomposition style be used?

Fixed decomposition is suitable for stable, repeatable processes. Adaptive decomposition is suitable when different inputs need different specialists or playbooks. The two methods can be combined.

## 10. Why save investigation sessions?

Saving sessions allows work to survive program closure and analyst shift changes. The JSON record preserves session ID, parent ID, messages, and summary.

## 11. Why fork a session?

Forking creates independent investigation branches from a shared parent. The insider-threat and external-APT branches inherited the same original evidence but maintained separate message lists.

## 12. Why summarize older messages?

Summarization reduces context size while preserving decisions, facts, and open questions. Recent messages remain unchanged so current work retains detailed context.

## 13. Why preserve concrete identifiers?

Alert IDs, IP addresses, hostnames, hashes, legal-hold IDs, and case numbers are essential for investigation continuity, evidence tracking, and handover. A summary that loses these values is operationally unsafe.

## Key Takeaway

Reliable execution requires controls outside the model. Hooks enforce safety, decomposition organizes complex work, and persistent session state supports long-running investigations.
