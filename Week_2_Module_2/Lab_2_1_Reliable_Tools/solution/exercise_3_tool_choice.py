import os
import sys

import anthropic


# Allow Windows Command Prompt to display Unicode safely.
sys.stdout.reconfigure(encoding="utf-8")


# ---------------------------------------------------------
# ANTHROPIC CLIENT AND MODEL
# ---------------------------------------------------------

client = anthropic.Anthropic()

MODEL = os.getenv(
    "ANTHROPIC_MODEL",
    "claude-sonnet-4-6"
)


# ---------------------------------------------------------
# TOOL 1: CLASSIFY TICKET
# ---------------------------------------------------------

CLASSIFY_TOOL = {
    "name": "classify_ticket",
    "description": (
        "Classify a NorthPeak customer-support ticket into "
        "exactly one routing category."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "description": (
                    "The routing category for the ticket."
                ),
                "enum": [
                    "order_issue",
                    "product_question",
                    "return_request",
                    "other"
                ]
            },
            "reason": {
                "type": "string",
                "description": (
                    "A short explanation for the selected category."
                )
            }
        },
        "required": [
            "category",
            "reason"
        ]
    }
}


# ---------------------------------------------------------
# TOOL 2: DRAFT CUSTOMER REPLY
# ---------------------------------------------------------

DRAFT_REPLY_TOOL = {
    "name": "draft_customer_reply",
    "description": (
        "Draft a friendly customer-facing response. "
        "This tool writes replies but does not classify tickets."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "reply": {
                "type": "string",
                "description": (
                    "The customer-facing response draft."
                )
            }
        },
        "required": [
            "reply"
        ]
    }
}


TOOLS = [
    CLASSIFY_TOOL,
    DRAFT_REPLY_TOOL
]


# ---------------------------------------------------------
# TOOL-CHOICE MODES
# ---------------------------------------------------------

MODES = {
    "auto": {
        "type": "auto"
    },
    "any": {
        "type": "any"
    },
    "FORCED": {
        "type": "tool",
        "name": "classify_ticket"
    }
}


# ---------------------------------------------------------
# TEST TICKETS
# ---------------------------------------------------------

TEST_TICKETS = [
    {
        "ticket": (
            "Where is my order NP-100245? "
            "The tracking page has not updated in three days."
        ),
        "expected_category": "order_issue"
    },
    {
        "ticket": (
            "Do you carry a lightweight four-person tent "
            "that can handle heavy rain?"
        ),
        "expected_category": "product_question"
    },
    {
        "ticket": (
            "I need to return the hiking boots from order "
            "NP-100311 because they are the wrong size."
        ),
        "expected_category": "return_request"
    },
    {
        "ticket": (
            "I would like to suggest opening a NorthPeak "
            "retail store in my city."
        ),
        "expected_category": "other"
    }
]


# ---------------------------------------------------------
# RESPONSE HELPERS
# ---------------------------------------------------------

def extract_text(response):
    """
    Extracts all text blocks from a Claude response.
    """

    text_parts = []

    for block in response.content:
        if block.type == "text":
            text_parts.append(block.text)

    return "\n".join(text_parts).strip()


def find_tool_call(response):
    """
    Returns the first tool call from Claude's response.
    """

    for block in response.content:
        if block.type == "tool_use":
            return {
                "name": block.name,
                "input": block.input
            }

    return None


# ---------------------------------------------------------
# RUN ONE TICKET
# ---------------------------------------------------------

def run_ticket(ticket_text, tool_choice):
    """
    Sends one ticket to Claude using the specified
    tool_choice configuration.
    """

    response = client.messages.create(
        model=MODEL,
        max_tokens=500,
        system=(
            "You are a support triage agent for NorthPeak "
            "Outfitters. An incoming support ticket should be "
            "classified before routing. A tool for drafting a "
            "customer reply is also available. Follow the "
            "restrictions in the tool_choice configuration."
        ),
        tools=TOOLS,
        tool_choice=tool_choice,
        messages=[
            {
                "role": "user",
                "content": (
                    "Process this incoming support ticket:\n\n"
                    + ticket_text
                )
            }
        ]
    )

    return {
        "stop_reason": response.stop_reason,
        "tool_call": find_tool_call(response),
        "text": extract_text(response)
    }


# ---------------------------------------------------------
# EVALUATE ONE RESULT
# ---------------------------------------------------------

def evaluate_result(result, expected_category):
    """
    Checks whether Claude called classify_ticket and selected
    the expected category.
    """

    tool_call = result["tool_call"]

    if tool_call is None:
        return {
            "classified": False,
            "correct": False,
            "status": "NO CLASSIFICATION",
            "actual_category": None
        }

    if tool_call["name"] != "classify_ticket":
        return {
            "classified": False,
            "correct": False,
            "status": "WRONG TOOL",
            "actual_category": None
        }

    actual_category = tool_call["input"].get(
        "category"
    )

    if actual_category == expected_category:
        return {
            "classified": True,
            "correct": True,
            "status": "PASSED",
            "actual_category": actual_category
        }

    return {
        "classified": True,
        "correct": False,
        "status": "WRONG CATEGORY",
        "actual_category": actual_category
    }


# ---------------------------------------------------------
# RUN ALL TICKETS UNDER ONE MODE
# ---------------------------------------------------------

def run_mode(mode_name, tool_choice):
    """
    Runs all four tickets using one tool-choice mode.
    """

    print("\n" + "=" * 72)
    print(f"MODE: {mode_name}")
    print("=" * 72)

    classification_count = 0
    correct_count = 0
    results = []

    for number, test_case in enumerate(
        TEST_TICKETS,
        start=1
    ):
        print(f"\nTicket {number}:")
        print(test_case["ticket"])

        print(
            "Expected category: "
            f"{test_case['expected_category']}"
        )

        try:
            result = run_ticket(
                ticket_text=test_case["ticket"],
                tool_choice=tool_choice
            )

        except anthropic.RateLimitError as error:
            print("\nAPI RATE-LIMIT ERROR:")
            print(error)

            return {
                "mode": mode_name,
                "classified": classification_count,
                "correct": correct_count,
                "total": len(TEST_TICKETS),
                "results": results,
                "error": "rate_limit"
            }

        except anthropic.APIError as error:
            print("\nANTHROPIC API ERROR:")
            print(error)

            return {
                "mode": mode_name,
                "classified": classification_count,
                "correct": correct_count,
                "total": len(TEST_TICKETS),
                "results": results,
                "error": "api_error"
            }

        evaluation = evaluate_result(
            result,
            test_case["expected_category"]
        )

        tool_call = result["tool_call"]

        print(
            f"Stop reason:      "
            f"{result['stop_reason']}"
        )

        if tool_call is None:
            print("Tool selected:    None")

            if result["text"]:
                print("Plain-text output:")
                print(result["text"])

        else:
            print(
                f"Tool selected:    "
                f"{tool_call['name']}"
            )

            print(
                f"Tool input:       "
                f"{tool_call['input']}"
            )

        print(
            f"Actual category:  "
            f"{evaluation['actual_category']}"
        )

        print(
            f"Result:           "
            f"{evaluation['status']}"
        )

        if evaluation["classified"]:
            classification_count += 1

        if evaluation["correct"]:
            correct_count += 1

        results.append(
            {
                "ticket_number": number,
                "expected_category": (
                    test_case["expected_category"]
                ),
                "tool_call": tool_call,
                "status": evaluation["status"],
                "correct": evaluation["correct"]
            }
        )

    print("\n" + "-" * 72)

    print(
        f"{mode_name} classifications: "
        f"{classification_count}/{len(TEST_TICKETS)}"
    )

    print(
        f"{mode_name} correct results:  "
        f"{correct_count}/{len(TEST_TICKETS)}"
    )

    print("-" * 72)

    return {
        "mode": mode_name,
        "classified": classification_count,
        "correct": correct_count,
        "total": len(TEST_TICKETS),
        "results": results,
        "error": None
    }


# ---------------------------------------------------------
# FINAL COMPARISON
# ---------------------------------------------------------

def print_comparison(all_results):
    """
    Compares auto, any, and forced modes.
    """

    print("\n" + "=" * 72)
    print("TOOL-CHOICE COMPARISON")
    print("=" * 72)

    print(
        f"{'Mode':<12}"
        f"{'Classifications':<20}"
        f"{'Correct':<12}"
        f"{'Reliable for triage'}"
    )

    print("-" * 72)

    for result in all_results:
        reliable = (
            result["classified"] == result["total"]
            and result["correct"] == result["total"]
        )

        classification_score = (
            f"{result['classified']}/{result['total']}"
        )

        correct_score = (
            f"{result['correct']}/{result['total']}"
        )

        reliable_text = (
            "YES" if reliable else "NO"
        )

        print(
            f"{result['mode']:<12}"
            f"{classification_score:<20}"
            f"{correct_score:<12}"
            f"{reliable_text}"
        )

    print("\nINTERPRETATION:")

    print(
        "1. auto may answer in plain text, select a tool, "
        "or select no tool."
    )

    print(
        "2. any must call a tool, but Claude decides which "
        "available tool to call."
    )

    print(
        "3. FORCED must call the classify_ticket tool."
    )

    print(
        "4. FORCED is the reliable configuration for a "
        "deterministic ticket-triage step."
    )

    print(
        "5. Forced tool selection guarantees the structure "
        "of the turn, but the category should still be "
        "validated using business rules."
    )


# ---------------------------------------------------------
# MAIN PROGRAM
# ---------------------------------------------------------

if __name__ == "__main__":
    print("=" * 72)

    print(
        "LAB 2.1 - EXERCISE 3: "
        "SELECTION CONTROL WITH TOOL_CHOICE"
    )

    print("=" * 72)

    print(f"\nModel: {MODEL}")
    print(f"Test tickets: {len(TEST_TICKETS)}")

    all_results = []

    for mode_name, tool_choice in MODES.items():
        mode_result = run_mode(
            mode_name,
            tool_choice
        )

        all_results.append(mode_result)

        if mode_result["error"] is not None:
            print(
                "\nExecution stopped because "
                "an API error occurred."
            )

            break

    execution_successful = (
        len(all_results) == len(MODES)
        and all(
            result["error"] is None
            for result in all_results
        )
    )

    if execution_successful:
        print_comparison(all_results)

        forced_result = next(
            result
            for result in all_results
            if result["mode"] == "FORCED"
        )

        print("\n" + "=" * 72)

        if (
            forced_result["classified"]
            == forced_result["total"]
        ):
            print(
                "FORCED MODE PRODUCED A CLASSIFICATION "
                "FOR EVERY TICKET"
            )
        else:
            print(
                "FORCED MODE DID NOT CLASSIFY "
                "EVERY TICKET"
            )

        print("=" * 72)

        print("\n" + "=" * 72)
        print("EXERCISE 3 COMPLETED")
        print("=" * 72)