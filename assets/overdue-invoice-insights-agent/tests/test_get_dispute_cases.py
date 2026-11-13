"""Unit tests for dispute case MCP tool (mocked)."""
import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))


def _load_mock(server: str, tool: str) -> dict:
    mock_path = os.path.join(os.path.dirname(__file__), "..", "mcp-mock.json")
    with open(mock_path) as f:
        data = json.load(f)
    return data["servers"][server]["tools"][tool]["mock_response"]


def test_dispute_case_list_has_results():
    response = _load_mock("sap-s4-dispute-case", "list_disputecase_for_sap_self")
    assert "results" in response
    assert len(response["results"]) >= 1


def test_dispute_case_has_uuid():
    response = _load_mock("sap-s4-dispute-case", "list_disputecase_for_sap_self")
    for item in response["results"]:
        assert "CaseUUID" in item


def test_dispute_case_has_disputed_amount():
    response = _load_mock("sap-s4-dispute-case", "list_disputecase_for_sap_self")
    for item in response["results"]:
        assert "DisputedAmount" in item


def test_dispute_case_has_remaining_amount():
    response = _load_mock("sap-s4-dispute-case", "list_disputecase_for_sap_self")
    for item in response["results"]:
        assert "CARemainingDisputedAmount" in item


def test_dispute_case_has_status():
    response = _load_mock("sap-s4-dispute-case", "list_disputecase_for_sap_self")
    for item in response["results"]:
        assert "CaseStatus" in item
        assert "CaseStatusName" in item


def test_dispute_case_has_creation_date():
    response = _load_mock("sap-s4-dispute-case", "list_disputecase_for_sap_self")
    for item in response["results"]:
        assert "CaseCreationDate" in item


def test_dispute_case_single_entity():
    response = _load_mock("sap-s4-dispute-case", "get_disputecase_for_sap_self")
    assert "CaseUUID" in response
    assert "DisputedAmount" in response


def test_dispute_input_schema_has_filter():
    mock_path = os.path.join(os.path.dirname(__file__), "..", "mcp-mock.json")
    with open(mock_path) as f:
        data = json.load(f)
    schema = data["servers"]["sap-s4-dispute-case"]["tools"]["list_disputecase_for_sap_self"]["input_schema"]
    assert "$filter" in schema["properties"]
