from decimal import Decimal

import pytest

from conftest import make_test_token

from auth.tokens import verify_token
from orders.service import count_items, place_order
from payments.charges import charge

GOOD = make_test_token()


def test_verify_token():
    assert verify_token(GOOD) is True
    assert verify_token("short") is False


def test_verify_token_accepts_valid_shapes():
    assert verify_token(make_test_token()) is True
    assert verify_token(make_test_token("0123456789")) is True


def test_verify_token_rejects_invalid_shapes():
    assert verify_token("npk_short") is False  # right prefix, too short
    assert verify_token("abc_test_abc123456") is False  # long enough, wrong prefix
    assert verify_token("") is False
    assert verify_token(None) is False


def test_place_order():
    out = place_order(GOOD, [{"name": "Tent", "price": 289.0}])
    assert out["placed"] and out["item_count"] == 1


def test_place_order_subtotal_is_exact_decimal():
    out = place_order(GOOD, [{"price": "0.1"}, {"price": "0.2"}])
    assert out["subtotal"] == Decimal("0.30")


def test_count_items():
    assert count_items([]) == 0
    assert count_items([{"price": "1.00"}, {"price": "2.00"}]) == 2
    with pytest.raises(ValueError):
        count_items("not a list")


def test_charge():
    out = charge(GOOD, "50.00")
    assert out["charged"] is True
    assert out["amount"] == Decimal("50.00")


def test_place_order_rejects_weak_token():
    # "abc123" passed the old verify_token_v1 (6+ chars); the strict check rejects it.
    with pytest.raises(PermissionError):
        place_order("abc123", [{"price": "1.00"}])


def test_charge_rejects_weak_token():
    with pytest.raises(PermissionError):
        charge("abc123", "50.00")


def test_charge_rejects_non_positive_amount():
    for bad in ("0", "0.00", "-5", "-0.01"):
        with pytest.raises(ValueError, match="amount must be positive"):
            charge(GOOD, bad)


def test_charge_accepts_maximum_amount():
    out = charge(GOOD, "10000.00")
    assert out["charged"] is True
    assert out["amount"] == Decimal("10000.00")


def test_charge_rejects_amount_over_maximum():
    with pytest.raises(ValueError, match="must not exceed"):
        charge(GOOD, "10000.01")
