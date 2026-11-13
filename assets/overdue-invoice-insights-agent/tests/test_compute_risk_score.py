"""Unit tests for compute_risk_score — account risk ranking."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

from datetime import date, timedelta
from invoice_tools import compute_risk_score


def _make_header(partner: str, balance: float, level: str = "1") -> dict:
    return {
        "BusinessPartner": partner,
        "ContractAccount": f"CA-{partner}",
        "CADunningBalance": balance,
        "CADunningLevel": level,
        "TransactionCurrency": "EUR",
        "CANextDunningDate": "",
        "CAMassRunDate": (date.today() - timedelta(days=45)).isoformat(),
    }


def test_empty_returns_empty():
    assert compute_risk_score([]) == []


def test_higher_balance_ranks_higher():
    headers = [
        _make_header("LOW", 1000.0),
        _make_header("HIGH", 50000.0),
    ]
    ranked = compute_risk_score(headers)
    assert ranked[0]["business_partner"] == "HIGH"


def test_blocked_account_gets_bonus():
    headers = [_make_header("BP-A", 10000.0)]
    credit = {"BP-A": {"CreditAccountIsBlocked": True, "CreditRiskClass": "B"}}
    ranked_with_block = compute_risk_score(headers, credit)
    ranked_without = compute_risk_score(headers)
    assert ranked_with_block[0]["risk_score"] > ranked_without[0]["risk_score"]


def test_high_risk_class_adds_bonus():
    headers = [_make_header("BP-X", 10000.0)]
    credit_high = {"BP-X": {"CreditAccountIsBlocked": False, "CreditRiskClass": "C"}}
    credit_low = {"BP-X": {"CreditAccountIsBlocked": False, "CreditRiskClass": "A"}}
    ranked_high = compute_risk_score(headers, credit_high)
    ranked_low = compute_risk_score(headers, credit_low)
    assert ranked_high[0]["risk_score"] > ranked_low[0]["risk_score"]


def test_score_is_between_0_and_1():
    headers = [_make_header(f"BP-{i}", float(i * 1000), str(i % 5)) for i in range(1, 6)]
    ranked = compute_risk_score(headers)
    for item in ranked:
        assert 0.0 <= item["risk_score"] <= 1.0


def test_result_sorted_descending():
    headers = [_make_header(f"BP-{i}", float(i * 5000)) for i in range(1, 5)]
    ranked = compute_risk_score(headers)
    scores = [r["risk_score"] for r in ranked]
    assert scores == sorted(scores, reverse=True)


def test_rationale_contains_balance():
    headers = [_make_header("BP-RAT", 12345.0)]
    ranked = compute_risk_score(headers)
    assert "12345" in ranked[0]["rationale"]
