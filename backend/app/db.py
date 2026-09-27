"""
Database models - the shared "case" table both the document path and
the request path write into.

Run once to create the table:
    python -m app.db

Note: price is always stored in INR (the base currency policy rules
are written in) - original_currency / original_price / exchange_rate
preserve what the source document actually stated, for transparency.
"""
import os
import uuid
from datetime import datetime, timezone

from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/autoops")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class Case(Base):
    __tablename__ = "cases"

    case_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    source_type = Column(String, nullable=False)   # "document" | "request"
    item = Column(String)
    quantity = Column(Integer)
    department = Column(String)
    destination = Column(String, nullable=True)
    price = Column(Float)                          # always stored in INR
    original_currency = Column(String, nullable=True)   # e.g. "USD" - null if source was already INR
    original_price = Column(Float, nullable=True)       # amount as stated in the source document
    exchange_rate = Column(Float, nullable=True)        # rate used to convert to INR
    requester = Column(String, nullable=True)
    status = Column(String, default="pending_extraction")
    policy_flags = Column(JSON, default=list)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    approved_by = Column(String, nullable=True)


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    print("cases table created/verified (existing tables are not altered automatically)")