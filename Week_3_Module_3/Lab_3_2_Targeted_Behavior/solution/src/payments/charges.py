"""Payment charges for NorthPeak."""

from __future__ import annotations

from decimal import Decimal

from auth.tokens import verify_token

CENTS = Decimal("0.01")
MAX_CHARGE = Decimal("10000.00")


def charge(token: str, amount: Decimal | float | str) -> dict:
    """Charge an amount if the caller's token is valid.

    The amount must be positive and no greater than MAX_CHARGE.
    """
    if not verify_token(token):
        raise PermissionError("invalid token")
    amount = Decimal(str(amount))
    if amount <= 0:
        raise ValueError("amount must be positive")
    if amount > MAX_CHARGE:
        raise ValueError(f"amount must not exceed {MAX_CHARGE}")
    return {"charged": True, "amount": amount.quantize(CENTS)}
