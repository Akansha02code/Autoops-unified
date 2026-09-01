"""
Human Approval Agent - minimal version. Takes a case_id and marks it
approved. Later this becomes a real dashboard button; for now it's a
script so you can test the full loop end to end.

Usage:
    python approve_case.py <case_id>

List pending cases first if you don't have an ID handy:
    python approve_case.py --list
"""
import sys

from backend.app.db import SessionLocal, Case


def list_pending():
    session = SessionLocal()
    try:
        pending = session.query(Case).filter(Case.status.like("pending%")).all()
        if not pending:
            print("No pending cases.")
        for c in pending:
            print(f"{c.case_id} | {c.item} | ₹{c.price} | {c.status}")
    finally:
        session.close()


def approve(case_id: str, approved_by: str = "manager_demo"):
    session = SessionLocal()
    try:
        case = session.query(Case).filter(Case.case_id == case_id).first()
        if not case:
            print(f"No case found with id {case_id}")
            return
        case.status = "approved"
        case.approved_by = approved_by
        session.commit()
        print(f"Case {case_id} ({case.item}) marked approved.")
    finally:
        session.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python approve_case.py <case_id>  OR  python approve_case.py --list")
        sys.exit(1)

    if sys.argv[1] == "--list":
        list_pending()
    else:
        approve(sys.argv[1])