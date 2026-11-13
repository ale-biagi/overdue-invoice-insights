"""Integration test: full agent flow with mocked LLM and MCP tools."""
import sys
import os
import asyncio
import json
from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

import pytest
from langchain_core.messages import AIMessage
from langchain_core.tools import StructuredTool


def _make_mock_dunning_tool() -> StructuredTool:
    """Return a mock dunning tool that returns predictable overdue data."""
    def list_dunning(**kwargs):
        return json.dumps({
            "results": [
                {
                    "BusinessPartner": "BP-HIGH",
                    "ContractAccount": "CA-HIGH",
                    "CADunningBalance": "75000.00",
                    "CADunningLevel": "3",
                    "CANextDunningDate": "2026-10-01",
                    "TransactionCurrency": "EUR",
                    "CAMassRunDate": (date.today() - timedelta(days=95)).isoformat(),
                    "CAMassRunID": "RUN01",
                    "CADunningCounter": "000001",
                },
                {
                    "BusinessPartner": "BP-MED",
                    "ContractAccount": "CA-MED",
                    "CADunningBalance": "12000.00",
                    "CADunningLevel": "1",
                    "CANextDunningDate": "2026-10-15",
                    "TransactionCurrency": "EUR",
                    "CAMassRunDate": (date.today() - timedelta(days=35)).isoformat(),
                    "CAMassRunID": "RUN01",
                    "CADunningCounter": "000002",
                },
            ]
        })
    return StructuredTool.from_function(
        func=list_dunning,
        name="list_cadunning_for_sap_self",
        description="List overdue dunning records",
    )


def _make_mock_dispute_tool() -> StructuredTool:
    """Return a mock dispute tool with no open disputes."""
    def list_disputes(**kwargs):
        return json.dumps({"results": []})
    return StructuredTool.from_function(
        func=list_disputes,
        name="list_disputecase_for_sap_self",
        description="List dispute cases",
    )


def _make_mock_credit_tool() -> StructuredTool:
    """Return a mock credit tool."""
    def list_credit(**kwargs):
        return json.dumps({
            "results": [
                {"BusinessPartner": "BP-HIGH", "CreditRiskClass": "C", "CreditWorthinessScoreValue": "300"},
            ]
        })
    return StructuredTool.from_function(
        func=list_credit,
        name="list_creditmgmtbusinesspartner_for_cds_api_crdtmbusinesspartner",
        description="List credit management business partners",
    )


@pytest.fixture()
def mock_tools():
    return [_make_mock_dunning_tool(), _make_mock_dispute_tool(), _make_mock_credit_tool()]


@pytest.mark.asyncio
async def test_agent_invoke_returns_completed_status(mock_tools):
    """Agent invoke returns a completed status with a non-empty message."""
    canned_response = (
        "Based on the overdue invoice data, your top high-risk accounts are:\n"
        "1. BP-HIGH — overdue balance 75,000 EUR, dunning level 3 (90+ days overdue)\n"
        "2. BP-MED — overdue balance 12,000 EUR, dunning level 1 (31–60 days overdue)"
    )

    mock_message = AIMessage(content=canned_response)
    mock_result = {"messages": [mock_message]}

    with patch("agent.SampleAgent._invoke_with_fallback", new=AsyncMock(return_value=mock_result)):
        from agent import SampleAgent
        agent = SampleAgent()
        response = await agent.invoke(
            query="Which accounts are highest risk?",
            context_id="test-context-001",
            tools=mock_tools,
        )

    assert response.status == "completed"
    assert "BP-HIGH" in response.message or len(response.message) > 0


@pytest.mark.asyncio
async def test_agent_stream_yields_processing_then_result(mock_tools):
    """Agent stream yields a processing update then a final completed result."""
    canned_response = "Here is the aging analysis for your overdue invoices."
    mock_message = AIMessage(content=canned_response)
    mock_result = {"messages": [mock_message]}

    with patch("agent.SampleAgent._invoke_with_fallback", new=AsyncMock(return_value=mock_result)):
        from agent import SampleAgent
        agent = SampleAgent()
        chunks = []
        async for chunk in agent.stream(
            query="Show me aging distribution",
            context_id="test-context-002",
            tools=mock_tools,
        ):
            chunks.append(chunk)

    # First chunk should be a working status
    assert chunks[0]["is_task_complete"] is False
    # Last chunk should be complete
    assert chunks[-1]["is_task_complete"] is True
    assert chunks[-1]["content"] == canned_response


@pytest.mark.asyncio
async def test_agent_handles_tool_error_gracefully(mock_tools):
    """Agent returns a non-empty message when invocation raises an exception.

    The agent wraps exceptions and returns a completed response with an
    error message rather than propagating the exception, ensuring the
    A2A task always completes cleanly.
    """
    with patch(
        "agent.SampleAgent._invoke_with_fallback",
        new=AsyncMock(side_effect=RuntimeError("LLM unavailable")),
    ):
        from agent import SampleAgent
        agent = SampleAgent()
        response = await agent.invoke(
            query="Show overdue invoices",
            context_id="test-context-003",
            tools=mock_tools,
        )

    # Agent catches the exception and returns a graceful error message
    assert response.message is not None
    assert len(response.message) > 0


def test_aging_summary_integration_with_dunning_data():
    """compute_aging_summary correctly buckets data that would come from the MCP tool."""
    from invoice_tools import compute_aging_summary

    items = [
        {
            "BusinessPartner": "BP-HIGH",
            "CADocumentNumber": "INV-001",
            "CADunningAmount": "75000.00",
            "CANetDueDate": (date.today() - timedelta(days=95)).isoformat(),
            "TransactionCurrency": "EUR",
        },
        {
            "BusinessPartner": "BP-MED",
            "CADocumentNumber": "INV-002",
            "CADunningAmount": "12000.00",
            "CANetDueDate": (date.today() - timedelta(days=35)).isoformat(),
            "TransactionCurrency": "EUR",
        },
    ]

    result = compute_aging_summary(items)
    assert result["buckets"]["over_90"]["count"] == 1
    assert result["buckets"]["over_90"]["total_amount"] == 75000.0
    assert result["buckets"]["31_60"]["count"] == 1
    assert result["buckets"]["31_60"]["total_amount"] == 12000.0


def test_risk_score_integration_with_credit_data():
    """compute_risk_score correctly ranks with combined dunning + credit signals."""
    from invoice_tools import compute_risk_score

    headers = [
        {
            "BusinessPartner": "BP-HIGH",
            "ContractAccount": "CA-HIGH",
            "CADunningBalance": "75000.00",
            "CADunningLevel": "3",
            "CANextDunningDate": "",
            "TransactionCurrency": "EUR",
            "CAMassRunDate": (date.today() - timedelta(days=95)).isoformat(),
        },
        {
            "BusinessPartner": "BP-MED",
            "ContractAccount": "CA-MED",
            "CADunningBalance": "12000.00",
            "CADunningLevel": "1",
            "CANextDunningDate": "",
            "TransactionCurrency": "EUR",
            "CAMassRunDate": (date.today() - timedelta(days=35)).isoformat(),
        },
    ]
    credit = {
        "BP-HIGH": {"CreditAccountIsBlocked": False, "CreditRiskClass": "C"},
        "BP-MED": {"CreditAccountIsBlocked": False, "CreditRiskClass": "A"},
    }

    ranked = compute_risk_score(headers, credit)
    assert ranked[0]["business_partner"] == "BP-HIGH"
    assert ranked[0]["risk_score"] > ranked[1]["risk_score"]
