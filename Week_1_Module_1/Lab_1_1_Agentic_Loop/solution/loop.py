import json
import anthropic

from tools import classify_ticket


# Create the Anthropic client.
# It automatically reads ANTHROPIC_API_KEY from Windows.
client = anthropic.Anthropic()


# Register the Python function as a tool Claude can request.
tools = [
    {
        "name": "classify_ticket",
        "description": (
            "Classify a customer-support ticket. "
            "Use this tool to obtain product_area, severity, and intent."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "ticket_text": {
                    "type": "string",
                    "description": "The complete customer-support ticket text."
                },
                "fields_needed": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": [
                            "product_area",
                            "severity",
                            "intent"
                        ]
                    },
                    "description": (
                        "The classification fields that are still needed."
                    )
                }
            },
            "required": [
                "ticket_text",
                "fields_needed"
            ]
        }
    }
]


# Test ticket provided in the lab.
ticket = """
From: sarah.chen@globalcorp.com
Subject: Cannot access SSO login - entire team locked out

Our team of 40 has been unable to log in via SSO since
09:00 this morning. We have a client demo in 3 hours.
This is completely blocking us.
"""


# The first message sent to Claude.
messages = [
    {
        "role": "user",
        "content": f"""
Fully classify the following customer-support ticket.

You must confirm all three fields:
1. product_area
2. severity
3. intent

Use the classify_ticket tool as many times as necessary.
Do not finish until all three fields are available.

Ticket:
{ticket}
"""
    }
]


iteration = 0

while True:
    iteration += 1

    # Send the current conversation to Claude.
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1000,
        tools=tools,
        messages=messages
    )

    print(f"\nIteration: {iteration}")
    print(f"stop_reason: {response.stop_reason}")

    # Mandatory: append Claude's response before tool results.
    messages.append(
        {
            "role": "assistant",
            "content": response.content
        }
    )

    # Claude has completed the task.
    if response.stop_reason == "end_turn":
        print("\nFinal classification:")

        for block in response.content:
            if block.type == "text":
                print(block.text)

        break

    # Claude wants to use one or more tools.
    elif response.stop_reason == "tool_use":
        tool_results = []

        for block in response.content:
            if block.type == "tool_use":
                print(f"Tool requested: {block.name}")
                print(f"Tool input: {block.input}")

                if block.name == "classify_ticket":
                    result = classify_ticket(**block.input)
                else:
                    result = {
                        "error": f"Unknown tool: {block.name}"
                    }

                print(f"Tool result: {result}")

                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result)
                    }
                )

        # Return all tool results to Claude in one user message.
        messages.append(
            {
                "role": "user",
                "content": tool_results
            }
        )

    # Response was cut because it reached the token limit.
    elif response.stop_reason == "max_tokens":
        print("\nWarning: Claude reached the token limit.")
        break

    # A configured stop sequence was reached.
    elif response.stop_reason == "stop_sequence":
        print("\nClaude reached a stop sequence.")
        break

    # Handle any unexpected response.
    else:
        print(f"\nUnexpected stop reason: {response.stop_reason}")
        break