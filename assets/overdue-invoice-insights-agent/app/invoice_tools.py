"""
Business logic tools for the Overdue Invoice Insights Agent.

Provides:
- compute_aging_summary: Classifies dunning items into aging buckets
- compute_risk_score: Ranks accounts by combined overdue risk
- Milestone instrumentation (M1–M5) with structured logging and OpenTelemetry spans
"""

import logging
from datetime import date, datetime
from typing import Any

from opentelemetry import trace

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


# ---------------------------------------------------------------------------
# Aging analysis
# ---------------------------------------------------------------------------

def _days_overdue(net_due_date: str | None) -> int:
    """Return the number of days an item is overdue (positive = overdue)."""
    if not net_due_date:
        return 0
    try:
        due = date.fromisoformat(str(net_due_date)[:10])
        return (date.today() - due).days
    except (ValueError, TypeError):
        return 0


def compute_aging_summary(dunning_items: list[dict[str, Any]]) -> dict[str, Any]:
    """Classify a list of dunning items into aging buckets and return summary.

    Args:
        dunning_items: List of CADunningItem records from the MCP tool.

    Returns:
        Dict with buckets 0_30, 31_60, 61_90, over_90, each containing
        count, total_amount, currency, and top_5_customers.
    """
    with tracer.start_as_current_span("M2_aging_analysis"):
        buckets: dict[str, dict] = {
            "0_30":   {"count": 0, "total_amount": 0.0, "currency": "", "customers": {}},
            "31_60":  {"count": 0, "total_amount": 0.0, "currency": "", "customers": {}},
            "61_90":  {"count": 0, "total_amount": 0.0, "currency": "", "customers": {}},
            "over_90": {"count": 0, "total_amount": 0.0, "currency": "", "customers": {}},
        }

        if not dunning_items:
            logger.warning("[M2.missed]: aging analysis did not complete — invoice data may be empty or malformed")
            return {"buckets": buckets, "total_items": 0}

        for item in dunning_items:
            days = _days_overdue(item.get("CANetDueDate"))
            amount = float(item.get("CADunningAmount", 0) or 0)
            currency = item.get("TransactionCurrency", "")
            partner = item.get("BusinessPartner", "Unknown")

            if days <= 0:
                continue  # not overdue

            if days <= 30:
                key = "0_30"
            elif days <= 60:
                key = "31_60"
            elif days <= 90:
                key = "61_90"
            else:
                key = "over_90"

            bucket = buckets[key]
            bucket["count"] += 1
            bucket["total_amount"] += amount
            if not bucket["currency"]:
                bucket["currency"] = currency
            bucket["customers"][partner] = bucket["customers"].get(partner, 0.0) + amount

        # Build top-5 per bucket
        result: dict[str, Any] = {"buckets": {}, "total_items": len(dunning_items)}
        for key, bucket in buckets.items():
            sorted_customers = sorted(bucket["customers"].items(), key=lambda x: x[1], reverse=True)
            result["buckets"][key] = {
                "count": bucket["count"],
                "total_amount": round(bucket["total_amount"], 2),
                "currency": bucket["currency"],
                "top_5_customers": [
                    {"business_partner": bp, "amount": round(amt, 2)}
                    for bp, amt in sorted_customers[:5]
                ],
            }

        logger.info("[M2.achieved]: aging analysis completed — invoices classified into aging buckets")
        return result


# ---------------------------------------------------------------------------
# Risk scoring
# ---------------------------------------------------------------------------

def _aging_score(days: int) -> float:
    """Return a 0–1 score based on days overdue (30-day steps)."""
    if days <= 30:
        return 0.25
    if days <= 60:
        return 0.50
    if days <= 90:
        return 0.75
    return 1.0


def _dunning_level_score(level: str) -> float:
    """Convert a dunning level string to a 0–1 score."""
    try:
        lvl = int(level)
        return min(lvl / 5.0, 1.0)
    except (ValueError, TypeError):
        return 0.0


def compute_risk_score(
    dunning_headers: list[dict[str, Any]],
    credit_info_by_partner: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Rank accounts by a composite risk score.

    Weights:
      - Overdue amount:  50%
      - Aging bucket:    30%
      - Dunning level:   20%
    Credit info (risk class, blocked) adds +0.1 bonus when negative signals present.

    Args:
        dunning_headers: List of CADunning records.
        credit_info_by_partner: Optional dict keyed by BusinessPartner with credit data.

    Returns:
        List of ranked account dicts, highest risk first.
    """
    with tracer.start_as_current_span("M3_risk_prioritization"):
        if not dunning_headers:
            logger.warning("[M3.missed]: risk prioritization did not complete — insufficient data to rank accounts")
            return []

        # Normalize amounts for scoring
        amounts = [float(h.get("CADunningBalance", 0) or 0) for h in dunning_headers]
        max_amount = max(amounts) if amounts else 1.0

        scored: list[dict[str, Any]] = []
        for header in dunning_headers:
            partner = header.get("BusinessPartner", "Unknown")
            balance = float(header.get("CADunningBalance", 0) or 0)
            level = header.get("CADunningLevel", "0")
            next_date = header.get("CANextDunningDate", "")

            # Days overdue approximation from next dunning date (proxy)
            days = _days_overdue(header.get("CAMassRunDate"))

            amount_score = (balance / max_amount) if max_amount > 0 else 0.0
            aging_sc = _aging_score(days)
            dun_sc = _dunning_level_score(level)

            score = 0.50 * amount_score + 0.30 * aging_sc + 0.20 * dun_sc

            # Credit signals bonus
            rationale_parts = [
                f"Overdue balance: {balance:.2f}",
                f"Dunning level: {level}",
            ]
            if credit_info_by_partner:
                credit = credit_info_by_partner.get(partner, {})
                risk_class = credit.get("CreditRiskClass", "")
                blocked = credit.get("CreditAccountIsBlocked", False)
                if blocked:
                    score += 0.10
                    rationale_parts.append("Credit account is BLOCKED")
                if risk_class in ("HIGH", "C", "3"):
                    score += 0.05
                    rationale_parts.append(f"High credit risk class: {risk_class}")

            scored.append({
                "business_partner": partner,
                "contract_account": header.get("ContractAccount", ""),
                "dunning_balance": balance,
                "dunning_level": level,
                "currency": header.get("TransactionCurrency", ""),
                "next_dunning_date": next_date,
                "risk_score": round(min(score, 1.0), 4),
                "rationale": "; ".join(rationale_parts),
            })

        ranked = sorted(scored, key=lambda x: x["risk_score"], reverse=True)
        logger.info("[M3.achieved]: risk prioritization completed — high-risk accounts ranked and returned")
        return ranked


# ---------------------------------------------------------------------------
# Milestone log helpers (called from agent_executor wrappers)
# ---------------------------------------------------------------------------

def log_m1_achieved() -> None:
    logger.info("[M1.achieved]: overdue invoice data retrieved from S/4HANA successfully")


def log_m1_missed(reason: str = "") -> None:
    logger.warning("[M1.missed]: failed to retrieve overdue invoice data from S/4HANA — %s", reason or "check API connectivity and credentials")


def log_m4_achieved(partner: str = "") -> None:
    logger.info("[M4.achieved]: collection recommendation generated for account %s", partner)


def log_m4_missed(reason: str = "") -> None:
    logger.warning("[M4.missed]: could not generate collection recommendation — %s", reason or "insufficient account data available")


def log_m5_achieved(partner: str = "") -> None:
    logger.info("[M5.achieved]: personalized follow-up email draft generated for customer %s", partner)


def log_m5_missed(reason: str = "") -> None:
    logger.warning("[M5.missed]: email draft generation failed — %s", reason or "customer or invoice data not found")
