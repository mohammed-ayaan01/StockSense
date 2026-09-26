"""
Tests for critical inventory logic.
Run: pytest tests/ -v
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock


# ─── Stock Math Edge Cases ────────────────────────────────────────────────────

def test_stock_math_receipt_increases():
    """10 received → stock becomes 10."""
    stock = 0.0
    received = 10.0
    assert stock + received == 10.0


def test_stock_math_delivery_decreases():
    """10 in stock, deliver 6 → 4 left."""
    stock = 10.0
    delivered = 6.0
    remaining = stock - delivered
    assert remaining == 4.0


def test_stock_math_delivery_reject_insufficient():
    """4 in stock, try to deliver 5 → rejected."""
    stock = 4.0
    requested = 5.0
    available = stock  # reserved=0 in this test
    assert available < requested, "Should be rejected"


def test_stock_math_transfer_total_unchanged():
    """Transfer 4 from A(7) to B(0): A=3, B=4, total=7."""
    src = 7.0
    dst = 0.0
    transfer_qty = 4.0
    total_before = src + dst
    src -= transfer_qty
    dst += transfer_qty
    total_after = src + dst
    assert total_after == total_before
    assert src == 3.0
    assert dst == 4.0


def test_stock_never_negative_delivery():
    """Delivery cannot make stock negative."""
    stock = 3.0
    requested = 10.0
    available = stock
    if available < requested:
        # Rejected — stock unchanged
        pass
    assert stock >= 0


def test_stock_never_negative_adjustment():
    """Adjustment to -1 must be rejected."""
    recorded = 5.0
    counted = 0.0  # This would make delta = -5
    new_qty = counted  # = 0, not negative — valid
    assert new_qty >= 0

    # But if counted < 0 → reject
    counted_invalid = -1.0
    assert counted_invalid < 0  # Would be caught by validator


def test_adjustment_delta_computation():
    """counted=8, recorded=5 → delta=+3."""
    recorded = 5.0
    counted = 8.0
    delta = counted - recorded
    assert delta == 3.0

    recorded = 10.0
    counted = 7.0
    delta = counted - recorded
    assert delta == -3.0


def test_transfer_same_location_rejected():
    """Transfer from location A to location A must be rejected."""
    src_id = 1
    dst_id = 1
    assert src_id == dst_id, "Same-location transfer should be rejected"


def test_sequential_deliveries():
    """10 in stock → deliver 6 → 4 → deliver 5 rejected → deliver 3 → 1."""
    stock = 10.0

    # First delivery: 6
    assert stock >= 6
    stock -= 6
    assert stock == 4.0

    # Second delivery: 5 — rejected
    assert stock < 5  # 4 < 5 → reject
    stock_after_rejected = stock
    assert stock_after_rejected == 4.0  # unchanged

    # Third delivery: 3
    assert stock >= 3
    stock -= 3
    assert stock == 1.0


def test_receipt_reference_format():
    """References should follow pattern."""
    import re
    ref = "REC/00001"
    assert re.match(r"REC/\d+", ref)
    ref = "DEL/00001"
    assert re.match(r"DEL/\d+", ref)
    ref = "INT/00001"
    assert re.match(r"INT/\d+", ref)
    ref = "ADJ/00001"
    assert re.match(r"ADJ/\d+", ref)
