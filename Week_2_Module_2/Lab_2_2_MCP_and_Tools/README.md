# Lab 2.2 Reflection Answers

## 1. Where are project MCP servers declared and verified?

Project MCP servers are declared in `.mcp.json` at the project root. Claude Code reads the file at startup, and `/mcp` displays connection status and available tools.

## 2. Why use two MCP servers instead of pasted data?

The Orders and Documents servers provide reusable, independently updated sources. Claude retrieves only the information needed, avoids stale copied data, and preserves a visible source trail.

## 3. What did the multi-source question demonstrate?

Claude combined order `NP-100190` from the Orders server with the return-window and condition rules from the Documents server in one answer.

## 4. Why was the item list important?

The `BOOT-` and `FILT-` prefixes determined which footwear and filter conditions applied. General policy text alone could not identify the rules for the purchased items.

## 5. Why did the servers initially fail?

The installed MCP version was incompatible with `mcp.server.fastmcp.FastMCP`. Installing a compatible MCP 1.x release and launching the servers with the virtual-environment interpreter resolved the issue.

## 6. Why use virtual-environment Python in `.mcp.json`?

The required MCP SDK was installed in `.venv`. Using `.venv\Scripts\python.exe` ensured the servers ran with the correct dependencies instead of an unrelated system interpreter.

## 7. What tools did the servers expose?

The Orders server exposed `get_order` and `find_orders_by_email`. The Documents server exposed `list_docs`, `read_doc`, and `search_docs`.

## 8. What is Glob for?

Glob finds files by path and filename pattern. The lab used it to locate both `*.test.ts` files.

## 9. What is Grep for?

Grep searches file contents. It located the deprecated definition and all four active `logEvent(` calls before migration.

## 10. Why read only `analytics.ts` first?

`analytics.ts` defined the replacement signature. Reading only that file revealed that `track()` accepts one `{ name, props }` object instead of two positional arguments.

## 11. Why update imports and edit one file at a time?

Changing calls without imports would break the files. Editing one file at a time kept each change small, reviewable, and easy to approve.

## 12. Why use Edit for source files and Write for `MIGRATION.md`?

Edit is appropriate for targeted changes in existing files. Write is appropriate for creating a new file. Using the wrong tool could overwrite unrelated content or make the operation less precise.

## 13. How was migration verified?

A final Grep showed no live `logEvent(` calls in `notifications.ts` or `orders.ts`; only the deprecated definition and comment remained in `analytics.ts`.

## 14. What did the event rename demonstrate?

Claude used Grep, Read, and Edit to change only `order_cancelled` to `order_canceled` in `orders.ts`, then updated the migration note and verified the source result.

## 15. Why is incremental exploration better than reading everything?

The workflow `Glob → Grep → Read → Edit → Verify` reduces context usage, locates exact evidence, keeps changes minimal, and improves reviewability.

## 16. When is broader reading appropriate?

Broader reading is appropriate when a public interface, shared dependency, architecture, or many related call sites are affected. Reading scope should follow discovery evidence.

## 17. How do MCP and built-in tools reinforce each other?

MCP provides reliable business context, while built-in tools provide precise local actions. Together they enable informed, controlled, and auditable work.

## Key Takeaway

Locate precisely, read narrowly, and change minimally. Reliable data sources and precise coding tools work best together.
