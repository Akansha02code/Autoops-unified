"""
Wires the extraction + currency conversion + policy pipeline into the
real database.

Usage:
    python run_pipeline.py sample_docs/batch1-1486.jpg
"""
import sys
import json

from ocr_test import extract_text
from extract_test import extract_structured
from currency_convert import convert_to_inr
from policy_check import check_policy
from backend.app.db import SessionLocal, Case


def run(image_path: str):
    text = extract_text(image_path)
    case = extract_structured(text)

    # Convert to INR BEFORE the policy check, since thresholds are in INR.
    original_price = case.get("price")
    original_currency = case.get("currency")
    converted_price, rate, conversion_note = convert_to_inr(original_price, original_currency)
    case["price"] = converted_price  # policy_check now sees the INR amount
    if conversion_note:
        print(f"NOTE: {conversion_note}")

    case = check_policy(case)

    status = "pending_cfo_approval" if case["policy_status"] == "flagged" else "pending_approval"

    db_case = Case(
        source_type="document",
        item=case.get("item"),
        quantity=int(case["quantity"]) if case.get("quantity") else None,
        price=case.get("price"),  # INR, post-conversion
        original_currency=original_currency if original_currency and original_currency != "INR" else None,
        original_price=original_price if original_currency and original_currency != "INR" else None,
        exchange_rate=rate if original_currency and original_currency != "INR" else None,
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