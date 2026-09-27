"""
Full request-path pipeline - the natural-language equivalent of
run_pipeline.py. Chains: intent parsing -> catalog lookup -> policy
check -> DB insert, reusing the exact same policy_check.py and
Case model the document path already uses.

Usage:
    python run_request_pipeline.py "5 laptops for new interns"
"""
import sys
import json

from intent_parse import parse_intent
from catalog_lookup import enrich_with_catalog
from policy_check import check_policy
from backend.app.db import SessionLocal, Case


def run(request_text: str):
    case = parse_intent(request_text)

    if not case.get("is_new_request") or str(case.get("is_new_request")).lower() == "false":
        print("Not processed further - not classified as a new request.")
        print(json.dumps(case, indent=2))
        return

    case = enrich_with_catalog(case)
    case = check_policy(case)

    status = "pending_cfo_approval" if case["policy_status"] == "flagged" else "pending_approval"

    db_case = Case(
        source_type="request",
        item=case.get("catalog_match") or case.get("item"),
        quantity=int(case["quantity"]) if case.get("quantity") else None,
        department=case.get("department"),
        price=case.get("price"),
        requester=case.get("requester"),
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
        print('Usage: python run_request_pipeline.py "your request text here"')
        sys.exit(1)
    run(sys.argv[1])