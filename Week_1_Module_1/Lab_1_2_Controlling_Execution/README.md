# Lab 1.2: Controlling Execution

## Objective

Build production-style execution controls for a security operations copilot using deterministic hooks, fixed and adaptive task decomposition, and persistent session state.

## Concepts Covered

- Logging, validation, and policy-blocking hooks
- Tool interception before side effects
- Fixed and adaptive decomposition
- Session save and resume
- Session forking
- Structured session summarization

## Solution Approach

The hook engine checks every proposed response action before the simulated tool executes. Safe actions are allowed, malformed requests are rejected, and protected production assets are blocked. A live agent version routes Claude tool calls through the same hook chain.

The decomposition exercise implements both a fixed threat-intelligence digest and an adaptive alert-triage router. The session manager demonstrates save, resume, independent forks, and structured summarization while preserving concrete values such as alert IDs, IP addresses, hashes, and legal-hold IDs.

## Solution Files

- `tool_hooks.py`: deterministic log, validation, and protected-asset hooks
- `agent_with_hooks.py`: live agentic loop protected by the hook chain
- `decompose.py`: fixed and adaptive decomposition workflows
- `session_manager.py`: save, resume, fork, and summarize operations

## Prerequisites

- Python 3.9 or later
- Anthropic Python SDK
- `ANTHROPIC_API_KEY` configured for live model calls

## Setup

```cmd
pip install anthropic
```

## How to Run

```cmd
python tool_hooks.py
python -X utf8 agent_with_hooks.py
python -X utf8 decompose.py
python -X utf8 session_manager.py
```

## Expected Results

- The hook engine records all allowed and blocked attempts.
- Protected assets such as `trading-prod-01` are never quarantined.
- The fixed pipeline always runs extract, enrich, and brief in order.
- Adaptive triage routes alerts to data-exfiltration, phishing, and brute-force branches.
- Sessions survive save and resume operations.
- Forked branches share a parent but maintain separate message lists.
- Summarization retains critical IDs, IPs, hostnames, hashes, and legal-hold values.

## Key Learning

A model should not be the final authority for destructive operations. Deterministic hooks must enforce safety before side effects occur.
