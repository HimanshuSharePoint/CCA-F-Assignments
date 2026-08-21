from northpeak.pricing import (
    GIFT_WRAP_FEE,
    apply_member_discount,
    gift_wrap_fee,
    order_total,
    shipping_cost,
)


def test_member_discount():
    assert apply_member_discount(100.0, True) == 90.0
    assert apply_member_discount(100.0, False) == 100.0


def test_free_shipping_threshold():
    assert shipping_cost(74.99) == 7.95
    assert shipping_cost(75.0) == 0.0


def test_order_total_member_crosses_threshold():
    # 80 -> 72 after discount, which is below the free-shipping threshold.
    assert order_total(80.0, is_member=True) == round(72.0 + 7.95, 2)


def test_negative_subtotal_rejected():
    import pytest
    with pytest.raises(ValueError):
        order_total(-1.0)


def test_gift_wrap_fee_is_a_flat_five_dollars():
    assert gift_wrap_fee() == 5.0


def test_gift_wrap_fee_matches_the_module_constant():
    assert gift_wrap_fee() == GIFT_WRAP_FEE


def test_gift_wrap_fee_does_not_change_the_order_total():
    # The fee is not yet applied by order_total; this pins current behavior.
    assert order_total(100.0) == 100.0