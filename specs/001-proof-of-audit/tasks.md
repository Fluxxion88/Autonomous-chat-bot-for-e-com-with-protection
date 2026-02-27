# Tasks: Proof of Audit

**Input**: Design documents from `/specs/001-proof-of-audit/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: This project is a hackathon prototype. Formal automated tests (like pytest) are secondary to functional independent testing of each user story, but can be added in the polish phase if desired.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/` at repository root
- As per plan, Streamlit app runs from `src/main.py`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Initialize Python project, create `requirements.txt` with `streamlit`, `openai`, `psycopg2-binary`, `python-dotenv`, `sqlalchemy`, `pytest`
- [x] T002 Create project structure (`src/`, `src/database/`, `src/services/`, `src/utils/`)
- [x] T003 [P] Set up environment configuration loading in `src/config.py`
- [x] T004 [P] Set up basic Streamlit entry point structure in `src/main.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Implement database connection and table initialization for `DB1_Actions` and `DB2_AuditLog` in `src/database/connection.py`
- [x] T006 [P] Create SHA-256 hashing utility in `src/utils/hashing.py`
- [x] T007 Configure OpenAI API client with the Structured Outputs format (`contracts/llm-schema.json`) in `src/services/ai_agent.py`

**Checkpoint**: Foundation ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - Configure Global Limit (Priority: P1) 🎯 MVP

**Goal**: As an Operator, I want to set a global limit for approved discounts so that I can control the maximum discount an AI agent can issue without manual review.

**Independent Test**: Can be fully tested by setting the value in the "Limit Settings" on the dashboard and saving it.

### Implementation for User Story 1

- [x] T008 [US1] Add a sidebar or specific layout section in `src/main.py` for Operator "Limit Settings" input.
- [x] T009 [US1] Implement Streamlit session state management to store and update the "Global Limit" in `src/main.py`.

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently.

---

## Phase 4: User Story 2 - Request and Receive Discount (Priority: P1)

**Goal**: As a Customer, I want to ask for a discount in the chat so that the AI agent can process my request and generate a promo code.

**Independent Test**: Can be tested by sending a chat message and verifying that the agent responds with a JSON-based message and discount string, and that entries appear in both DB1 and DB2.

### Implementation for User Story 2

- [x] T010 [P] [US2] Implement double-logging transaction logic (insert DB1 and DB2 simultaneously, rollback on DB2 failure) in `src/database/operations.py`
- [x] T011 [P] [US2] Implement strictly numeric check in `src/database/operations.py` before database insertion, rejecting non-numeric values.
- [x] T012 [P] [US2] Implement the OpenAI API call to evaluate user requests and return structured output, handling 10s timeout and returning fallback ("0"), in `src/services/ai_agent.py`
- [x] T013 [US2] Implement Customer chat interface in `src/main.py` using Streamlit chat elements.
- [x] T014 [US2] Wire Customer chat input to `ai_agent.py` and then to `operations.py` for logging in `src/main.py`.

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently.

---

## Phase 5: User Story 3 - Validate Legitimate Claim (Priority: P1)

**Goal**: As an Operator, I want to file a claim for a recorded discount to ensure its authenticity against the audit log.

**Independent Test**: Can be tested by selecting an unmodified transaction from the dashboard and clicking "File Claim".

### Implementation for User Story 3

- [x] T015 [P] [US3] Create function to fetch `DB1_Actions` and `DB2_AuditLog` records in `src/database/operations.py`
- [x] T016 [P] [US3] Implement logic to evaluate claims based on Global Limit (<= limit: "Denied, within permission limit"; > limit: compare hashes -> "Approved, Coverage wired" or "Denied, hash mismatch") in `src/database/operations.py`
- [x] T017 [US3] Create Operator dashboard table view showing transactions from DB1 in `src/main.py`.
- [x] T018 [US3] Add "File Claim" interaction for rows in the Operator dashboard in `src/main.py` and wire it to the evaluation logic, displaying the correct status.
- [x] T019 [US3] Create separate tab for "DB2: Secure Audit Log" to display immutable hashes in `src/main.py`.

**Checkpoint**: All normal flows should now be independently functional.

---

## Phase 6: User Story 4 - Detect Tampered Claim (Priority: P1)

**Goal**: As an Operator, I want the system to block tampered records when I file a claim so that fraudulent changes are detected.

**Independent Test**: Can be tested by manually editing a DB1 record and then filing a claim to see the hash mismatch block.

### Implementation for User Story 4

- [x] T020 [US4] Update `src/database/operations.py` to support updating a `discount_val` in `DB1_Actions` (simulating tampering, strictly avoiding DB2 updates).
- [x] T021 [US4] Implement a Streamlit data editor or manual edit action for `DB1_Actions` rows in `src/main.py` to allow Operator manual editing.
- [x] T022 [US4] Verify that the "File Claim" interaction correctly returns "Denied, hash mismatch" for tampered records in `src/main.py`.

**Checkpoint**: Tampering simulation and detection is now fully functional.

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T023 [P] Implement graceful degradation/error handling in UI for DB connection drops ("Reconnecting to Audit Server...") in `src/main.py`.
- [x] T024 [P] Code cleanup, refactoring, and adding inline documentation.
- [x] T025 Execute end-to-end dry run to ensure demo script completes in <3 minutes smoothly.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - Due to the nature of the MVP, US2, US3, and US4 benefit from sequential progression, but data-layer tasks can run in parallel.
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2).
- **User Story 2 (P1)**: Can start after Foundational (Phase 2). Independent from US1.
- **User Story 3 (P1)**: Depends on US2 to have sample data to display and validate.
- **User Story 4 (P1)**: Depends on US3 to build upon the "File Claim" and table view functionality.

### Parallel Opportunities

- Setup and Foundational tasks marked `[P]` can run in parallel.
- `src/database/operations.py` logic and `src/services/ai_agent.py` logic can be implemented independently before wiring them into `src/main.py`.

---

## Implementation Strategy

### MVP First (User Story 1 & 2)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (Global Limit UI)
4. Complete Phase 4: User Story 2 (Chat & Double Logging)
5. **STOP and VALIDATE**: Verify data appears correctly in both DB tables.

### Incremental Delivery

1. Deliver US1 & US2 for core functionality.
2. Deliver US3 to show the dashboard and valid claim workflow.
3. Deliver US4 to enable the tampering simulation.
4. Final Polish.
