"""
Invoice / Document Generator Agent - minimal version. Takes an approved
case and produces a simple PDF invoice.

Usage:
    python generate_invoice.py <case_id>

Requires: pip install reportlab
"""
import sys
import os
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from backend.app.db import SessionLocal, Case

OUTPUT_DIR = "generated_invoices"


def generate_invoice(case_id: str):
    session = SessionLocal()
    try:
        case = session.query(Case).filter(Case.case_id == case_id).first()
        if not case:
            print(f"No case found with id {case_id}")
            return
        if case.status != "approved":
            print(f"Case {case_id} is not approved yet (status: {case.status}). Approve it first.")
            return

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        filename = os.path.join(OUTPUT_DIR, f"invoice_{case.case_id}.pdf")

        c = canvas.Canvas(filename, pagesize=A4)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 800, "AutoOps - Generated Invoice")

        c.setFont("Helvetica", 11)
        c.drawString(50, 760, f"Case ID: {case.case_id}")
        c.drawString(50, 740, f"Item: {case.item}")
        c.drawString(50, 720, f"Quantity: {case.quantity}")
        c.drawString(50, 700, f"Price: {case.price}")
        c.drawString(50, 680, f"Approved by: {case.approved_by}")
        c.drawString(50, 660, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

        c.save()
        print(f"Invoice generated: {filename}")

    finally:
        session.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_invoice.py <case_id>")
        sys.exit(1)
    generate_invoice(sys.argv[1])