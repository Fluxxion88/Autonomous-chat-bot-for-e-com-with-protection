# Quickstart: Proof of Audit

## 1. Prerequisites
- Python 3.11+
- PostgreSQL database (local or AWS RDS instance)
- OpenAI API Key

## 2. Environment Setup

1. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   # or venv\Scripts\activate # Windows
   ```

2. Install dependencies:
   ```bash
   pip install streamlit psycopg2-binary openai python-dotenv
   ```

3. Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   DATABASE_URL=postgresql://user:password@host:port/dbname
   ```

## 3. Database Initialization
Ensure your target PostgreSQL database exists. The application should handle creating the `DB1_Actions` and `DB2_AuditLog` tables if they do not exist upon startup.

## 4. Running the Application

Start the Streamlit development server:
```bash
streamlit run src/main.py
```

The application will launch in your default web browser (typically at `http://localhost:8501`).

## 5. Deployment
For deployment to Render:
1. Connect your GitHub repository.
2. Select "Web Service" and use `Python 3` as the environment.
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `streamlit run src/main.py --server.port $PORT`
5. Add `OPENAI_API_KEY` and `DATABASE_URL` (connected to an attached AWS RDS or Render Postgres instance) to your environment variables.
