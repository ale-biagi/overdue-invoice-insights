"""Unit tests for credit management MCP tool (mocked)."""
import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))


def _load_mock(server: str, tool: str) -> dict:
    mock_path = os.path.join(os.path.dirname(__file__), "..", "mcp-mock.json")
    with open(mock_path) as f:
        data = json.load(f)
    return data["servers"][server]["tools"][tool]["mock_response"]


def test_credit_bp_list_has_results():
    response = _load_mock(
        "sap-s4-credit-management",
        "list_creditmgmtbusinesspartner_for_cds_api_crdtmbusinesspartner"
    )
    assert "results" in response
    assert len(response["results"]) >= 1


def test_credit_bp_has_risk_class():
    response = _load_mock(
        "sap-s4-credit-management",
        "list_creditmgmtbusinesspartner_for_cds_api_crdtmbusinesspartner"
    )
    for item in response["results"]:
        assert "CreditRiskClass" in item


def test_credit_bp_has_score():
    response = _load_mock(
        "sap-s4-credit-management",
        "list_creditmgmtbusinesspartner_for_cds_api_crdtmbusinesspartner"
    )
    for item in response["results"]:
        assert "CreditWorthinessScoreValue" in item


def test_credit_account_has_blocked_flag():
    response = _load_mock(
        "sap-s4-credit-management",
        "list_creditmanagementaccount_for_cds_api_crdtmbusinesspartner"
    )
    for item in response["results"]:
        assert "CreditAccountIsBlocked" in item


def test_credit_account_has_limit():
    response = _load_mock(
        "sap-s4-credit-management",
        "list_creditmanagementaccount_for_cds_api_crdtmbusinesspartner"
    )
    for item in response["results"]:
        assert "CreditLimitAmount" in item


def test_single_credit_bp_lookup():
    response = _load_mock(
        "sap-s4-credit-management",
        "get_creditmgmtbusinesspartner_for_cds_api_crdtmbusinesspartner"
    )
    assert "BusinessPartner" in response
    assert "CreditRiskClass" in response
