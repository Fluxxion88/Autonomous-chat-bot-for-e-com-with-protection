import os
from sqlalchemy import create_engine, MetaData, Table, Column, String, DateTime
from sqlalchemy.orm import sessionmaker
from src.config import DATABASE_URL
import datetime

# Create SQLAlchemy engine
# Make sure DATABASE_URL is not None
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set. Please check your environment variables.")

engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Define tables
db1_actions = Table(
    'db1_actions', metadata,
    Column('id', String, primary_key=True),
    Column('timestamp', DateTime, default=datetime.datetime.utcnow),
    Column('discount_val', String, nullable=False)
)

db2_auditlog = Table(
    'db2_auditlog', metadata,
    Column('id', String, primary_key=True),
    Column('timestamp', DateTime, default=datetime.datetime.utcnow),
    Column('discount_hash', String, nullable=False)
)

def init_db():
    """Create tables if they don't exist."""
    metadata.create_all(engine)

def get_session():
    """Get a new SQLAlchemy session."""
    Session = sessionmaker(bind=engine)
    return Session()
