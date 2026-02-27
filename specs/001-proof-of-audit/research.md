# Research & Decisions: Proof of Audit

## 1. UI Framework: Streamlit
- **Decision**: Use Streamlit for the complete Operator and Customer experience.
- **Rationale**: Python-native, explicitly required in PRD for rapid assembly of dashboards, chats, and interactive tables.
- **Alternatives considered**: React (TypeScript) frontend + FastAPI backend. Discarded as it introduces too much complexity for a hackathon MVP.

## 2. LLM Engine & Response Format
- **Decision**: OpenAI API (e.g., gpt-4o-mini) with Structured Outputs feature.
- **Rationale**: Required by PRD. Ensuring the LLM returns strictly `{ "chat_message": "...", "discount_str": "..." }` bypasses brittle string parsing.
- **Alternatives considered**: Standard completions with prompting to output JSON + Regex/JSON parser fallback. Discarded as Structured Outputs guarantees a 100% adherence rate.

## 3. Storage and State Management
- **Decision**: AWS RDS (PostgreSQL).
- **Rationale**: Persists data between application restarts (required since Render containers spin down/restart).
- **Alternatives considered**: SQLite. Discarded because Render instances have ephemeral file systems by default, losing data on restart.

## 4. Double Logging Transaction Strategy
- **Decision**: Wrap DB1 (plaintext) and DB2 (SHA-256 hash) inserts into a single SQL `BEGIN...COMMIT` block using `psycopg2` or `SQLAlchemy`.
- **Rationale**: The PRD mandates synchronous insertion with rollback if DB2 fails.
- **Alternatives considered**: Two separate API calls or event-driven logging. Discarded due to risk of "split-brain" where DB1 records an entry that DB2 misses, defeating the Proof of Audit.
