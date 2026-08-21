"""NorthPeak Orders MCP server.

Exposes two tools over STDIO:

1. get_order(order_id)
   Returns one order using its order ID.

2. find_orders_by_email(email)
   Returns all orders belonging to a customer email.

The order data is loaded from:
data/orders.json
"""

import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP


# Create the MCP server.
mcp = FastMCP("northpeak-orders")


# Build an absolute path to data/orders.json.
# This keeps the server working regardless of the current folder.
ORDERS_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "orders.json"
)


def _load_orders() -> dict:
    """
    Load and return all orders from data/orders.json.
    """

    with open(
        ORDERS_PATH,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


@mcp.tool()
def get_order(order_id: str) -> dict:
    """
    Return one order using its order ID.

    Example order ID: NP-100245

    The result contains:
    - order_id
    - status
    - customer email
    - items
    - tracking number
    - order date
    - delivery date

    Returns an error object when the order does not exist.
    """

    orders = _load_orders()
    order = orders.get(order_id)

    if order is None:
        return {
            "error": (
                f"No order found with id {order_id!r}"
            )
        }

    return order


@mcp.tool()
def find_orders_by_email(email: str) -> list:
    """
    Return all orders for a customer email address.

    Email matching is case-insensitive.
    Returns an empty list when no orders match.
    """

    orders = _load_orders()
    normalized_email = email.strip().lower()

    matching_orders = [
        order
        for order in orders.values()
        if order.get(
            "email",
            ""
        ).strip().lower() == normalized_email
    ]

    return matching_orders


if __name__ == "__main__":
    # Start the MCP server using STDIO transport.
    mcp.run()