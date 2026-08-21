# Lab 2.2 Reflection Answers

## 1. Where are project MCP servers declared, and how are they verified?

Project-level MCP servers are declared in the `.mcp.json` file located at the project root.

Claude Code reads this configuration when it starts from the project folder. Each server entry specifies the command and arguments required to launch the server.

The project configured two MCP servers:

- `northpeak-orders`
- `northpeak-docs`

The server connections were verified inside Claude Code using:

`/mcp`

The final verification showed:

- `northpeak-orders` connected with two tools
- `northpeak-docs` connected with three tools

## 2. Why use two MCP servers instead of pasting data into the conversation?

The MCP servers provide access to two independent sources of information.

The Orders server provides:

- Order status
- Customer email
- Item SKUs
- Tracking information
- Order and delivery dates

The Documents server provides:

- Returns policy
- Shipping policy
- Warranty policy

Using MCP is better than manually pasting data because:

- Claude 