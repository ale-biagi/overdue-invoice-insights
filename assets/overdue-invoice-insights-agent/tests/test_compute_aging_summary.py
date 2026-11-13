"""Unit tests for compute_aging_summary — aging bucket classification."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

from datetime import date, timedelta
from invoice_tools import compute_aging_summary


def _make_item(days_overdue: int, amount: float, partner: str = "BP-001") -> dict:
    due = date.today() - timedelta(days=days_overdue)
    return {
        "BusinessPartner": partner,
        "CADocumentNumber": f"INV-{days_overdue}",
        "CADunningAmount": amount,
        "CANetDueDate": due.isoformat(),
        "TransactionCurrency": "EUR",
    }


def test_empty_items_returns_zero_counts():
    result = compute_aging_summary([])
    for bucket in result["buckets"].values():
        assert bucket["count"] == 0
    assert result["total_items"] == 0


def test_item_exactly_30_days_falls_in_0_30():
    items = [_make_item(30, 1000.0)]
    result = compute_aging_summary(items)
    assert result["buckets"]["0_30"]["count"] == 1
    assert result["buckets"]["31_60"]["count"] == 0


def test_item_31_days_falls_in_31_60():
    items = [_make_item(31, 2000.0)]
    result = compute_aging_summary(items)
    assert result["buckets"]["31_60"]["count"] == 1


def test_item_exactly_60_days_falls_in_31_60():
    items = [_make_item(60, 1500.0)]
    result = compute_aging_summary(items)
    assert result["buckets"]["31_60"]["count"] == 1


def test_item_exactly_90_days_falls_in_61_90():
    items = [_make_item(90, 3000.0)]
    result = compute_aging_summary(items)
    assert result["buckets"]["61_90"]["count"] == 1


def test_item_91_days_falls_in_over_90():
    items = [_make_item(91, 5000.0)]
    result = compute_aging_summary(items)
    assert result["buckets"]["over_90"]["count"] == 1


def test_amount_totals_are_correct():
    items = [
        _make_item(15, 1000.0),
        _make_item(45, 2000.0),
        _make_item(75, 3000.0),
        _make_item(120, 4000.0),
    ]
    result = compute_aging_summary(items)
    assert result["buckets"]["0_30"]["total_amount"] == 1000.0
    assert result["buckets"]["31_60"]["total_amount"] == 2000.0
    assert result["buckets"]["61_90"]["total_amount"] == 3000.0
    assert result["buckets"]["over_90"]["total_amount"] == 4000.0


def test_top_5_customers_sorted_by_amount():
    items = [_make_item(95, float(i * 1000), f"BP-{i:03d}") for i in range(1, 8)]
    result = compute_aging_summary(items)
    top5 = result["buckets"]["over_90"]["top_5_customers"]
    assert len(top5) == 5
    amounts = [c["amount"] for c in top5]
    assert amounts == sorted(amounts, reverse=True)


def test_not_overdue_items_excluded():
    items = [_make_item(-5, 999.0)]  # due in the future
    result = compute_aging_summary(items)
    total = sum(b["count"] for b in result["buckets"].values())
    assert total == 0
