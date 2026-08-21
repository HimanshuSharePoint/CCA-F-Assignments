# Lab 2.2: MCP Servers and Built-in Claude Code Tools

## Objective

Connect multiple MCP servers to Claude Code and use built-in tools to explore and modify a TypeScript project precisely.

## Concepts Covered

- Project-scoped `.mcp.json`
- STDIO MCP servers
- Multiple independent MCP data sources
- Claude Code Glob, Grep, Read, Edit, and Write tools
- Incremental codebase exploration

## Solution Approach

Two local Python MCP servers expose order information and policy documents. Claude Code combines both sources to answer questions that require live order state and return-policy rules.

The TypeScript migration follows an incremental workflow:

1. Glob to find test files
2. Grep to locate deprecated calls
3. Read only the replacement function definition
4. Edit each affected source file
5. Write a migration note
6. Grep again to verify the migration

The final exercise renames one analytics event by locating the exact call site, reading only the relevant file, and changing one line.

## Important Files

- `.mcp.json`
- `requirements.txt`
- `mcp_servers/orders_server.py`
- `mcp_servers/docs_server.py`
- `data/orders.json`
- `data/docs/returns-policy.md`
- `data/docs/shipping-policy.md`
- `data/docs/warranty.md`
- `sample_codebase/src/analytics.ts`
- `sample_codebase/src/notifications.ts`
- `sample_codebase/src/orders.ts`
- `sample_codebase/MIGRATION.md`

## Prerequisites

- Python 3.10 or later
- Claude Code CLI
- MCP Python SDK version 1.x

## Setup

```cmd
python -m venv .venv
.venv\Scriptsctivate
pip install "mcp>=1.2.0,<2.0.0"
claude
```

Inside Claude Code, verify the servers:

```text
/mcp
```

## Expected Results

- `northpeak-orders` connects with two tools.
- `northpeak-docs` connects with three tools.
- Claude combines order `NP-100190` with the returns policy.
- All live `logEvent` calls are migrated to `track({ name, props })`.
- `order_cancelled` is renamed to `order_canceled` in source code.
- Final Grep shows no old source occurrence and one new source occurrence.

## Key Learning

Good external context and precise built-in tools reinforce each other. Locate precisely, read narrowly, and change minimally.
