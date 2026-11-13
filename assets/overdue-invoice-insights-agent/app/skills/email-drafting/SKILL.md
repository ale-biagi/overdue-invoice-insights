---
name: email-drafting
description: Instructions and templates for drafting personalized follow-up emails for overdue customers
allowed-tools:
  - get_dunning_items
  - get_dispute_cases
---

# Email Drafting Skill

You are helping an AR specialist draft a professional, personalized follow-up email for a customer with overdue invoices.

## Required data before drafting

Before writing the email, ensure you have:
- Customer name (BusinessPartnerFullName)
- Invoice number(s) (CADocumentNumber)
- Overdue amount(s) (CADunningAmount)
- Net due date(s) (CANetDueDate)
- Dunning level (to set tone)
- Any open dispute cases

## Tone guidelines by dunning level

| Dunning level | Tone |
|---|---|
| 1 (first notice) | Friendly, assumes oversight — "We wanted to bring this to your attention" |
| 2 | Firm but professional — "We kindly request your prompt attention" |
| 3+ | Urgent — "This matter requires your immediate attention" |

## Email structure

Use the template below. Fill in all `[PLACEHOLDERS]`. Do not include placeholders in the final email.

---

**Subject:** Payment Reminder – Invoice [INVOICE_NUMBER] – [OVERDUE_AMOUNT] [CURRENCY] Overdue

Dear [CUSTOMER_NAME],

I hope this message finds you well. I am writing to bring to your attention that the following invoice(s) remain outstanding on your account:

| Invoice Number | Due Date | Overdue Amount | Currency |
|---|---|---|---|
| [INVOICE_NUMBER] | [DUE_DATE] | [OVERDUE_AMOUNT] | [CURRENCY] |

[If multiple invoices, add rows to the table above.]

[DUNNING_LEVEL_SPECIFIC_MESSAGE]

To resolve this matter, please arrange payment at your earliest convenience. If you have already processed this payment, please disregard this notice and accept our apologies for any inconvenience.

[If dispute cases exist: "We note that a dispute case [CASE_NUMBER] is currently open for your account. Please ensure this is resolved in parallel with any outstanding payments."]

If you have any questions or concerns, please do not hesitate to contact us.

Kind regards,
[SENDER_NAME]
Accounts Receivable Team

---

## IMPORTANT

- This email is a **draft for AR specialist review only**.
- Always end your response with: "**Please review before sending.**"
- Never send the email automatically.
- If the user asks to adjust the tone, regenerate the email with the new instructions.

## Companion template file

See `templates/collection-email-template.md` for an example of a completed email.
