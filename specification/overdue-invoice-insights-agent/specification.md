# Specification: overdue-invoice-insights-agent

> **Guidelines**: Read all applicable guidelines before executing ANY tasks below:
> - [guidelines.md](../guidelines.md) — Universal execution rules
> - [guidelines-agent.md](../guidelines-agent.md) — Universal agent patterns
> - [guidelines-agent-python.md](../guidelines-agent-python.md) — Python implementation details
> - [guidelines-agent-skills.md](../guidelines-agent-skills.md) — Runtime skills patterns
> - [guidelines-agent-mcp.md](../guidelines-agent-mcp.md) — MCP integration patterns

---

## Basic Setup

- [x] Read the project input (`product-requirements-document.md` and `intent.md`)
- [x] Bootstrap agent code in `assets/overdue-invoice-insights-agent/` using instructions from the sap-agent-bootstrap section (invoke from inside `assets/overdue-invoice-insights-agent/`, use copy commands — do NOT create files manually)
- [x] Install dependencies, validate the agent starts and responds at `/.well-known/agent.json`

---

## Runtime Skills

> **Before proceeding**, read [guidelines-agent-skills.md](../guidelines-agent-skills.md) and decide whether the agent needs runtime skills.

The agent requires runtime skills for the following domains:

- [x] Create `assets/overdue-invoice-insights-agent/app/skills/collection-recommendations/SKILL.md` with:
  - YAML frontmatter: `name: collection-recommendations`, `description: Step-by-step instructions for recommending next-best collection actions based on overdue amount, aging bracket, and dunning history`
  - Body: Decision tree for recommending payment reminder, escalation, or dispute check based on aging bucket and dunning level
  - `allowed-tools`: MCP tools for dunning and credit data

- [x] Create `assets/overdue-invoice-insights-agent/app/skills/email-drafting/SKILL.md` with:
  - YAML frontmatter: `name: email-drafting`, `description: Instructions and templates for drafting personalized follow-up emails for overdue customers`
  - Body: Email structure guidelines (subject, greeting, overdue summary, call-to-action, sign-off), tone instructions (professional, firm but courteous), required fields (customer name, invoice number, overdue amount, due date)
  - Companion template file `templates/collection-email-template.md` with a base email template

---

## Project-Specific Tasks

## REQ-01: Overdue Invoice Retrieval

- [x] Implement tool `get_overdue_dunning_notices` in the agent that calls the MCP tool generated from `specification/overdue-invoice-insights-agent/api-specs/cadunning.edmx` (ORD ID: `sap.s4:apiResource:CADUNNING_0001:v1`) to retrieve the `CADunning` entity set — returns business partner, contract account, dunning balance, dunning level, next dunning date, collection strategy per record
- [x] Implement tool `get_dunning_items` that retrieves `CADunningItem` records for a given business partner — returns document number, net due date, dunning amount, dunning level per item
- [x] Add pagination logic: implement `$top` / `$skip` query options to handle up to 500 records per request without timeout
- [x] Agent system prompt must include: "Always retrieve live overdue invoice data from S/4HANA before answering any question about overdue invoices. Never fabricate invoice data."

## REQ-02: Aging Analysis

- [x] Implement `compute_aging_summary` function in the agent that takes the list of dunning items and classifies them into aging buckets: 0–30 days, 31–60 days, 61–90 days, 90+ days, based on `CANetDueDate` compared to today's date
- [x] The function must return: total count, total overdue amount, and list of top 5 customers by overdue amount for each aging bucket
- [x] Agent must be able to answer "What is our aging distribution?" by calling `get_dunning_items` then `compute_aging_summary` and rendering the result in a structured natural language response

## REQ-03: Risk Prioritization

- [x] Implement tool `get_credit_info` that calls the MCP tool generated from `specification/overdue-invoice-insights-agent/api-specs/credit-management.edmx` (ORD ID: `sap.s4:apiResource:API_CRDTMBUSINESSPARTNER:v1`) — queries `CreditMgmtBusinessPartner` and `CreditManagementAccount` for a given business partner — returns credit risk class, credit worthiness score, credit limit, and whether the account is blocked
- [x] Implement `compute_risk_score` function that combines: overdue amount (weight: 50%), aging bucket (weight: 30%), and dunning level (weight: 20%) to produce a ranked list of high-risk accounts
- [x] When credit info is available, factor in `CreditRiskClass` and `CreditAccountIsBlocked` as additional risk signals
- [x] Agent must respond to "Which accounts are highest risk?" by retrieving dunning data + credit info, computing the risk score, and returning the top N accounts with a brief explanation of the risk rationale per account

## REQ-04: Collection Action Recommendations

- [x] Load the `collection-recommendations` runtime skill via the `load(path)` tool when the user asks for collection recommendations
- [x] Implement the collection recommendation logic in the skill:
  - 0–30 days overdue: recommend "Send first payment reminder by email"
  - 31–60 days overdue: recommend "Make a follow-up phone call; send second reminder"
  - 61–90 days overdue: recommend "Escalate to collections manager; check for open disputes"
  - 90+ days overdue: recommend "Submit to external collections agency; consider credit block"
  - If an open dispute case exists for the customer: always prepend "Check and resolve open dispute case before proceeding"
- [x] Agent must respond to "What should I do about [customer]?" by retrieving dunning items, checking for open dispute cases via the dispute tool, applying the skill logic, and returning a specific recommended action with rationale

## REQ-05: Dispute Case Lookup

- [x] Implement tool `get_dispute_cases` that calls the MCP tool generated from `specification/overdue-invoice-insights-agent/api-specs/dispute-case.edmx` (ORD ID: `sap.s4:apiResource:CADISPUTECASE_0001:v1`) — queries `DisputeCase` filtered by `BusinessPartner` — returns case UUID, case title, disputed amount, remaining disputed amount, case status, case creation date, and root cause description
- [x] This tool is called automatically as part of REQ-03 (risk prioritization) and REQ-04 (collection recommendations) to enrich the agent's context before reasoning

## REQ-06: Personalized Follow-Up Email Drafting

- [x] Load the `email-drafting` runtime skill via the `load(path)` tool when the user requests an email draft
- [x] Implement the email drafting flow:
  1. Call `get_dunning_items` to retrieve the specific invoice(s) for the customer
  2. Call `get_dispute_cases` to check for any open disputes
  3. Load the `email-drafting` skill to get the template and tone guidelines
  4. Use the LLM to render a draft email populated with: customer name (from `BusinessPartnerFullName`), invoice number(s) (`CADocumentNumber`), overdue amount(s) (`CADunningAmount`), net due date(s) (`CANetDueDate`), and a call to action matching the dunning level
- [x] Agent must never send the email — always return the draft as text in the response with a note: "Please review before sending."
- [x] Agent must support follow-up requests like "make it more formal" or "add the dispute reference" by regenerating the email with the updated instructions in the same conversation context

## REQ-06-b: Natural Language Interface

- [x] Agent system prompt must include clear instructions to handle both operational queries (AR specialist: specific customer/invoice queries) and strategic queries (Finance manager: portfolio-level questions like total overdue exposure, DSO estimates)
- [x] Agent must maintain conversation context across turns within a session — e.g., after returning an aging summary, a follow-up question "who is the riskiest?" should not require the user to repeat the context
- [x] Agent must never return raw API response objects — always render data in human-readable natural language with relevant numbers highlighted

---

## Business Instrumentation

- [x] Implement business step instrumentation for all 5 milestones from the PRD using structured logging with pattern `[MILESTONE_ID].[achieved|missed]: [description]` and OpenTelemetry custom spans:
  - **M1** — `[M1.achieved]: overdue invoice data retrieved from S/4HANA successfully` / `[M1.missed]: failed to retrieve overdue invoice data from S/4HANA — check API connectivity and credentials`
  - **M2** — `[M2.achieved]: aging analysis completed — invoices classified into aging buckets` / `[M2.missed]: aging analysis did not complete — invoice data may be empty or malformed`
  - **M3** — `[M3.achieved]: risk prioritization completed — high-risk accounts ranked and returned` / `[M3.missed]: risk prioritization did not complete — insufficient data to rank accounts`
  - **M4** — `[M4.achieved]: collection recommendation generated for account` / `[M4.missed]: could not generate collection recommendation — insufficient account data available`
  - **M5** — `[M5.achieved]: personalized follow-up email draft generated for customer` / `[M5.missed]: email draft generation failed — customer or invoice data not found`
- [x] Extract business logic from `stream()` into plain async helpers to avoid `GeneratorExit` context errors (see [guidelines-agent-python.md](../guidelines-agent-python.md))
- [x] Verify `bootstrap(app)` is called after `app = server.build()` in `main.py`

---

## MCP Tool Integration

> Read [guidelines-agent-mcp.md](../guidelines-agent-mcp.md) for complete MCP integration patterns.

- [x] Verify `specification/overdue-invoice-insights-agent/api-specs/` contains three EDMX files:
  - `cadunning.edmx` — ORD ID: `sap.s4:apiResource:CADUNNING_0001:v1`
  - `credit-management.edmx` — ORD ID: `sap.s4:apiResource:API_CRDTMBUSINESSPARTNER:v1`
  - `dispute-case.edmx` — ORD ID: `sap.s4:apiResource:CADISPUTECASE_0001:v1`
- [x] Invoke `mcp-translation-file` skill for each EDMX file to generate MCP translation files — if the skill is not available in this environment, skip this step and proceed
- [x] Invoke `setup-solution` skill to create `solution.yaml` and register MCP assets for all three translation files — skip if `mcp-translation-file` was skipped
- [x] Wire MCP tool loading in `agent.py` using `get_mcp_tools()` from the `mcp_tools` module — NEVER import directly from `sap_cloud_sdk.agentgateway`; NEVER create direct HTTP clients for SAP APIs
- [x] Add MCP server dependencies to `asset.yaml` under `requires` — one entry per generated MCP server using exact ORD IDs from the generated assets
- [x] Generate `mcp-mock.json` using the `mcp-mock-config` skill after MCP translation files are generated (required before tests can run); skip if translation files were not generated and no `mcp-specs/` exist

---

## Testing

> See [guidelines-agent-python.md](../guidelines-agent-python.md) for Python testing setup and patterns.

- [x] `conftest.py` only sets `IBD_TESTING=true` — this causes the agent to run with mock MCP tool results during tests
- [x] Write unit tests in `assets/overdue-invoice-insights-agent/tests/` — exactly one test per tool:
  - `test_get_overdue_dunning_notices.py` — mocks MCP call, asserts correct fields returned
  - `test_get_dunning_items.py` — mocks MCP call, asserts pagination is handled
  - `test_compute_aging_summary.py` — unit test for the aging bucket classification logic with edge cases (invoices exactly at 30/60/90 day boundaries)
  - `test_get_credit_info.py` — mocks MCP call, asserts credit risk fields returned
  - `test_get_dispute_cases.py` — mocks MCP call, asserts dispute case fields returned
  - `test_compute_risk_score.py` — unit test for risk scoring logic, asserts correct ranking
- [x] Write one integration test `test_end_to_end.py` that simulates a full agent flow: user asks for top at-risk accounts → agent retrieves dunning data + credit info + dispute cases → returns ranked list with rationale (mocked LLM + mocked MCP)
- [x] Run `pytest` from `assets/overdue-invoice-insights-agent/` (no args, no extra flags) — if coverage < 70%, add tests until threshold is met
- [x] Run `pytest` again to generate final `test_report.json`
- [x] Verify `test_report.json` exists in `assets/overdue-invoice-insights-agent/` — if not, run pytest again until it does
