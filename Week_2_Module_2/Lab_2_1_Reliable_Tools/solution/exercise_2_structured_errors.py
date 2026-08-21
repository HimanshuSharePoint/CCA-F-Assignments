import json
import os
import re
import sys
import time

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
# ORDER-ID FORMAT
# ---------------------------------------------------------

ORDER_ID_PATTERN = r"^NP-[0-9]{6}$"


# ---------------------------------------------------------
# RETRYABLE HTTP STATUS CODES
# ---------------------------------------------------------

RETRYABLE = {
    408,
    429,
    500,
    502,
    503,
    504
}


# ---------------------------------------------------------
# CUSTOM SERVICE ERROR
# ---------------------------------------------------------

class ServiceError(Exception):
    """
    Represents an error returned by the mock Orders service.
    """

    def __init__(self, status, message):
        super().__init__(message)

        self.status = status
        self.message = message


# ---------------------------------------------------------
# MOCK ORDER DATABASE
# ---------------------------------------------------------

ORDERS = {
    "NP-100245": {
        "order_id": "NP-100245",
        "status": "Shipped",
        "items": [
            "NorthPeak Alpine Four-Person Tent"
        ],
        "tracking_number": "NPT-78291456",
        "estimated_delivery": "2026-08-16"
    },
    "NP-100311": {
        "order_id": "NP-100311",
        "status": "Processing",
        "items": [
            "NorthPeak Winter Hiking Boots"
        ],
        "tracking_number": None,
        "estimated_delivery": "2026-08-19"
    },
    "NP-100190": {
        "order_id": "NP-100190",
        "status": "Delivered",
        "items": [
            "NorthPeak Lightweight Sleeping Bag"
        ],
        "tracking_number": "NPT-66031904",
        "estimated_delivery": "2026-08-10"
    }
}


# ---------------------------------------------------------
# FAILURE-INJECTION QUEUE
# ---------------------------------------------------------

FAILURE_QUEUE = {}


def queue_failure(order_id, status, message):
    """
    Adds one simulated service failure for an order.
    """

    if order_id not in FAILURE_QUEUE:
        FAILURE_QUEUE[order_id] = []

    FAILURE_QUEUE[order_id].append(
        {
            "status": status,
            "message": message
        }
    )


def clear_failures():
    """
    Clears all queued mock failures.
    """

    FAILURE_QUEUE.clear()


# ---------------------------------------------------------
# RAW ORDERS SERVICE
# ---------------------------------------------------------

def orders_service(order_id):
    """
    Simulates the raw NorthPeak Orders service.

    This raw service may raise ServiceError.
    The agent should never call this function directly.
    """

    # Validate the order-ID format.
    if not re.fullmatch(ORDER_ID_PATTERN, order_id):
        raise ServiceError(
            400,
            (
                f"Malformed order ID '{order_id}'. "
                "The required format is NP-XXXXXX."
            )
        )

    # Apply a queued temporary or permanent failure.
    queued_failures = FAILURE_QUEUE.get(order_id, [])

    if queued_failures:
        failure = queued_failures.pop(0)

        raise ServiceError(
            failure["status"],
            failure["message"]
        )

    # Return 404 when the correctly formatted order does not exist.
    if order_id not in ORDERS:
        raise ServiceError(
            404,
            f"Order '{order_id}' was not found."
        )

    return dict(ORDERS[order_id])


# ---------------------------------------------------------
# STRUCTURED TOOL WRAPPER
# ---------------------------------------------------------

def call_order_tool(order_id):
    """
    Calls the raw service and always returns structured data.

    ServiceError never escapes this function.
    """

    try:
        data = orders_service(order_id)

        return {
            "isError": False,
            **data
        }

    except ServiceError as error:
        return {
            "isError": True,
            "isRetryable": error.status in RETRYABLE,
            "status": error.status,
            "error": error.message
        }


# ---------------------------------------------------------
# RETRY LOOP
# ---------------------------------------------------------

def run_with_retry(
    order_id,
    max_attempts=4,
    initial_delay=0.2
):
    """
    Retries temporary failures using exponential backoff.

    Permanent failures such as 400 and 404 stop immediately.
    """

    delay = initial_delay

    for attempt in range(1, max_attempts + 1):
        print(
            f"[ATTEMPT {attempt}/{max_attempts}] "
            f"Looking up {order_id}"
        )

        result = call_order_tool(order_id)

        if not result["isError"]:
            print(
                f"[SUCCESS] Order retrieved on attempt {attempt}."
            )

            result["attempts"] = attempt

            return result

        print(
            f"[ERROR] Status {result['status']}: "
            f"{result['error']}"
        )

        if (
            result["isRetryable"]
            and attempt < max_attempts
        ):
            print(
                f"[RETRYABLE] Waiting {delay:.1f} seconds "
                "before retrying."
            )

            time.sleep(delay)

            delay *= 2

            continue

        if not result["isRetryable"]:
            print(
                "[STOP] Permanent error. "
                "The request will not be retried."
            )
        else:
            print(
                "[STOP] Maximum retry attempts reached."
            )

        result["attempts"] = attempt

        return result

    return {
        "isError": True,
        "isRetryable": False,
        "status": 500,
        "error": "Retry loop ended unexpectedly.",
        "attempts": max_attempts
    }


# ---------------------------------------------------------
# CLAUDE TOOL DEFINITION
# ---------------------------------------------------------

ORDER_TOOL = {
    "name": "get_order_status",
    "description": (
        "Retrieve the status of an existing NorthPeak customer "
        "order. Use this when a customer asks about shipping, "
        "tracking, delivery, items, or an existing purchase. "
        "Pass the order identifier exactly as the customer wrote it. "
        "Do not add, remove, correct, or infer any characters."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "order_id": {
                "type": "string",
                "description": (
                    "The order identifier exactly as supplied by "
                    "the customer. Do not add the NP- prefix. "
                    "For example, if the customer writes 100245, "
                    "pass exactly 100245."
                )
            }
        },
        "required": [
            "order_id"
        ]
    }
}


# ---------------------------------------------------------
# EXTRACT TEXT FROM CLAUDE RESPONSE
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


# ---------------------------------------------------------
# LIVE AGENT TURN
# ---------------------------------------------------------

def run_agent_turn(
    customer_question,
    exact_test_order_id=None
):
    """
    Runs one customer-support agentic loop.

    exact_test_order_id is used only to ensure the test service
    receives the literal identifier supplied in a test case.
    """

    print("\nCustomer:")
    print(customer_question)

    messages = [
        {
            "role": "user",
            "content": customer_question
        }
    ]

    iteration = 0

    while True:
        iteration += 1

        print(f"\nAgent iteration: {iteration}")

        response = client.messages.create(
            model=MODEL,
            max_tokens=700,
            system=(
                "You are a customer-support agent for NorthPeak "
                "Outfitters. Use get_order_status when a customer "
                "asks about an existing order. "
                "Pass the customer's order identifier to the tool "
                "exactly as supplied. Never add the NP- prefix and "
                "never correct a malformed identifier. "
                "If the tool reports status 400, explain that the "
                "required format is NP-XXXXXX and ask the customer "
                "for a correctly formatted order ID. "
                "If the tool reports status 404, explain that the "
                "order was not found. "
                "If the tool succeeds, clearly summarize its status, "
                "tracking information, and delivery information. "
                "Never invent missing order details."
            ),
            tools=[
                ORDER_TOOL
            ],
            tool_choice={
                "type": "auto"
            },
            messages=messages
        )

        print(f"stop_reason: {response.stop_reason}")

        # Always append the assistant response before tool results.
        messages.append(
            {
                "role": "assistant",
                "content": response.content
            }
        )

        if response.stop_reason == "end_turn":
            final_text = extract_text(response)

            print("\nAgent response:")
            print(final_text)

            return final_text

        if response.stop_reason == "tool_use":
            tool_results = []

            for block in response.content:
                if block.type != "tool_use":
                    continue

                print(f"\nTool requested: {block.name}")
                print(f"Claude tool input: {block.input}")

                if block.name == "get_order_status":
                    model_order_id = block.input.get(
                        "order_id",
                        ""
                    )

                    # For Case C, preserve the literal malformed
                    # identifier instead of allowing normalization.
                    if exact_test_order_id is not None:
                        order_id = exact_test_order_id

                        print(
                            "Exact test identifier used: "
                            f"{order_id}"
                        )
                    else:
                        order_id = model_order_id

                    result = run_with_retry(order_id)

                else:
                    result = {
                        "isError": True,
                        "isRetryable": False,
                        "status": 400,
                        "error": (
                            f"Unknown tool '{block.name}'."
                        )
                    }

                print("\nStructured tool result:")

                print(
                    json.dumps(
                        result,
                        indent=2
                    )
                )

                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result),
                        "is_error": result["isError"]
                    }
                )

            messages.append(
                {
                    "role": "user",
                    "content": tool_results
                }
            )

            continue

        if response.stop_reason == "max_tokens":
            print(
                "\nThe response reached the token limit."
            )

            return None

        print(
            f"\nUnexpected stop reason: "
            f"{response.stop_reason}"
        )

        return None


# ---------------------------------------------------------
# OFFLINE SELF-CHECK
# ---------------------------------------------------------

def run_offline_check():
    """
    Verifies structured envelopes without calling Claude.
    """

    print("=" * 72)
    print("OFFLINE STRUCTURED-ERROR SELF-CHECK")
    print("=" * 72)

    all_passed = True

    # Check 1: Valid order
    clear_failures()

    print("\nCHECK 1: Valid order succeeds")

    result = call_order_tool("NP-100245")

    print(json.dumps(result, indent=2))

    passed = (
        result["isError"] is False
        and result["order_id"] == "NP-100245"
    )

    print(
        "Result:",
        "PASSED" if passed else "FAILED"
    )

    all_passed = all_passed and passed

    # Check 2: Permanent 404
    clear_failures()

    print(
        "\nCHECK 2: Missing order returns "
        "non-retryable 404"
    )

    result = call_order_tool("NP-999999")

    print(json.dumps(result, indent=2))

    passed = (
        result["isError"] is True
        and result["isRetryable"] is False
        and result["status"] == 404
    )

    print(
        "Result:",
        "PASSED" if passed else "FAILED"
    )

    all_passed = all_passed and passed

    # Check 3: Retryable 503
    clear_failures()

    queue_failure(
        "NP-100245",
        503,
        "Orders service temporarily unavailable."
    )

    print(
        "\nCHECK 3: Queued 503 returns "
        "retryable error"
    )

    result = call_order_tool("NP-100245")

    print(json.dumps(result, indent=2))

    passed = (
        result["isError"] is True
        and result["isRetryable"] is True
        and result["status"] == 503
    )

    print(
        "Result:",
        "PASSED" if passed else "FAILED"
    )

    all_passed = all_passed and passed

    # Check 4: Permanent 400
    clear_failures()

    print(
        "\nCHECK 4: Malformed ID returns "
        "non-retryable 400"
    )

    result = call_order_tool("100245")

    print(json.dumps(result, indent=2))

    passed = (
        result["isError"] is True
        and result["isRetryable"] is False
        and result["status"] == 400
    )

    print(
        "Result:",
        "PASSED" if passed else "FAILED"
    )

    all_passed = all_passed and passed

    print("\n" + "=" * 72)

    if all_passed:
        print("ALL OFFLINE CHECKS PASSED")
    else:
        print("ONE OR MORE OFFLINE CHECKS FAILED")

    print("=" * 72)


# ---------------------------------------------------------
# LIVE DEMONSTRATION
# ---------------------------------------------------------

def run_live_demonstration():
    """
    Runs the live agent over three failure shapes.
    """

    print("=" * 72)
    print(
        "LAB 2.1 - EXERCISE 2: "
        "STRUCTURED ERRORS AND RETRIES"
    )
    print("=" * 72)

    print(f"\nModel: {MODEL}")

    # -----------------------------------------------------
    # CASE A: TEMPORARY 504, THEN SUCCESS
    # -----------------------------------------------------

    clear_failures()

    queue_failure(
        "NP-100245",
        504,
        "The Orders service timed out."
    )

    print("\n" + "=" * 72)
    print("CASE A: TEMPORARY 504, THEN SUCCESS")
    print("=" * 72)

    run_agent_turn(
        "Where is my order NP-100245?"
    )

    # -----------------------------------------------------
    # CASE B: PERMANENT 404
    # -----------------------------------------------------

    clear_failures()

    print("\n" + "=" * 72)
    print("CASE B: PERMANENT 404, NO RETRY")
    print("=" * 72)

    run_agent_turn(
        "Where is my order NP-999999?"
    )

    # -----------------------------------------------------
    # CASE C: MALFORMED ID, PERMANENT 400
    # -----------------------------------------------------

    clear_failures()

    print("\n" + "=" * 72)
    print("CASE C: MALFORMED ORDER ID, NO RETRY")
    print("=" * 72)

    run_agent_turn(
        (
            "Please check the delivery status for the literal "
            "order identifier 100245. Pass 100245 exactly as "
            "written without adding any prefix."
        ),
        exact_test_order_id="100245"
    )

    print("\n" + "=" * 72)
    print("EXERCISE 2 COMPLETED")
    print("=" * 72)


# ---------------------------------------------------------
# MAIN PROGRAM
# ---------------------------------------------------------

if __name__ == "__main__":
    if "--check" in sys.argv:
        run_offline_check()
    else:
        run_live_demonstration()