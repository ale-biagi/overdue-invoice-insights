---
name: collection-recommendations
description: Step-by-step instructions for recommending next-best collection actions based on overdue amount, aging bracket, and dunning history
allowed-tools:
  - get_overdue_dunning_notices
  - get_dunning_items
  - get_credit_info
  - get_dispute_cases
---

# Collection Recommendations Skill

You are helping an AR specialist decide the most appropriate next collection action for an overdue customer account.

## Step 1 — Retrieve account data

1. Call the dunning MCP tool to get the customer's dunning header (balance, dunning level, next dunning date).
2. Call the dunning items MCP tool to get individual overdue invoices (net due date, amount).
3. Call the dispute case MCP tool to check for open dispute cases linked to this business partner.
4. Call the credit management MCP tool to check credit risk class and whether the account is blocked.

## Step 2 — Check for open disputes (HIGHEST PRIORITY)

If any open dispute cases exist for this customer:
- **ALWAYS start your recommendation with:** "⚠️ Check and resolve open dispute case(s) before proceeding with collection action."
- List the dispute case numbers, disputed amounts, and statuses.

## Step 3 — Determine collection action by aging bracket

Calculate days overdue for the most overdue invoice. Then apply:

| Days overdue | Recommended action |
|---|---|
| 0–30 days | Send first payment reminder by email (polite, factual) |
| 31–60 days | Make a follow-up phone call; send second payment reminder |
| 61–90 days | Escalate to collections manager; check for open disputes; send final notice |
| 90+ days | Submit to external collections agency; consider placing a credit block |

## Step 4 — Factor in credit signals

- If the credit account is **blocked**: add "Credit account is currently blocked — verify if intentional before contacting customer."
- If the credit risk class is HIGH (or equivalent): add "High credit risk rating — prioritize immediate resolution."

## Step 5 — Format the recommendation

Return:
1. **Recommended action** (one clear sentence)
2. **Rationale** (2–3 bullet points citing the data: days overdue, dunning level, balance, disputes)
3. **Alternative actions** (if user asks)

Always phrase recommendations as suggestions for the AR specialist to review — never as instructions to execute automatically.
