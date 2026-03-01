import streamlit as st
import sys
import os

# Ensure src module is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import OPENAI_API_KEY, DATABASE_URL
from src.database.connection import init_db
from src.database.operations import log_discount, fetch_db1_records, fetch_db2_records, evaluate_claim, update_db1_record, seed_data
from src.services.ai_agent import generate_discount_offer

def initialize():
    """Initialize database and session state."""
    try:
        init_db()
        seed_data()
    except Exception as e:
        st.error(f"Failed to connect to the database. Check connection settings. Error: {e}")
        st.stop()
        
    if "global_limit" not in st.session_state:
        st.session_state.global_limit = 20
    if "messages" not in st.session_state:
        st.session_state.messages = []

def main():
    st.set_page_config(page_title="Proof of Audit Demo", layout="wide")
    
    if not OPENAI_API_KEY:
        st.error("Missing critical environment variables. Please check your .env file.")
        st.stop()
        
    initialize()

    st.title("Autonomous AI Agent: Proof of Audit")

    # Layout: Operator Dashboard (Sidebar) & Customer Chat (Main)
    with st.sidebar:
        st.header("Operator Dashboard")
        st.subheader("Limit Settings")
        
        new_limit = st.number_input("Global Limit (%)", min_value=0, max_value=100, value=st.session_state.global_limit, step=1)
        if st.button("Save Limit"):
            st.session_state.global_limit = new_limit
            st.success(f"Global limit updated to {new_limit}%")
            
        st.markdown("---")
        st.write(f"**Current Global Limit:** {st.session_state.global_limit}%")

    # Main area has two main columns: Chat and Dashboard Views
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.header("Customer Chat")
        
        # Display chat messages
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Chat input
        if prompt := st.chat_input("Ask for a discount..."):
            # Display user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Generate response
            with st.spinner("AI Agent is processing..."):
                response = generate_discount_offer(prompt)
                chat_msg = response.get("chat_message", "An error occurred.")
                discount_str = response.get("discount_str", "0")
                
                # Double Log the transaction
                success = log_discount(discount_str)
                
                if not success:
                    chat_msg = "Произошла системная ошибка генерации купона"
                    st.error("Transaction failed to log securely.")

                # Display assistant message
                full_response = f"{chat_msg}\n\n*(System Note: Discount generated: {discount_str}%)*"
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                with st.chat_message("assistant"):
                    st.markdown(full_response)
                    
    with col2:
        # Создаем две колонки для заголовка и кнопки
        col_header, col_btn = st.columns([3, 1])
        with col_header:
            st.header("Data & Audit Logs")
        with col_btn:
            st.write("") # Небольшой отступ, чтобы выровнять кнопку по центру заголовка
            st.link_button("Verifier link ↗", "https://agentriskscore.com/agents")

        tab1, tab2 = st.tabs(["DB1: Actions Log", "DB2: Secure Audit Log"])
        
        with tab1:
            st.subheader("DB1_Actions (Plaintext)")
            db1_records = fetch_db1_records()
            if db1_records:
                for rec in db1_records:
                    with st.container():
                        c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
                        c1.write(f"**ID**: `{rec['id']}`")
                        
                        # Tampering simulation
                        new_val = c2.text_input("Discount", value=rec['discount_val'], key=f"edit_{rec['id']}")
                        if new_val != rec['discount_val']:
                            if c2.button("Tamper", key=f"tamper_{rec['id']}"):
                                if update_db1_record(rec['id'], new_val):
                                    st.rerun()
                                    
                        c3.write(f"**Time**: {rec['timestamp'].strftime('%H:%M:%S')}")
                        if c4.button("File Claim", key=f"claim_{rec['id']}"):
                            status = evaluate_claim(rec['id'], new_val, st.session_state.global_limit)
                            if "Denied" in status:
                                st.error(f"Claim Status: **{status}**")
                            else:
                                st.success(f"Claim Status: **{status}**")
                        st.markdown("---")
            else:
                st.write("No records found.")
                
        with tab2:
            st.subheader("DB2_AuditLog (Immutable Hashes)")
            db2_records = fetch_db2_records()
            if db2_records:
                for rec in db2_records:
                    st.write(f"**ID**: `{rec['id']}` | **Hash**: `{rec['discount_hash'][:20]}...`")
                    st.markdown("---")
            else:
                st.write("No records found.")

if __name__ == "__main__":
    main()

