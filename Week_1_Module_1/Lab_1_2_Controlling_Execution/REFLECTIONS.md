# Lab 1.2 Reflection Answers

## 1. Why use deterministic hooks around tool calls?

Deterministic hooks allow the application to inspect and control every proposed tool action before execution.

The logging hook records the request, the validation hook checks the arguments, and the protected-asset hook applies business rules. This prevents unsafe actions from relying only on the model's judgment.

A model may make a mistake, but a Python policy check always produces the same result for the same input.

## 2. Why should logging run before the other hooks?

Logging should run first so every attempted action is recorded, including actions that are later blocked.

This creates a complete audit trail showing:

- The requested tool
- The supplied arguments
- Whether the action was allowed or blocked
- The reason for a blocked action

Without early logging, rejected actions might disappear from the audit history.

## 3. Why validate tool arguments before checking business policy?

Argument validation confirms that the tool input has the correct structure and format before policy rules use it.

For example, `block_ip` requires a valid IPv4 address. An invalid value such as `999.999.999.999` should be rejected as malformed before checking whether the address is protected.

This separation keeps validation errors distinct from business-policy violations.

## 4. Why must protected assets be enforced outside the model?

Protected assets represent hard business restrictions. The model should not be able to override them through reasoning, retries, or user instructions.

The protected-asset hook prevents actions such as:

- Quarantining a production trading server
- Blocking an approved business-critical IP address
- Disabling a protected executive account

The simulator executes only after every hook returns an allowed result.

## 5. What did the standalone hook demonstration prove?

The standalone demonstration proved that the complete hook chain works without an AI model.

The tests included:

- Allowed laptop quarantine
- Blocked production-server quarantine
- Allowed suspicious-IP block
- Blocked malformed IP address
- Blocked protected business IP
- Blocked empty username
- Blocked executive account
- Allowed SIEM query

All eight attempts were recorded in the audit log.

## 6. What did the live agent with hooks demonstrate?

The live agent demonstrated that Claude-generated tool requests still pass through deterministic Python controls.

Claude could request an action, but the model did not execute the simulator directly. The request first passed through logging, argument validation, and protected-asset policy checks.

This design ensures that a model cannot complete a prohibited action merely by requesting a tool.

## 7. What is fixed decomposition?

Fixed decomposition always follows the same predefined sequence.

The threat-intelligence workflow used these steps:

1. Extract indicators of compromise.
2. Match the indicators against the asset inventory.
3. Produce an executive brief.

This method is suitable when the workflow is stable and each input requires the same processing stages.

## 8. What is adaptive decomposition?

Adaptive decomposition selects a workflow based on the input.

The alert was first classified, then routed to one specialist branch such as:

- Data exfiltration
- Phishing
- Brute force
- Malware
- Lateral movement
- False positive

This method is useful when different input categories require different investigation playbooks.

## 9. When should fixed and adaptive decomposition be used?

Fixed decomposition is appropriate when:

- The process is predictable
- Every request follows the same steps
- Consistency is more important than flexibility

Adaptive decomposition is appropriate when:

- Inputs have different categories
- Different specialists or actions are needed
- The workflow depends on earlier classification results

The two approaches can also be combined. A fixed classification stage can select an adaptive specialist branch.

## 10. Why save investigation sessions?

Saving a session allows an 