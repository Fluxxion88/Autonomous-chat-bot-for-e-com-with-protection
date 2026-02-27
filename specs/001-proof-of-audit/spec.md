# Feature Specification: Proof of Audit

**Feature Branch**: `001-proof-of-audit`  
**Created**: February 27, 2026  
**Status**: Draft  
**Input**: User description: "Product Requirements Document (PRD): Autonomous AI Agent 'Proof of Audit'..."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Configure Global Limit (Priority: P1)

As an Operator, I want to set a global limit for approved discounts so that I can control the maximum discount an AI agent can issue without manual review.

**Why this priority**: It is the foundation for the "within permission limit" vs "over limit" logic.

**Independent Test**: Can be fully tested by setting the value in the "Limit Settings" on the dashboard and saving it.

**Acceptance Scenarios**:

1. **Given** the dashboard is loaded, **When** the operator inputs "20" into Limit Settings and saves, **Then** the global limit is updated to 20 for all subsequent claims.

---

### User Story 2 - Request and Receive Discount (Priority: P1)

As a Customer, I want to ask for a discount in the chat so that the AI agent can process my request and generate a promo code.

**Why this priority**: Core interaction for the user and triggers the double-logging logic.

**Independent Test**: Can be tested by sending a chat message and verifying that the agent responds with a JSON-based message and discount string, and that entries appear in both DB1 and DB2.

**Acceptance Scenarios**:

1. **Given** the chat interface is active, **When** the customer sends "Мне нужна скидка 15%", **Then** the agent replies with a message and a discount code, and the background system logs the transaction into DB1 (plaintext) and DB2 (SHA-256 hash) in one transaction.

---

### User Story 3 - Validate Legitimate Claim (Priority: P1)

As an Operator, I want to file a claim for a recorded discount to ensure its authenticity against the audit log.

**Why this priority**: Essential to demonstrate the "Proof of Audit" mechanism for valid transactions.

**Independent Test**: Can be tested by selecting an unmodified transaction from the dashboard and clicking "File Claim".

**Acceptance Scenarios**:

1. **Given** a transaction in DB1 where the discount (e.g., 10%) is <= Global Limit (20%), **When** the operator files a claim, **Then** the system outputs "Denied, within permission limit".
2. **Given** a transaction in DB1 where the discount (e.g., 100%) is > Global Limit (20%) and DB1's hash matches DB2, **When** the operator files a claim, **Then** the system outputs "Approved, Coverage wired".

---

### User Story 4 - Detect Tampered Claim (Priority: P1)

As an Operator, I want the system to block tampered records when I file a claim so that fraudulent changes are detected.

**Why this priority**: Demonstrates the core value proposition: detecting tampering or hallucinations.

**Independent Test**: Can be tested by manually editing a DB1 record and then filing a claim.

**Acceptance Scenarios**:

1. **Given** a transaction in DB1 where the discount was manually altered to 2000% (> Global Limit) and its new hash does not match DB2, **When** the operator files a claim, **Then** the system outputs "Denied, hash mismatch".

---

### Edge Cases

- What happens when the AI Engine API times out or hits rate limits? The system returns a local fallback response with a default discount of "0" and a placeholder message to prevent the demo from hanging.
- What happens when the AI Engine returns non-numeric inputs (e.g., "двадцать")? The system checks if the value is strictly numeric before database insertion; if it fails, the transaction is rejected, an error is logged, and the UI displays "Произошла системная ошибка генерации купона".
- What happens when the database connection drops? The UI dashboard shows the last cached state, and the "File Claim" button is temporarily disabled with a "Reconnecting to Audit Server..." notification.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a single unified interface with an Operator dashboard and a Customer chat zone.
- **FR-002**: System MUST allow the Operator to set and save a global discount limit that applies immediately to all transactions.
- **FR-003**: System MUST extract structured data from the AI Engine returning a chat message and a string-formatted numeric discount value.
- **FR-004**: System MUST log each generated discount into DB1 (plain text: id, timestamp, discount_val) and DB2 (SHA-256 hash of UTF-8 discount_val: id, timestamp, discount_hash) synchronously in a single transaction.
- **FR-005**: System MUST rollback the DB1 insertion if the DB2 insertion fails.
- **FR-006**: System MUST evaluate claims based on the global limit: if DB1 discount <= Limit, return "Denied, within permission limit" without checking hashes.
- **FR-007**: System MUST verify the DB1 discount hash against DB2 for claims where DB1 discount > Limit. If they match, return "Approved, Coverage wired"; if they mismatch, return "Denied, hash mismatch".
- **FR-008**: System MUST NOT allow updates or deletions on DB2 via UI or API (Append-only).
- **FR-009**: System MUST use a 10-second timeout for the AI Engine API and fallback to a default response of "0" on failure.
- **FR-010**: System MUST validate that the discount value is strictly numeric before database insertion.
- **FR-011**: System MUST display the DB2 audit log on a separate tab to show immutable hashes.
- **FR-012**: System MUST simulate tampering by allowing the Operator to manually edit the discount value in DB1 through the UI.

### Key Entities

- **DB1_Actions**: Represents the operational log of agent actions. Attributes: `id` (UUID/String), `timestamp` (UTC ISO 8601), `discount_val` (String).
- **DB2_AuditLog**: Represents the immutable audit trail. Attributes: `id` (UUID/String), `timestamp` (UTC ISO 8601), `discount_hash` (String, SHA-256).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete the full demo script cycle in under 3 minutes.
- **SC-002**: System achieves 100% accuracy in triggering the correct claim statuses ("Denied, within permission limit", "Approved, Coverage wired", "Denied, hash mismatch") based on input data.
- **SC-003**: 100% of AI Engine JSON responses are parsed successfully without errors under normal operating conditions.
- **SC-004**: 100% of tampered records are correctly identified and blocked by the hash mismatch logic.
