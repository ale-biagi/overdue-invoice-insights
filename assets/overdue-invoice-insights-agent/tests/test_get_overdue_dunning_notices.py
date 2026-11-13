"""Unit tests for overdue dunning notices MCP tool (mocked)."""
import sys
import os
import json
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))


def _load_mock_tool_response(server: str, tool: str) -> dict:
    mock_path = os.path.join(os.path.dirname(__file__), "..", "mcp-mock.json")
    with open(mock_path) as f:
        data = json.load(f)
    return data["servers"][server]["tools"][tool]["mock_response"]


def test_cadunning_mock_returns_results():
    response = _load_mock_tool_response("sap-s4-cadunning", "list_cadunning_for_sap_self")
    assert "results" in response
    assert len(response["results"]) >= 1


def test_cadunning_mock_has_required_fields():
    response = _load_mock_tool_response("sap-s4-cadunning", "list_cadunning_for_sap_self")
    required = {"BusinessPartner", "CADunningBalance", "CADunningLevel", "TransactionCurrency"}
    for item in response["results"]:
        for field in required:
            assert field in item, f"Missing field {field}"


def test_cadunning_mock_balance_is_string():
    """SAP OData decimals are strings, not floats."""
    response = _load_mock_tool_response("sap-s4-cadunning", "list_cadunning_for_sap_self")
    for item in response["results"]:
        assert isinstance(item["CADunningBalance"], str)


def test_cadunning_mock_has_two_items():
    response = _load_mock_tool_response("sap-s4-cadunning", "list_cadunning_for_sap_self")
    assert len(response["results"]) == 2


def test_cadunning_single_entity_mock():
    response = _load_mock_tool_response("sap-s4-cadunning", "get_cadunning_for_sap_self")
    assert "BusinessPartner" in response
    assert "CADunningBalance" in response
