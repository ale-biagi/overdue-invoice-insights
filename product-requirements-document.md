# Product Requirements Document (PRD)

**Title:** Overdue Invoice Insights AI Agent
**Date:** 2026-09-29
**Owner:** Finance / Accounts Receivable
**Solution Category:** AI Agent

---

## Product Purpose & Value Proposition

**Elevator Pitch:**
Finance teams are losing cash flow efficiency because overdue invoices are managed manually, reactively, and at low scale. This AI agent gives AR specialists and Finance managers an intelligent, conversational interface to instantly understand overdue invoice exposure, identify high-risk accounts, and take the right collection action — all from a single interface, powered by SAP S/4HANA data.

**Business Need:**
AR teams rely on static SAP reports and manual processes to track overdue invoices. There is no intelligent layer that interprets aging patterns, highlights which customers pose the greatest risk, or generates contextual collection actions and follow-up communication. This results in slow collections, high Days Sales Outstanding (DSO), and growing overdue volumes.

**Expected Value:**
- Reduce average DSO from 60 days to 40 days within 6 months
- Cut monthly overdue invoice volume from ~400 to ~280 (−30%)
- Free AR specialists from repetitive manual analysis
- Enable Finance managers to query invoice status in natural language without navigating complex SAP reports

**Product Objectives (Prioritized):**
1. Enable instant, natural-language access to overdue invoice data and aging analysis from SAP S/4HANA Cloud Public Edition
2. Provide AI-driven risk prioritization that surfaces the highest-risk accounts for immediate collection action
3. Generate contextual, personalized follow-up communications that AR specialists can review and send

---

## Business Metrics

| Metric | Baseline | Target | Timeline | Process / Capability | Source |
|--------|----------|--------|----------|----------------------|--------|
| Days Sales Outstanding (DSO) | 60 days | 40 days (−20 days) | 6 months | Invoice to Cash / Collections Management | user |
| Overdue Invoice Volume | ~400/month | ~280/month (−30%) | 6 months | Accounts Receivable & Collections | user |

---

## User Profiles & Personas

### Primary Persona: Alex — AR Specialist / Collections Agent

Alex is a 32-year-old Accounts Receivable specialist who manages collections for a portfolio of 150+ business customers. Every morning he opens multiple SAP transactions, exports overdue invoice lists to spreadsheets, and manually decides whom to call or email first. He spends roughly 2–3 hours per day on this repetitive triage work before he can start making actual collection calls. Alex is comfortable with SAP but frustrated by the lack of smart prioritization — some weeks he chases low-value invoices while a large at-risk account slips past due. He needs a tool that tells him instantly: "here are your top 10 accounts to contact today and why," and gives him a draft email he can review and send.

### Secondary Persona: Maria — Finance Manager / CFO

Maria is a 47-year-old Finance Director who oversees the company's receivables portfolio and cash flow performance. She reviews AR aging reports weekly in preparation for board meetings but finds the standard SAP reports difficult to interpret quickly. She wants to ask a simple question like "how much cash is overdue more than 60 days and which customers are the biggest risk?" and get a direct, actionable answer. Maria does not use SAP daily — she needs a conversational interface that surfaces the insight without requiring SAP navigation skills.

### Other User Types

- IT/BTP Administrator: Responsible for deploying, configuring, and monitoring the agent on SAP BTP.

---

## User Goals & Tasks

### For Alex (AR Specialist):

**Goals:**
- Know every morning which overdue accounts require immediate attention, ranked by risk and value
- Spend less time on manual triage and more time on high-value collection conversations
- Send personalized, professional follow-up emails to overdue customers with minimal effort

**Key Tasks:**
- Ask the agent "Show me all invoices overdue by more than 60 days"
- Ask for the top 5 highest-risk accounts and review the agent's recommended actions
- Request a draft follow-up email for a specific customer and lightly edit before sending

### For Maria (Finance Manager):

**Goals:**
- Get a clear, real-time view of total overdue exposure and trend at any time
- Identify strategic risks in the receivables portfolio without deep SAP expertise
- Confirm collections performance is on track toward DSO targets

**Key Tasks:**
- Ask "What is our current DSO and how has it changed over the last 30 days?"
- Ask "Which customers account for the most overdue exposure this month?"
- Ask for a summary of the aging distribution for a board report

---

## Product Principles

1. **Insights over raw data:** The agent interprets and prioritizes — it never just dumps a list. Every response answers "so what?" not just "what."
2. **Human-in-the-loop for all actions:** The agent recommends; humans decide. No emails are sent, no records modified without explicit AR review and approval.
3. **Trust through transparency:** When the agent recommends a collection action or drafts an email, it explains which data points drove the recommendation.
4. **S/4HANA as the single source of truth:** All data is retrieved in real time from SAP S/4HANA Cloud Public Edition. No parallel data stores or shadow copies.
5. **Graceful degradation:** When the agent cannot retrieve data or is uncertain, it communicates clearly and suggests a fallback rather than producing a wrong answer.

---

## Business Context

**Current State:**
AR specialists manually export overdue invoice lists from SAP S/4HANA, sort them in spreadsheets, and apply personal judgment to prioritize collection calls. Follow-up emails are written from scratch or from saved templates with minimal personalization. Finance managers rely on weekly aging reports that are often out of date by the time they are reviewed. The lack of intelligent prioritization means collection effort is not optimally directed.

**Strategic Alignment:**
This solution supports the company's cash flow optimization strategy and aligns with its investment in SAP S/4HANA Cloud Public Edition and SAP BTP as the extensibility platform. The agent demonstrates the value of AI-augmented finance operations.

**Success Criteria:**
See Business Metrics section above.

---

## Goals and Non-Goals

### Goals (In Scope)

- Retrieve overdue customer invoices from SAP S/4HANA Cloud Public Edition in real time via OData APIs
- Classify invoices into aging buckets (30 / 60 / 90+ days overdue) and surface key metrics
- Identify and rank high-risk accounts using overdue amount, aging, and dunning history
- Recommend next-best collection actions per account based on available data
- Generate personalized draft follow-up emails for overdue customers
- Support natural language queries for both AR specialists and Finance managers

### Non-Goals (Out of Scope)

- Automatically sending emails or initiating any outbound communication without human approval
- Writing back to SAP S/4HANA (e.g., creating dispute cases, updating dunning records, posting payments)
- Managing or configuring collections workflows or dunning levels in SAP
- Providing cash flow forecasting or financial planning beyond overdue invoice status
- Integrating with any system other than SAP S/4HANA Cloud Public Edition in this release

---

## Requirements

### Must-Have Requirements

**REQ-01: Overdue Invoice Retrieval**

- **Problem to Solve:** AR specialists have no fast way to get a current, structured list of overdue invoices without navigating SAP manually.
- **User Story:** As an AR specialist, I need the agent to retrieve all open and overdue customer invoices from SAP S/4HANA so that I can start my collections work immediately without manual data extraction.
- **Acceptance Criteria:**
  - Given the agent is connected to SAP S/4HANA Cloud Public Edition, when I ask for overdue invoices, then the agent returns a list including customer name, invoice number, amount, due date, and days overdue.
  - Given a large number of open items, when the agent retrieves data, then it handles pagination and returns results within 10 seconds for up to 500 records.
- **Maps to Objective:** Objective 1
- **Priority Rank:** 1

**REQ-02: Aging Analysis**

- **Problem to Solve:** Finance managers and AR specialists cannot quickly see how overdue amounts are distributed across aging brackets, making it hard to assess overall portfolio risk.
- **User Story:** As a Finance manager, I need the agent to classify overdue invoices into aging buckets (0–30 / 31–60 / 61–90 / 90+ days) so that I can assess exposure and communicate it clearly to stakeholders.
- **Acceptance Criteria:**
  - Given a set of overdue invoices, when I ask for an aging analysis, then the agent returns total amounts and invoice counts per aging bucket.
  - Given the aging results, when I ask "which bucket has the highest risk exposure?", then the agent highlights the bucket with the largest overdue amount and identifies the top customers within it.
- **Maps to Objective:** Objective 1
- **Priority Rank:** 2

**REQ-03: Risk Prioritization**

- **Problem to Solve:** With 150+ accounts, AR specialists cannot manually determine each morning which customers pose the greatest risk and require immediate contact.
- **User Story:** As an AR specialist, I need the agent to rank overdue accounts by risk so that I can focus my collection effort on the highest-priority accounts first.
- **Acceptance Criteria:**
  - Given overdue invoices and available dunning/credit data, when I ask for the top at-risk accounts, then the agent returns a ranked list with risk rationale per customer.
  - Given the ranked list, when I ask why a specific customer is flagged as high risk, then the agent explains the contributing factors (e.g., overdue amount, aging bracket, previous dunning history).
- **Maps to Objective:** Objective 2
- **Priority Rank:** 3

**REQ-04: Collection Action Recommendations**

- **Problem to Solve:** AR specialists apply inconsistent collection actions because there is no guidance on the best next step per customer based on the available data.
- **User Story:** As an AR specialist, I need the agent to suggest the most appropriate next collection action for each overdue account so that I take the right action without guesswork.
- **Acceptance Criteria:**
  - Given a specific overdue account, when I ask the agent for a recommended action, then it suggests a concrete next step (e.g., "Send a payment reminder", "Escalate to collections manager", "Check open dispute") with a brief rationale.
  - Given the recommendation, when I ask for alternatives, then the agent provides up to two other options with trade-offs explained.
- **Maps to Objective:** Objective 2
- **Priority Rank:** 4

**REQ-05: Personalized Follow-Up Email Drafting**

- **Problem to Solve:** AR specialists spend significant time writing individual follow-up emails for each overdue customer, often from scratch, with inconsistent tone and accuracy.
- **User Story:** As an AR specialist, I need the agent to draft a personalized follow-up email for a specific overdue customer so that I can review, adjust, and send it quickly without writing from scratch.
- **Acceptance Criteria:**
  - Given a customer name or invoice number, when I ask the agent to draft a follow-up email, then it generates a professional email including the customer name, overdue amount, due date, invoice number, and a clear call to action.
  - Given the draft, when I request changes (e.g., "make it more formal" or "add the dispute reference"), then the agent regenerates an updated version.
  - The agent never sends the email — it only produces a draft for human review.
- **Maps to Objective:** Objective 3
- **Priority Rank:** 5

**REQ-06: Natural Language Interface**

- **Problem to Solve:** Finance managers need actionable overdue invoice insights but do not have deep SAP navigation skills or time to learn them.
- **User Story:** As a Finance manager, I need to query overdue invoice status in plain language so that I can get answers without navigating SAP transactions or running reports.
- **Acceptance Criteria:**
  - Given a conversational question such as "How much is overdue more than 90 days?", when submitted to the agent, then a clear, direct answer is returned in natural language with supporting data.
  - Given a follow-up question in the same session, when submitted, then the agent maintains conversation context and does not require the user to repeat prior conditions.
- **Maps to Objective:** Objective 1
- **Priority Rank:** 6

---

## Non-Functional Requirements

### Performance

- **Latency:** Agent responses for standard queries (overdue list, aging summary, risk ranking) should complete within 10 seconds end-to-end.
- **Throughput:** Support at least 20 concurrent users querying the agent simultaneously.

### Reliability

- **Availability:** Target 99.5% uptime during business hours (Monday–Friday, 07:00–19:00 local time).
- **Fallback:** If the S/4HANA OData API is unavailable, the agent informs the user clearly and suggests retrying rather than returning stale or incorrect data.

### Cost

- **Budget Controls:** LLM calls should be minimized through response caching for repeated identical queries within the same business day.

### Explainability

- **Traceability:** Every risk ranking and collection recommendation must cite the data point(s) from S/4HANA that drove the output.
- **Decision Logging:** All agent actions, queries issued to S/4HANA, and LLM invocations are logged with timestamps for auditability.
- **Uncertainty Communication:** When the agent lacks sufficient data to make a confident recommendation, it explicitly signals this to the user and suggests a manual review.

---

## Solution Architecture

**Architecture Overview:**
A Python AI agent (A2A protocol) deployed on SAP BTP Cloud Foundry. The agent connects to SAP S/4HANA Cloud Public Edition via OData APIs using MCP tools generated from API translation files. An LLM (via SAP Generative AI Hub) handles natural language understanding, reasoning, and email generation. All data stays within SAP infrastructure.

**Key Components:**

- **AI Agent (Python, A2A):** Core reasoning and orchestration layer; handles user queries, tool selection, response generation, and email drafting via LLM.
- **SAP S/4HANA Cloud Public Edition:** Source of all invoice, AR open item, dunning, credit, and dispute data accessed read-only via OData APIs.
- **MCP Tools (generated from OData specs):** Structured tool interfaces the agent uses to query S/4HANA — covering dunning/invoice data, credit management, and dispute management.
- **SAP Generative AI Hub:** Provides the LLM backend for natural language reasoning, risk explanation, and email generation.
- **SAP BTP Cloud Foundry:** Deployment and runtime environment for the agent.

**Integration Points:**

- SAP S/4HANA Cloud Public Edition — Contract Accounting Dunning API (`CADUNNING_0001`): read-only, retrieves overdue invoice and dunning data.
- SAP S/4HANA Cloud Public Edition — Credit Management Master Data API (`API_CRDTMBUSINESSPARTNER`): read-only, retrieves customer credit risk information.
- SAP S/4HANA Cloud Public Edition — Dispute Management API (`CADISPUTECASE_0001`): read-only, checks for open dispute cases per customer.

**Deployment Environments:**

- **Development:** SAP BTP dev space; connects to S/4HANA sandbox/test tenant.
- **Production:** SAP BTP production space; connects to live S/4HANA Cloud Public Edition tenant with read-only service user credentials.

### Agent Extensibility & Instrumentation

**Agent Extensibility:**
The agent is designed with extension points to support future capabilities without requiring a full rewrite:
- New S/4HANA data sources can be added by registering additional MCP tools from OData API translation files.
- New reasoning skills (e.g., cash flow forecasting, write-back actions) can be added as isolated tool modules.
- Prompt templates for email drafting are externalized to allow business users to customize tone and content without code changes.

**Business Step Instrumentation:**
All five key business milestones are instrumented as named spans to support observability and debugging in production. Each milestone emits a structured log on achievement and on miss. See the Milestones section for the full log statement definitions.

### Automation & Agent Behaviour

**Automation Level:** Autonomous agent (LLM-driven reasoning with human approval gate for all actions)

**Actions the system performs without human approval:**
- Querying SAP S/4HANA OData APIs to retrieve invoice, dunning, credit, and dispute data
- Computing aging analysis and risk rankings based on retrieved data
- Generating draft collection recommendations and follow-up emails

**Actions that require human review or approval:**
- Sending any follow-up email or communication to a customer (agent produces draft only)
- Any write-back to SAP S/4HANA (out of scope for this release)

**Model or engine used:** LLM via SAP Generative AI Hub (e.g., GPT-4o or equivalent available model)

**Knowledge & data sources accessed:**
- SAP S/4HANA Cloud Public Edition — overdue invoices, dunning records, open items, credit master data, dispute cases (read-only)

**Tools or connectors invoked:**
- `get_overdue_invoices` (Dunning/Invoice OData — read-only): retrieves open overdue invoice list per customer
- `get_aging_summary` (Open Item OData — read-only): aggregates open items by aging bucket
- `get_credit_info` (Credit Management OData — read-only): retrieves customer credit risk indicators
- `get_dispute_cases` (Dispute Management OData — read-only): checks for open dispute cases linked to overdue invoices

**Guardrails & fail-safes:**
- The agent never modifies any SAP data — all tool calls are read-only.
- Email drafts are never sent automatically; they are returned as text for human review.
- If a tool call fails or returns no data, the agent informs the user and does not fabricate data.
- LLM outputs for financial recommendations are prefaced with a disclaimer that they are AI-generated suggestions for AR specialist review.
- Confidence threshold: if the agent cannot form a recommendation from available data, it says so explicitly.

---

## Governance, Risk & Compliance

**Data Handling:**
- All data is retrieved in real time from SAP S/4HANA Cloud Public Edition and is not persisted by the agent beyond the active session.
- No PII beyond customer name and invoice data (which is standard business data) is processed.
- Data residency: agent runs on SAP BTP in the same region as the S/4HANA tenant.

**Compliance Frameworks:**
- All access to S/4HANA follows existing role-based access controls; the agent uses a dedicated read-only service user.
- Email drafts are for internal AR specialist review only before any external communication.

**Approval Flows:**
- All collection actions recommended by the agent require human approval by an AR specialist before execution.

---

## Release Criteria

- **Performance:** Agent responds to standard queries within 10 seconds for datasets up to 500 invoices.
- **Reliability:** All five milestone steps complete successfully in end-to-end testing with no data fabrication on API failure.
- **Security:** Agent uses read-only S/4HANA credentials; no write permissions granted.
- **Usability:** At least 2 AR specialists complete a guided test session and confirm the agent provides accurate, useful output.
- **Documentation:** Agent README, deployment guide, and tool configuration instructions are complete.
- **Monitoring:** All five milestones emit structured logs; a basic observability dashboard is operational on SAP BTP.

---

## Schedule & Timeline Context

**Target Timeline:** 6 months from project kick-off to production go-live.

**Business Drivers:**
- DSO reduction target of 20 days within 6 months drives the timeline.
- Monthly overdue invoice volume reduction of 30% is a board-level commitment.

---

## Milestones

### M1: Data Connection

- **Description:** The agent connects to SAP S/4HANA Cloud Public Edition and successfully retrieves overdue customer invoices via the Dunning OData API.
- **Achieved when:** The agent returns a non-empty list of overdue invoices for at least one customer in response to a user query.
- **Log on achievement:** `M1.achieved: overdue invoice data retrieved from S/4HANA successfully`
- **Log on miss:** `M1.missed: failed to retrieve overdue invoice data from S/4HANA — check API connectivity and credentials`

### M2: Aging Analysis

- **Description:** The agent classifies retrieved overdue invoices into aging buckets (0–30 / 31–60 / 61–90 / 90+ days) and returns a summary with totals per bucket.
- **Achieved when:** The agent produces a complete aging breakdown with amounts and invoice counts per bucket.
- **Log on achievement:** `M2.achieved: aging analysis completed — invoices classified into aging buckets`
- **Log on miss:** `M2.missed: aging analysis did not complete — invoice data may be empty or malformed`

### M3: Risk Prioritization

- **Description:** The agent identifies high-risk overdue accounts using overdue amount, aging bracket, and available dunning/credit data, and returns a ranked list.
- **Achieved when:** The agent returns a ranked list of at least 3 accounts with a brief risk rationale per account.
- **Log on achievement:** `M3.achieved: risk prioritization completed — high-risk accounts ranked and returned`
- **Log on miss:** `M3.missed: risk prioritization did not complete — insufficient data to rank accounts`

### M4: Collection Recommendations

- **Description:** The agent generates a next-best collection action recommendation for a specific overdue account.
- **Achieved when:** The agent returns at least one concrete recommended action with a rationale citing S/4HANA data.
- **Log on achievement:** `M4.achieved: collection recommendation generated for account`
- **Log on miss:** `M4.missed: could not generate collection recommendation — insufficient account data available`

### M5: Email Drafting

- **Description:** The agent generates a personalized draft follow-up email for a specific overdue customer.
- **Achieved when:** The agent returns a complete draft email containing the customer name, invoice number, overdue amount, due date, and a clear call to action.
- **Log on achievement:** `M5.achieved: personalized follow-up email draft generated for customer`
- **Log on miss:** `M5.missed: email draft generation failed — customer or invoice data not found`

---

## Risks, Assumptions, and Dependencies

### Risks

- **API performance at scale:** OData queries over large open item sets may be slow; pagination and query filters must be implemented from the start.
- **LLM accuracy for financial recommendations:** Collection suggestions are LLM-generated and may be incorrect for edge cases; all outputs must be positioned as recommendations, not instructions.
- **S/4HANA API access provisioning:** Obtaining a read-only service user with the correct authorization objects may require IT involvement and could delay development.

### Assumptions

- SAP S/4HANA Cloud Public Edition is the live system of record for all invoice and AR data.
- A read-only service user for the required OData APIs can be provisioned on S/4HANA Cloud Public Edition.
- SAP Generative AI Hub is available and configured on the target SAP BTP tenant.
- MCP translation files will be generated from the available OData specs (CADUNNING_0001, API_CRDTMBUSINESSPARTNER, CADISPUTECASE_0001).

### Dependencies

- SAP S/4HANA Cloud Public Edition — OData API access (Dunning, Credit Management, Dispute Management)
- SAP BTP Cloud Foundry environment with Python runtime support
- SAP Generative AI Hub with an available and configured LLM model
- IT/Security sign-off on service user credentials and authorization scope

---

## Open Questions

- Which LLM model is preferred (subject to SAP Generative AI Hub availability) — GPT-4o, Claude, or another model?
- Are there specific email templates or tone guidelines the company currently uses for collections communication that should be reflected in the agent's email drafts?
- Should the agent support multiple languages for email drafting (e.g., local language for customers in non-English markets)?

---

## Appendix

### Glossary

- **DSO (Days Sales Outstanding):** Average number of days it takes to collect payment after a sale. Lower is better.
- **Aging bucket:** A time-based grouping of overdue invoices (e.g., 0–30 days, 31–60 days, etc.).
- **Dunning:** The SAP process of sending progressively escalating payment reminders to overdue customers.
- **A2A (Agent-to-Agent) protocol:** The communication protocol used by SAP BTP AI agents to expose and consume agent capabilities.
- **MCP (Model Context Protocol):** A protocol that wraps API capabilities as structured tools callable by an AI agent.
- **OData:** Open Data Protocol — a standard REST-based API format used extensively by SAP to expose S/4HANA data.

### References

- SAP S/4HANA Cloud Public Edition — Collections Management (SC100)
- SAP S/4HANA Cloud Public Edition — Dispute Management (SC89)
- SAP S/4HANA Cloud Public Edition — Credit Management (SC3083)
- SAP BTP AI Agent development guidelines
- SAP Generative AI Hub documentation
