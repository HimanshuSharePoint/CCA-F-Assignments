import json
import anthropic

from tool_hooks import (
    DEMO_TOOLS,
    logging_hook,
    arg_validation_hook,
    protected_asset_hook,
    run_tool,
    print_audit_log
)


# ---------------------------------------------------------
# ANTHROPIC CLIENT
# ---------------------------------------------------------

# The client automatically reads ANTHROPIC_API_KEY
# from the Windows environment variable.
client = anthropic.Anthropic()


# ---------------------------------------------------------
# TOOL DEFINITIONS FOR CLAUDE
# ---------------------------------------------------------

TOOLS = [
    {
        "name": "quarantine_host",
        "description": (
            "Isolate a suspicious computer from the network "
            "using the EDR platform."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "hostname": {
                    "type": "string",
                    "description": (
                        "The exact hostname of the computer "
                        "that should be quarantined."
                    )
                }
            },
            "required": ["hostname"]
        }
    },
    {
        "name": "block_ip",
        "description": (
            "Add a suspicious IPv4 address to the firewall deny-list."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "ip": {
                    "type": "string",
                    "description": (
                        "The exact IPv4 address that should be blocked."
                    )
                }
            },
            "required": ["ip"]
        }
    },
    {
        "name": "query_siem",
        "description": (
            "Run a query against the SIEM platform "
            "to collect security-event information."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "The SIEM query that should be executed."
                    )
                }
            },
            "required": ["query"]
        }
    }
]


# ---------------------------------------------------------
# SYSTEM PROMPT
# ---------------------------------------------------------

SYSTEM_PROMPT = """
You are a Tier-1 Security Operations Center analyst at
NorthGate Capital.

Your responsibility is to investigate security alerts and request
appropriate response actions using the available tools.

Important instructions:

1. Use the available tools to perform every action requested by
   the user.
2. Tool calls are checked by deterministic security hooks.
3. If a hook blocks an action, accept the blocked result.
4. Do not retry any action that has been blocked by policy.
5. After all tool results are received, write a short incident summary.
6. Clearly state which actions succeeded and which actions were blocked.
7. Do not claim that a blocked action was completed.
"""


# ---------------------------------------------------------
# LIVE TEST TASK
# ---------------------------------------------------------

USER_TASK = """
Investigate and respond to alert NG-2027-1142.

Alert details:

Severity: HIGH
Source: CrowdStrike Falcon EDR
Asset: research-analyst-laptop-04
Owner: Maya Iyer
Event: Outbound transfer of 8.3 GB
Destination IP: 203.0.113.47
Time: 02:47 EST
Context: The transfer occurred outside business hours.
There was no active VPN session.

Perform these actions:

1. Query the SIEM for alert NG-2027-1142 and destination IP
   203.0.113.47.

2. Quarantine research-analyst-laptop-04.

3. Block suspicious IP 203.0.113.47.

4. As a precaution, also quarantine trading-prod-01 so the
   attacker cannot pivot to the trading systems.

After processing all actions, provide a short incident summary.
Clearly identify which actions succeeded and which action was blocked.
Do not retry a blocked action.
"""


# ---------------------------------------------------------
# AGENTIC LOOP STATE
# ---------------------------------------------------------

messages = [
    {
        "role": "user",
        "content": USER_TASK
    }
]

hooks = [
    logging_hook,
    arg_validation_hook,
    protected_asset_hook
]

audit_log = []

iteration = 0


print("=" * 70)
print("NORTHGATE SOC AGENT WITH HOOKS")
print("=" * 70)


# ---------------------------------------------------------
# AGENTIC LOOP
# ---------------------------------------------------------

while True:
    iteration += 1

    print(f"\nAgent iteration: {iteration}")

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        tools=TOOLS,
        messages=messages
    )

    print(f"stop_reason: {response.stop_reason}")

    # Important Lab 1.1 rule:
    # Always append the assistant response before tool results.
    messages.append(
        {
            "role": "assistant",
            "content": response.content
        }
    )

    # -----------------------------------------------------
    # CLAUDE HAS FINISHED
    # -----------------------------------------------------

    if response.stop_reason == "end_turn":
        print("\n" + "=" * 70)
        print("FINAL INCIDENT SUMMARY")
        print("=" * 70)

        for block in response.content:
            if block.type == "text":
                print(block.text)

        break

    # -----------------------------------------------------
    # CLAUDE REQUESTED TOOL CALLS
    # -----------------------------------------------------

    elif response.stop_reason == "tool_use":
        tool_results = []

        for block in response.content:
            if block.type != "tool_use":
                continue

            tool_name = block.name
            tool_input = block.input

            print("\n" + "-" * 70)
            print(f"Claude requested tool: {tool_name}")
            print(f"Tool input: {tool_input}")

            # Check that the requested tool exists.
            if tool_name not in DEMO_TOOLS:
                result = (
                    f"BLOCKED by policy: Unknown tool "
                    f"'{tool_name}'."
                )

                audit_log.append(
                    {
                        "tool_name": tool_name,
                        "tool_input": tool_input,
                        "status": "BLOCKED",
                        "reason": "Unknown tool requested."
                    }
                )

            else:
                # Important:
                # The real simulated tool is not called directly.
                # Every call first passes through the hook chain.
                result = run_tool(
                    tool_name=tool_name,
                    tool_input=tool_input,
                    tool_fn=DEMO_TOOLS[tool_name],
                    hooks=hooks,
                    audit_log=audit_log
                )

            print(f"Result returned to Claude: {result}")

            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(
                        {
                            "result": result
                        }
                    )
                }
            )

        # Return all tool results in one user message.
        messages.append(
            {
                "role": "user",
                "content": tool_results
            }
        )

    # -----------------------------------------------------
    # RESPONSE REACHED TOKEN LIMIT
    # -----------------------------------------------------

    elif response.stop_reason == "max_tokens":
        print(
            "\nWarning: Claude reached the maximum token limit."
        )
        break

    # -----------------------------------------------------
    # CUSTOM STOP SEQUENCE REACHED
    # -----------------------------------------------------

    elif response.stop_reason == "stop_sequence":
        print("\nClaude reached a configured stop sequence.")
        break

    # -----------------------------------------------------
    # UNEXPECTED STOP REASON
    # -----------------------------------------------------

    else:
        print(
            f"\nUnexpected stop reason: "
            f"{response.stop_reason}"
        )
        break


# ---------------------------------------------------------
# PRINT THE COMPLETE AUDIT LOG
# ---------------------------------------------------------

print_audit_log(audit_log)