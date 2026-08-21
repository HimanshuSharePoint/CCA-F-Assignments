import pytest

from northpeak.refunds import within_return_window, refund_amount


def test_within_window_boundary():
    assert within_return_window(0) is True
    assert within_return_window(30) is True
    assert within_return_window(31) is False


def test_full_refund_within_window():
    assert refund_amount(100.0, 10) == 100.0


def test_full_refund_at_window_edge():
    # Day 30 is the last day inside the 30-day window: still a full refund.
    assert refund_amount(100.0, 30) == 100.0


def test_no_refund_after_window():
    assert refund_amount(100.0, 45) == 0.0


def test_no_refund_just_outside_window():
    # Day 31 is the first day outside the window: refund is 0.
    assert refund_amount(100.0, 31) == 0.0


def test_negative_inputs_rejected():
    with pytest.raises(ValueError):
        refund_amount(-1.0, 5)
    with pytest.raises(ValueError):
        within_return_window(-1)


def test_opened_item_within_window_charges_restocking_fee():
    # 15% restocking fee on opened items: 85% of the price comes back.
    assert refund_amount(100.0, 10, opened=True) == 85.0


def test_opened_item_at_window_edge_charges_restocking_fee():
    # Day 30 is still inside the window, so the 85% rule applies.
    assert refund_amount(100.0, 30, opened=True) == 85.0


def test_opened_item_refund_is_rounded_to_cents():
    # 85% of 49.99 is 42.4915, which must round to a whole number of cents.
    assert refund_amount(49.99, 5, opened=True) == 42.49


def test_opened_item_after_window_gets_nothing():
    assert refund_amount(100.0, 45, opened=True) == 0.0


def test_opened_item_just_outside_window_gets_nothing():
    assert refund_amount(100.0, 31, opened=True) == 0.0


def test_unopened_item_still_gets_full_refund():
    assert refund_amount(100.0, 10, opened=False) == 100.0


def test_opened_defaults_to_false_for_existing_callers():
    # Existing callers pass no flag and must keep their full refund.
    assert refund_amount(100.0, 10) == 100.0


def test_negative_price_rejected_for_opened_items():
    with pytest.raises(ValueError):
        refund_amount(-1.0, 5, opened=True)
