"""
Wires the extraction + policy pipeline into the real database.
This is the first version that actually writes a row into Postgres.

Usage:
    python run_pipeline.py sample_docs/batch1-1486.jpg
"""
import sys
import json

from ocr_test import extract_text
from extract_test import extract_structured
from policy_check import check_policy
from backend.app.db import SessionLocal, Case


def run(image_path: str):
    text = extract_text(image_path)
    case = extract_structured(text)
    case = check_policy(case)

    status = "pending_cfo_approval" if case["policy_status"] == "flagged" else "pending_approval"

    db_case = Case(
        source_type="document",
        item=case.get("item"),
        quantity=int(case["quantity"]) if case.get("quantity") else None,
        price=case.get("price"),
        status=status,
        policy_flags=case.get("policy_flags", []),
    )

    session = SessionLocal()
    try:
        session.add(db_case)
        session.commit()
        session.refresh(db_case)
        print(f"Inserted case {db_case.case_id} with status '{db_case.status}'")
        print(json.dumps(case, indent=2))
    finally:
        session.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_pipeline.py <path_to_image>")
        sys.exit(1)
    run(sys.argv[1])