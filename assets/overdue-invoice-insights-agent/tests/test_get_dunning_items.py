"""Unit tests for dunning items MCP tool (mocked) — including pagination verification."""
import sys
import os
import json
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))


def _load_mock(server: str, tool: str) -> dict:
    mock_path = os.path.join(os.path.dirname(__file__), "..", "mcp-mock.json")
    with open(mock_path) as f:
        data = json.load(f)
    return data["servers"][server]["tools"][tool]["mock_response"]


def test_dunning_items_mock_has_results():
    response = _load_mock("sap-s4-cadunning", "list_cadunningitem_for_sap_self")
    assert "results" in response
    assert len(response["results"]) >= 1


def test_dunning_items_have_net_due_date():
    response = _load_mock("sap-s4-cadunning", "list_cadunningitem_for_sap_self")
    for item in response["results"]:
        assert "CANetDueDate" in item


def test_dunning_items_have_document_number():
    response = _load_mock("sap-s4-cadunning", "list_cadunningitem_for_sap_self")
    for item in response["results"]:
        assert "CADocumentNumber" in item


def test_dunning_items_have_dunning_amount():
    response = _load_mock("sap-s4-cadunning", "list_cadunningitem_for_sap_self")
    for item in response["results"]:
        assert "CADunningAmount" in item


def test_dunning_items_input_schema_has_top_and_skip():
    """Verify the tool schema supports pagination parameters."""
    mock_path = os.path.join(os.path.dirname(__file__), "..", "mcp-mock.json")
    with open(mock_path) as f:
        data = json.load(f)
    schema = data["servers"]["sap-s4-cadunning"]["tools"]["list_cadunningitem_for_sap_self"]["input_schema"]
    assert "$top" in schema["properties"]
    assert "$skip" in schema["properties"]


def test_dunning_items_business_partner_present():
    response = _load_mock("sap-s4-cadunning", "list_cadunningitem_for_sap_self")
    for item in response["results"]:
        assert "BusinessPartner" in item
