# Lab 1.1 Reflection Answers

## 1. What controls the agentic loop?

The agentic loop is controlled by Claude's `stop_reason`.

When the value is `tool_use`, the Python program executes the requested tool, returns the tool result to Claude, and continues the conversation. When the value is `end_turn`, Claude has completed the task and the loop can stop.

This structure allows the model and the application to work together across multiple turns.

## 2. Why must the assistant response be added before the tool result?

The assistant response contains the original tool request and its tool-use ID. The corresponding tool result must reference that existing request.

If the tool result is added first, the conversation order becomes invalid because the result refers to a tool call that has not yet appeared in the message history.

The correct order is:

1. User request
2. Assistant tool request
3. Tool execution
4. User message containing the tool result
5. Assistant continuation or final response

## 3. Why use specialized subagents?

Each subagent has one clear responsibility:

- The Classifier identifies the ticket category and severity.
- The CRM Enricher retrieves relevant customer information.
- The Response Drafter prepares a customer-facing reply.
- The Validator checks the final result for quality and completeness.

This separation makes the pipeline easier to understand, test, debug, and maintain. A problem in one stage can be corrected without rewriting the full workflow.

## 4. Why is explicit context passing 