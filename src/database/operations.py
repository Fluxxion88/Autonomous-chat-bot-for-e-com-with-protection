import uuid
import datetime
from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from src.database.connection import get_session, db1_actions, db2_auditlog
from src.utils.hashing import generate_hash

def log_discount(discount_val: str) -> bool:
    """
    Implements double-logging transaction logic.
    Validates strictly numeric.
    Inserts into DB1 (plaintext) and DB2 (hash) simultaneously.
    Rolls back on failure.
    Returns True on success, False otherwise.
    """
    if not discount_val.isdigit():
        print(f"Error: discount_val '{discount_val}' is not strictly numeric.")
        return False

    session = get_session()
    
    # Generate common ID
    transaction_id = str(uuid.uuid4())
    current_time = datetime.datetime.utcnow()
    
    try:
        # 1. Insert into DB1
        ins_db1 = db1_actions.insert().values(
            id=transaction_id,
            timestamp=current_time,
            discount_val=discount_val
        )
        session.execute(ins_db1)
        
        # 2. Insert into DB2
        discount_hash = generate_hash(discount_val)
        ins_db2 = db2_auditlog.insert().values(
            id=transaction_id,
            timestamp=current_time,
            discount_hash=discount_hash
        )
        session.execute(ins_db2)
        
        # Commit transaction
        session.commit()
        return True
    
    except SQLAlchemyError as e:
        print(f"Database transaction failed. Rolling back. Error: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def fetch_db1_records():
    """Fetch all records from DB1_Actions ordered by timestamp descending."""
    session = get_session()
    try:
        query = select(db1_actions).order_by(db1_actions.c.timestamp.desc())
        result = session.execute(query).fetchall()
        return [{"id": row.id, "timestamp": row.timestamp, "discount_val": row.discount_val} for row in result]
    except Exception as e:
        print(f"Failed to fetch DB1 records: {e}")
        return []
    finally:
        session.close()

def fetch_db2_records():
    """Fetch all records from DB2_AuditLog ordered by timestamp descending."""
    session = get_session()
    try:
        query = select(db2_auditlog).order_by(db2_auditlog.c.timestamp.desc())
        result = session.execute(query).fetchall()
        return [{"id": row.id, "timestamp": row.timestamp, "discount_hash": row.discount_hash} for row in result]
    except Exception as e:
        print(f"Failed to fetch DB2 records: {e}")
        return []
    finally:
        session.close()

def evaluate_claim(transaction_id: str, current_discount_val: str, global_limit: int) -> str:
    """
    Evaluates a claim based on the Global Limit and audit hash.
    Returns the claim status string.
    """
    try:
        discount_int = int(current_discount_val)
    except ValueError:
        return "Error: Invalid discount value format"

    # Rule 1: <= limit -> "Denied, within permission limit"
    if discount_int <= global_limit:
        return "Denied, within permission limit"
        
    # Rule 2: > limit -> Check hash
    session = get_session()
    try:
        query = select(db2_auditlog).where(db2_auditlog.c.id == transaction_id)
        result = session.execute(query).fetchone()
        
        if not result:
            return "Error: Audit record not found"
            
        stored_hash = result.discount_hash
        expected_hash = generate_hash(current_discount_val)
        
        if stored_hash == expected_hash:
            return "Approved, Coverage wired"
        else:
            return "Denied, hash mismatch"
    except Exception as e:
        print(f"Failed to evaluate claim: {e}")
        return "Error evaluating claim"
    finally:
        session.close()

def update_db1_record(transaction_id: str, new_discount_val: str) -> bool:
    """
    Updates the discount_val in DB1_Actions for tampering simulation.
    Strictly avoids updating DB2.
    """
    session = get_session()
    try:
        stmt = update(db1_actions).where(db1_actions.c.id == transaction_id).values(discount_val=new_discount_val)
        session.execute(stmt)
        session.commit()
        return True
    except Exception as e:
        print(f"Failed to update DB1 record: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def seed_data():
    """Seed the database with initial transactions if it's empty."""
    records = fetch_db1_records()
    if not records:
        print("Seeding database with initial transactions...")
        for val in ["10", "20", "100"]:
            log_discount(val)
