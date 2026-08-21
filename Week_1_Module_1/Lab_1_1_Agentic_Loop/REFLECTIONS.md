# Lab 1.1 Reflection Answers

## 1. What controls the agentic loop?

The agentic loop is controlled by Claude's `stop_reason`. When the value is `tool_use`, Python executes the requested tool, returns the result, and continues the conversation. When the value is `end_turn`, Claude has completed the task and the loop stops.

## 2. Why must the assistant response be added before the tool result?

The assistant response contains the original tool request and its tool-use ID. The tool result must reference that existing request. Adding the result first would create invalid message ordering because the referenced tool call would not yet exist in the conversation.

The correct order is user request, assistant tool request, tool execution, user tool-result message, and assistant continuation.

## 3. Why use specialized subagents?

Each subagent has one clear responsibility. The Classifier identifies category and severity, the CRM Enricher retrieves customer information, the Response Drafter prepares a reply, and the Validator checks completeness and quality.

This separation makes the workflow easier to understand, test, debug, replace, and maintain.

## 4. Why is explicit context passing important?

Subagents do not automatically share memory. Each subagent must receive the information required for its task. Explicit context passing prevents later stages from guessing missing values and makes the data flow visible and testable.

For example, the Response Drafter needs both classification and CRM information, so both values must be passed explicitly.

## 5. Why use a `TicketContext` dataclass?

`TicketContext` provides one typed object for storing ticket text, classification, severity, customer information, draft response, validation result, and pipeline status.

A dataclass improves type clarity, reduces inconsistent dictionary keys, and makes missing required data easier to identify.

## 6. Why are programmatic gates safer than prompt instructions?

Prompts guide model behavior but do not guarantee execution rules. A model may omit a field or continue with incomplete information. A Python gate is deterministic and prevents later stages from running when a required condition fails.

Prompts guide behavior, while gates enforce behavior.

## 7. What did the sabotage test prove?

The sabotage test set `severity` to `None`. Gate 1 detected the missing value and stopped the pipeline before CRM enrichment, drafting, or validation.

This proved that the workflow fails safely and that downstream stages cannot run with incomplete context.

## 8. What is the benefit of the coordinator pattern?

The coordinator controls execution order and context transfer. It ensures that classification, enrichment, drafting, validation, and gate checks occur in the correct sequence.

This creates one central place for orchestration logic and prevents subagents from running out of order.

## 9. How does this design improve reliability?

Reliability comes from multiple layers: specialized subagents reduce ambiguity, explicit context prevents hidden dependencies, `TicketContext` stores structured state, and gates block invalid execution. The sabotage test verifies the failure path.

## Key Takeaway

An effective agentic system requires more than a capable model. The model performs reasoning, while the application controls orchestration, state, validation, and execution through deterministic code.
