# Implementation Plan: Proof of Audit

**Branch**: `001-proof-of-audit` | **Date**: February 27, 2026 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-proof-of-audit/spec.md`

## Summary

Build a lightweight SaaS prototype using Streamlit and Python to demonstrate a "Proof of Audit" concept. The app features an Operator dashboard and Customer chat, communicating with an AI Engine (OpenAI API) to generate discounts, and securely double-logging transactions (plaintext and SHA-256 hash) in PostgreSQL to detect tampering.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Streamlit (UI/Frontend), openai (LLM), psycopg2-binary or SQLAlchemy (DB access), python-dotenv  
**Storage**: PostgreSQL (AWS RDS)  
**Testing**: pytest  
**Target Platform**: Web application (deployed on Render)  
**Project Type**: Web dashboard and Chatbot Prototype  
**Performance Goals**: Support a full demo cycle in <3 minutes, AI responses under 10 seconds.  
**Constraints**: Append-only DB2, single DB transaction for DB1 and DB2 inserts, 10s LLM timeout.  
**Scale/Scope**: Lightweight SaaS prototype for demonstration purposes.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

No explicit constitution violations detected. The project uses standard Python tools and follows simplicity principles suitable for a hackathon/prototype.

## Project Structure

### Documentation (this feature)

```text
specs/001-proof-of-audit/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (to be created)
```

### Source Code (repository root)

```text
# Single project structure for Streamlit App
src/
├── main.py              # Streamlit entry point (UI + Chat)
├── config.py            # Environment and global configuration
├── database/
│   ├── connection.py    # PostgreSQL connection logic
│   └── operations.py    # Transaction logic (double logging)
├── services/
│   └── ai_agent.py      # OpenAI API interaction (Structured Outputs)
└── utils/
    └── hashing.py       # SHA-256 logic

tests/
├── integration/
└── unit/
```

**Structure Decision**: A single cohesive Python application with a `src/` directory separating the Streamlit UI (`main.py`) from the database and AI services.

## Complexity Tracking

No constitution violations requiring complexity tracking.
