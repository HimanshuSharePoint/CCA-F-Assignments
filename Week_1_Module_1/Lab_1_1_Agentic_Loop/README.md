# Lab 1.1: Building the Agentic Loop

## Objective

Build a reliable customer-support triage pipeline using an agentic loop, specialized subagents, explicit context passing, and programmatic gates.

## Concepts Covered

- Anthropic tool calling and `stop_reason`
- Agentic loops
- Coordinator and subagent orchestration
- Explicit context passing
- Python dataclasses for shared state
- Programmatic pipeline gates

## Solution Approach

The solution starts with a `classify_ticket` tool controlled by an agentic loop. It then introduces four independent specialist functions:

1. Classifier
2. CRM Enricher
3. Response Drafter
4. Validator

A `TicketContext` dataclass stores the state produced by each stage. Three gate functions prevent the pipeline from continuing when required data is missing. A sabotage version deliberately removes `severity` to prove that Gate 1 blocks downstream processing.

## Solution Files

- `tools.py`: simulated classification tool
- `loop.py`: agentic loop and tool dispatch
- `subagents.py`: classifier, CRM enricher, drafter, and validator
- `coordinator.py`: sequential subagent orchestration
- `context.py`: `TicketContext` dataclass
- `coordinator_v2.py`: context-based coordinator
- `gates.py`: pipeline gate checks and custom exception
- `coordinator_v3.py`: final protected pipeline
- `coordinator_v3_sabotage.py`: intentional Gate 1 failure test

## Prerequisites

- Python 3.9 or later
- Anthropic Python SDK
- `ANTHROPIC_API_KEY` configured as an environment variable

## Setup

```cmd
pip install anthropic
```

## How to Run

Run the files from the `solution` folder:

```cmd
python loop.py
python coordinator.py
python coordinator_v2.py
python coordinator_v3.py
python coordinator_v3_sabotage.py
```

## Expected Results

- `loop.py` continues until all classification fields are available.
- `coordinator.py` runs all four subagents in sequence.
- `coordinator_v2.py` stores the complete pipeline state in `TicketContext`.
- `coordinator_v3.py` passes all three gates and completes the pipeline.
- `coordinator_v3_sabotage.py` stops at Gate 1 and identifies `severity` as missing.

## Key Learning

Prompt instructions guide model behavior, but deterministic Python checks enforce business rules reliably.
