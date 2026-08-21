# Lab 2.1: Designing Reliable Tools

## Objective

Improve model tool use through precise interfaces, structured error envelopes, retry control, and deterministic `tool_choice` settings.

## Concepts Covered

- Weak versus strong tool interfaces
- Tool names, descriptions, and typed schemas
- Structured `isError` and `isRetryable` results
- Exponential backoff and retry caps
- `tool_choice` modes: auto, any, and forced tool

## Solution Approach

Exercise 1 compares vague tools with strongly defined catalog and order tools across six support questions. Exercise 2 wraps a simulated Orders service so failures return structured dictionaries instead of exceptions. Temporary failures retry with backoff, while `400` and `404` failures stop immediately. Exercise 3 compares three tool-selection modes and proves that forced mode guarantees a `classify_ticket` call.

## Solution Files

- `exercise_1_tool_interfaces.py`
- `exercise_2_structured_errors.py`
- `exercise_3_tool_choice.py`

## Prerequisites

- Python 3.9 or later
- Anthropic Python SDK
- `ANTHROPIC_API_KEY`

## Setup

```cmd
pip install anthropic
```

## How to Run

```cmd
python -X utf8 exercise_1_tool_interfaces.py
python -X utf8 exercise_2_structured_errors.py --check
python -X utf8 exercise_2_structured_errors.py
python -X utf8 exercise_3_tool_choice.py
```

## Expected Results

- Strong tool definitions route catalog and order questions correctly.
- The offline error checks all pass.
- A temporary `504` failure retries and succeeds on the next attempt.
- A `404` not-found result stops without retrying.
- A malformed ID returns a non-retryable `400` result.
- Forced mode produces a classification for every ticket.

## Key Learning

Reliable tool use depends on strong interfaces, recoverable error data, and choosing the narrowest tool-selection setting that still fits the task.
