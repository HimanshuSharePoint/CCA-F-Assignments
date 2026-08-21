import os
import sys

import anthropic


# Allow Windows Command Prompt to display Unicode safely.
sys.stdout.reconfigure(encoding="utf-8")


# ---------------------------------------------------------
# ANTHROPIC CLIENT AND MODEL
# ---------------------------------------------------------

# The API key is read automatically from ANTHROPIC_API_KEY.
client = anthropic.Anthropic()

# Read the model from ANTHROPIC_MODEL.
# If it is not configured, use the lab's default Sonnet model.
MODEL = os.getenv(
    "ANTHROPIC_MODEL",
    "claude-sonnet-4-6"
)


# ---------------------------------------------------------
# WEAK TOOL DEFINITIONS
# ---------------------------------------------------------

# These tools have vague names, overlapping descriptions,
# and generic parameters. They make selection difficult.
WEAK_TOOLS = [
    {
        "name": "search",
        "description": "Search for stuff in the system.",
        "input_schema": {
            "type": "object",
            "properties": {
                "q": {
                    "type": "string",
                    "description": "Something to search for."
                }
            },
            "required": ["q"]
        }
    },
    {
        "name": "lookup",
        "description": "Look up information in the system.",
        "input_schema": {
            "type": "object",
            "properties": {
                "q": {
                    "type": "string",
                    "description": "Something to look up."
                }
            },
            "required": ["q"]
        }
    }
]


# ---------------------------------------------------------
# STRONG TOOL DEFINITIONS
# ---------------------------------------------------------

# These tools use:
# 1. Clear object + action names
# 2. When-to-use and when-NOT-to-use descriptions
# 3. Specific and constrained parameters
STRONG_TOOLS = [
    {
        "name": "search_products",
        "description": (
            "Search the NorthPeak product CATALOG for items we sell, "
            "such as tents, sleeping bags, stoves, boots, backpacks, "
            "and outdoor equipment. Use this tool for product "
            "availability, product price, product features, or whether "
            "a particular product exists. Do NOT use this tool to check "
            "something a customer has already purchased. For an existing "
            "purchase or order number, use get_order_status instead."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "Free-text product query, such as "
                        "'four-person tent' or 'waterproof boots'."
                    )
                },
                "max_results": {
                    "type": "integer",
                    "description": (
                        "Maximum number of matching products to return."
                    ),
                    "minimum": 1,
                    "maximum": 10
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_order_status",
        "description": (
            "Retrieve information about an EXISTING NorthPeak customer "
            "order using its order ID. Use this tool when the customer "
            "provides an order number or asks about shipping, tracking, "
            "delivery, order contents, or an existing purchase. "
            "Do NOT use this tool to browse products or check whether "
            "NorthPeak sells an item. For product catalog questions, "
            "use search_products instead."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": (
                        "NorthPeak order ID in the format NP-XXXXXX, "
                        "for example NP-100245."
                    ),
                    "pattern": "^NP-[0-9]{6}$"
                }
            },
            "required": ["order_id"]
        }
    }
]


# ---------------------------------------------------------
# TEST CASES
# ---------------------------------------------------------

# Each question has:
# - The expected business intent
# - The expected weak tool
# - The expected strong tool
TEST_CASES = [
    {
        "question": "Do you carry a four-person tent?",
        "intent": "catalog",
        "weak_expected": "search",
        "strong_expected": "search_products"
    },
    {
        "question": "Where is my order NP-100245?",
        "intent": "order",
        "weak_expected": "lookup",
        "strong_expected": "get_order_status"
    },
    {
        "question": (
            "Do you sell waterproof hiking boots suitable "
            "for winter conditions?"
        ),
        "intent": "catalog",
        "weak_expected": "search",
        "strong_expected": "search_products"
    },
    {
        "question": (
            "Has order NP-100311 shipped yet, and is tracking available?"
        ),
        "intent": "order",
        "weak_expected": "lookup",
        "strong_expected": "get_order_status"
    },
    {
        "question": (
            "What lightweight sleeping bags do you have "
            "for temperatures below freezing?"
        ),
        "intent": "catalog",
        "weak_expected": "search",
        "strong_expected": "search_products"
    },
    {
        "question": (
            "I placed order NP-100190 last week. "
            "When should it arrive?"
        ),
        "intent": "order",
        "weak_expected": "lookup",
        "strong_expected": "get_order_status"
    }
]


# ---------------------------------------------------------
# SELECT A TOOL
# ---------------------------------------------------------

def select_tool(question, tools):
    """
    Sends a customer question to Claude and requires Claude
    to select one of the provided tools.

    tool_choice type 'any' means Claude must call a tool,
    but Claude chooses which available tool to call.
    """

    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        system=(
            "You are the customer-support routing agent for "
            "NorthPeak Outfitters. Read the customer's question "
            "and select the single most appropriate available tool. "
            "Do not answer the customer directly. Make one tool call."
        ),
        tools=tools,
        tool_choice={
            "type": "any"
        },
        messages=[
            {
                "role": "user",
                "content": question
            }
        ]
    )

    # Find the tool_use block in Claude's response.
    for block in response.content:
        if block.type == "tool_use":
            return {
                "tool_name": block.name,
                "tool_input": block.input,
                "stop_reason": response.stop_reason
            }

    # This should not usually happen because tool_choice is "any".
    return {
        "tool_name": None,
        "tool_input": None,
        "stop_reason": response.stop_reason
    }


# ---------------------------------------------------------
# RUN AND SCORE ONE TOOLSET
# ---------------------------------------------------------

def run_toolset_test(toolset_name, tools, expected_key):
    """
    Runs all six questions using one toolset and calculates
    the tool-selection score.
    """

    print("\n" + "=" * 72)
    print(f"{toolset_name} TOOLSET")
    print("=" * 72)

    score = 0
    results = []

    for number, test_case in enumerate(TEST_CASES, start=1):
        question = test_case["question"]
        expected_tool = test_case[expected_key]

        print(f"\nQuestion {number}:")
        print(question)

        try:
            selection = select_tool(question, tools)
            actual_tool = selection["tool_name"]

            if actual_tool == expected_tool:
                status = "OK"
                score += 1
            else:
                status = "MISS"

            result = {
                "question_number": number,
                "question": question,
                "intent": test_case["intent"],
                "expected": expected_tool,
                "actual": actual_tool,
                "status": status,
                "tool_input": selection["tool_input"]
            }

            results.append(result)

            print(f"Expected tool: {expected_tool}")
            print(f"Actual tool:   {actual_tool}")
            print(f"Tool input:    {selection['tool_input']}")
            print(f"Result:        {status}")

        except anthropic.RateLimitError as error:
            print("Result: API RATE LIMIT ERROR")
            print(error)

            return {
                "score": score,
                "total": len(TEST_CASES),
                "results": results,
                "error": "rate_limit"
            }

        except anthropic.APIError as error:
            print("Result: ANTHROPIC API ERROR")
            print(error)

            return {
                "score": score,
                "total": len(TEST_CASES),
                "results": results,
                "error": "api_error"
            }

    print("\n" + "-" * 72)
    print(
        f"{toolset_name} SCORE: "
        f"{score}/{len(TEST_CASES)}"
    )
    print("-" * 72)

    return {
        "score": score,
        "total": len(TEST_CASES),
        "results": results,
        "error": None
    }


# ---------------------------------------------------------
# PRINT COMPARISON
# ---------------------------------------------------------

def print_comparison(weak_result, strong_result):
    """
    Prints a final comparison of weak and strong selection scores.
    """

    print("\n" + "=" * 72)
    print("FINAL TOOL-INTERFACE COMPARISON")
    print("=" * 72)

    print(
        f"Weak toolset score:   "
        f"{weak_result['score']}/{weak_result['total']}"
    )

    print(
        f"Strong toolset score: "
        f"{strong_result['score']}/{strong_result['total']}"
    )

    improvement = (
        strong_result["score"]
        - weak_result["score"]
    )

    print(f"Score improvement:    {improvement}")

    print("\nINTERPRETATION:")

    if strong_result["score"] > weak_result["score"]:
        print(
            "The strong tool interfaces produced more reliable "
            "tool selection using the same model."
        )
    elif strong_result["score"] == weak_result["score"]:
        print(
            "Both toolsets received the same score on this run. "
            "The strong toolset is still safer because its names, "
            "descriptions, and parameter schemas clearly define "
            "the boundary between catalog and order requests."
        )
    else:
        print(
            "The weak toolset scored higher on this individual run. "
            "Because model output can vary, rerun the harness and "
            "compare multiple runs. Review any strong-tool misses."
        )

    print("\nStrong interface improvements:")

    print(
        "1. Names identify the object and action: "
        "search_products and get_order_status."
    )

    print(
        "2. Descriptions explain both when to use and "
        "when not to use each tool."
    )

    print(
        "3. Parameters are specific and typed."
    )

    print(
        "4. order_id is constrained to the format NP-XXXXXX."
    )


# ---------------------------------------------------------
# MAIN PROGRAM
# ---------------------------------------------------------

if __name__ == "__main__":
    print("=" * 72)
    print("LAB 2.1 - EXERCISE 1: TOOL INTERFACES")
    print("=" * 72)

    print(f"\nModel: {MODEL}")
    print(f"Test cases: {len(TEST_CASES)}")

    # Run the same six questions against the weak toolset.
    weak_result = run_toolset_test(
        toolset_name="WEAK",
        tools=WEAK_TOOLS,
        expected_key="weak_expected"
    )

    # Only continue if the first run did not encounter an API error.
    if weak_result["error"] is None:
        # Run the same six questions against the strong toolset.
        strong_result = run_toolset_test(
            toolset_name="STRONG",
            tools=STRONG_TOOLS,
            expected_key="strong_expected"
        )

        if strong_result["error"] is None:
            print_comparison(
                weak_result,
                strong_result
            )

            print("\n" + "=" * 72)
            print("EXERCISE 1 COMPLETED")
            print("=" * 72)
        else:
            print(
                "\nThe strong-tool test could not finish "
                "because of an API error."
            )
    else:
        print(
            "\nThe weak-tool test could not finish "
            "because of an API error."
        )