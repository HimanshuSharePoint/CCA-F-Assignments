# Lab 2.1 Reflection Answers

## 1. What information does the model use to select a tool?

The model selects a tool based primarily on three interface elements:

1. The tool name
2. The tool description
3. The input parameter schema

The model does not execute or inspect the Python implementation while deciding which tool to call. Therefore, the quality of the interface directly affects tool-selection reliability.

## 2. Why do vague tool names and descriptions cause incorrect selection?

Vague names such as `search` and `lookup` do not clearly explain what object or business operation the tool handles.

Descriptions such as “search for stuff” also create overlapping boundaries. The model must infer whether a customer is asking about the product catalog or an existing order.

Specific names such as `search_products` and `get_order_status` clearly communicate the object and action, reducing ambiguity.

## 3. Why include “when not to use” guidance in a tool description?

Positive descriptions explain what a tool can do, but they may not clearly define the boundary between similar tools.

Explicit negative guidance improves selection by stating which tool should handle the alternative case.

For example:

- `search_products` should not be used for an existing purchase.
- `get_order_status` should not be used to browse the product catalog.

This contrast helps the model separate overlapping customer intents.

## 4. What does the order-ID pattern provide?

The pattern `^NP-[0-9]{6}$` defines the required order-ID structure.

It helps the model understand the expected input and allows malformed values to be rejected at the interface or validation boundary.

For example:

- `NP-100245` is valid.
- `100245` is malformed.
- `NP-ABC123` is malformed.

The pattern improves routing, validation, and downstream service reliability.

## 5. What did the weak-versus-strong tool comparison demonstrate?

Both weak and strong toolsets scored 6 out of 6 during the recorded run.

This showed that the model could infer the intended operation from the clear test questions, even when tool names were vague.

However, the strong toolset remains safer because it provides:

- Specific names
- Clear business boundaries
- Explicit negative guidance
- Typed parameters
- Order-ID validation

A single successful run does not remove the need for a strong production interface.

## 6. Why should tool failures be returned as data instead of exceptions?

A Python exception can terminate the agentic loop before the model receives information about the failure.

A structured error result allows the application and model to inspect the failure and decide what should happen next.

The structured envelope used fields such as:

- `isError`
- `isRetryable`
- `status`
- `error`

This allows failures to remain part of the normal tool-result flow.

## 7. What is the purpose of `isError`?

`isError` indicates whether the tool operation succeeded or failed.

When `isError` is `False`, the result contains valid order information.

When `isError` is `True`, the result contains structured information about the failure instead of raising an unhandled exception.

## 8. What is the purpose of `isRetryable`?

`isRetryable` distinguishes temporary failures from permanent failures.

Temporary failures may succeed if the request is attempted again. Permanent failures cannot be corrected through repetition.

This field allows the retry loop to behave deterministically.

## 9. Which failures are retryable?

The retryable status codes in this lab were:

- 408
- 429
- 500
- 502
- 503
- 504

These statuses often represent a timeout, rate limit, or temporary service problem.

The retry loop waits and attempts the request again while attempts remain.

## 10. Which failures are not retryable?

The two important permanent failures were:

- `400`: malformed request or invalid order-ID format
- `404`: correctly formatted order not found

Retrying either request without changing the input would produce the same failure, so the loop stops immediately.

## 11. Why use exponential backoff?

Exponential backoff increases the delay between retry attempts.

The demonstration used delays such as:

- 0.2 seconds
- 0.4 seconds
- 0.8 seconds

This reduces pressure on a service that may already be overloaded or unavailable.

Without backoff, repeated requests