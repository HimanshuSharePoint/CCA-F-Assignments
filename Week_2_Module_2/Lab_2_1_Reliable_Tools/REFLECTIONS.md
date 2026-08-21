# Lab 2.1 Reflection Answers

## 1. What does the model use to select a tool?

The model primarily reads the tool name, description, and input schema. It does not inspect or execute the Python implementation while choosing a tool.

## 2. Why do vague tool definitions cause incorrect selection?

Names such as `search` and `lookup` do not identify the business object or operation. Specific names such as `search_products` and `get_order_status` reduce ambiguity.

## 3. Why include “when not to use” guidance?

Positive descriptions may leave boundaries implicit. Negative guidance clearly redirects the model to the sibling tool for the alternative case, making selection more reliable.

## 4. What does the order-ID pattern provide?

The pattern `^NP-[0-9]{6}$` documents and validates the required identifier format. It distinguishes valid IDs such as `NP-100245` from malformed inputs such as `100245`.

## 5. What did the weak-versus-strong comparison show?

Both toolsets scored 6/6 in the recorded run, showing that the model inferred intent from clear questions. The strong set remains safer because it provides precise names, explicit boundaries, typed parameters, and validation.

## 6. Why return tool errors as data?

An exception can terminate the agentic loop before Claude receives the failure. A structured error result remains part of the normal tool-result flow and can be handled by both application logic and the model.

## 7. What do `isError` and `isRetryable` mean?

`isError` states whether the operation failed. `isRetryable` distinguishes temporary failures from permanent failures so retry behavior is deterministic.

## 8. Which errors are retryable?

The lab treated 408, 429, 500, 502, 503, and 504 as retryable because they often represent timeouts, rate limits, or temporary service problems.

## 9. Which errors are permanent?

A 400 malformed-ID response and a 404 not-found response are not retryable. Repeating the same request without changing its input would produce the same failure.

## 10. Why use exponential backoff and an attempt cap?

Backoff reduces pressure on an unhealthy service, while the attempt cap prevents infinite retries, excessive delay, and uncontrolled cost.

## 11. How should 400 and 404 responses differ?

For 400, the agent should request an ID in `NP-XXXXXX` format. For 404, the agent should explain that the correctly formatted order was not found and ask the customer to verify the confirmation details.

## 12. What happened in the 504 test?

The first lookup timed out, the loop waited 0.2 seconds, and the second attempt succeeded. Claude then produced a normal customer response without a Python crash.

## 13. What are the `tool_choice` modes?

`auto` may call a tool or return text. `any` must call some tool but chooses which one. Forced `tool` mode must call one named tool.

## 14. Why is `any` insufficient for deterministic triage?

`any` guarantees a tool call but not the correct tool. Claude could choose `draft_customer_reply` instead of `classify_ticket`.

## 15. Why force the classifier?

Forced mode guarantees that `classify_ticket` is called and that the turn has the expected structure. Business validation must still check whether the selected category is correct.

## 16. Why not force a tool for every turn?

Some turns need flexibility to ask clarifying questions, report missing information, or respond directly. The best practice is to use the narrowest setting that still allows the task to succeed.

## Key Takeaway

Reliable tool use requires strong interfaces, structured error recovery, and deliberate selection control. A larger model cannot replace these application-level controls.
