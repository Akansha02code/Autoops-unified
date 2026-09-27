"""
Invoice / Document Generator Agent - polished version with a proper
header, organization branding, itemized table, and footer, instead of
plain coordinate-placed text lines.

Usage:
    python generate_invoice.py <case_id>

Requires: pip install reportlab
"""
import sys
import os
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
)
from reportlab.lib.enums import TA_RIGHT, TA_CENTER

from backend.app.db import SessionLocal, Case

OUTPUT_DIR = "generated_invoices"
ORG_NAME = "AutoOps Technologies Pvt. Ltd."
ORG_ADDRESS = "4th Floor, Tech Park One, Mumbai, Maharashtra, India - 400001"
ORG_CONTACT = "GSTIN: 27ABCDE1234F1Z5  |  invoices@autoops.tech  |  +91-22-4000-1234"
ACCENT = colors.HexColor("#4B2E83")
ACCENT_LIGHT = colors.HexColor("#EAE6FB")


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

        doc = SimpleDocTemplate(
            filename, pagesize=A4,
            topMargin=20 * mm, bottomMargin=20 * mm,
            leftMargin=20 * mm, rightMargin=20 * mm,
        )
        styles = getSampleStyleSheet()
        story = []

        # ---- Header band: org name + invoice label ----
        header_data = [[
            Paragraph(f"<b><font size=16 color='#4B2E83'>{ORG_NAME}</font></b><br/>"
                      f"<font size=8 color='#555555'>{ORG_ADDRESS}</font><br/>"
                      f"<font size=8 color='#555555'>{ORG_CONTACT}</font>", styles["Normal"]),
            Paragraph("<b><font size=20 color='#4B2E83'>INVOICE</font></b>", ParagraphStyle(
                "invLabel", parent=styles["Normal"], alignment=TA_RIGHT)),
        ]]
        header_table = Table(header_data, colWidths=[110 * mm, 60 * mm])
        header_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
        story.append(header_table)
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=1.2, color=ACCENT))
        story.append(Spacer(1, 14))

        # ---- Invoice meta info ----
        invoice_no = f"AO-{case.case_id.split('-')[0].upper()}"
        generated_on = datetime.now().strftime("%d %b %Y, %H:%M")
        meta_data = [
            ["Invoice No:", invoice_no, "Source Type:", case.source_type or "-"],
            ["Date Generated:", generated_on, "Status:", case.status.upper()],
            ["Case ID:", case.case_id, "Approved By:", case.approved_by or "-"],
        ]
        meta_table = Table(meta_data, colWidths=[32 * mm, 63 * mm, 30 * mm, 45 * mm])
        meta_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#333333")),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 18))

        # ---- Line item table ----
        item_header = ["#", "Description", "Qty", "Department", "Amount (INR)"]
        item_row = [
            "1",
            Paragraph(case.item or "-", styles["Normal"]),
            str(case.quantity or "-"),
            case.department or "-",
            f"{case.price:,.2f}" if case.price is not None else "-",
        ]
        item_table = Table(
            [item_header, item_row],
            colWidths=[10 * mm, 70 * mm, 20 * mm, 35 * mm, 35 * mm],
        )
        item_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9.5),
            ("ALIGN", (2, 0), (2, -1), "CENTER"),
            ("ALIGN", (4, 0), (4, -1), "RIGHT"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7F5FB")]),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(item_table)
        story.append(Spacer(1, 10))

        # ---- Currency conversion notice (only shown if source wasn't INR) ----
        if case.original_currency and case.original_price is not None:
            story.append(Paragraph(
                f"<font size=9 color='#4B2E83'><b>Currency Converted:</b> "
                f"Original amount {case.original_price:,.2f} {case.original_currency} "
                f"&rarr; INR {case.price:,.2f} "
                f"(rate used: 1 {case.original_currency} = {case.exchange_rate} INR)</font>",
                styles["Normal"]))
            story.append(Spacer(1, 8))

        # ---- Total row ----
        total_data = [["", "Total Amount Due", f"INR {case.price:,.2f}" if case.price is not None else "-"]]
        total_table = Table(total_data, colWidths=[95 * mm, 40 * mm, 35 * mm])
        total_table.setStyle(TableStyle([
            ("FONTNAME", (1, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (1, 0), (-1, 0), 11),
            ("ALIGN", (1, 0), (-1, 0), "RIGHT"),
            ("LINEABOVE", (1, 0), (-1, 0), 0.8, ACCENT),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("TEXTCOLOR", (1, 0), (-1, 0), ACCENT),
        ]))
        story.append(total_table)
        story.append(Spacer(1, 4))

        if case.policy_flags:
            flags_text = ", ".join(f["action"].replace("_", " ").title() for f in case.policy_flags)
            story.append(Paragraph(
                f"<font size=8 color='#8A6200'><b>Policy notes:</b> {flags_text}</font>",
                styles["Normal"]))

        story.append(Spacer(1, 40))
        story.append(HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#CCCCCC")))
        story.append(Spacer(1, 6))
        story.append(Paragraph(
            "<font size=8 color='#777777'>This is a system-generated invoice from the AutoOps "
            "unified automation platform and does not require a physical signature. "
            "For queries, contact invoices@autoops.tech.</font>",
            styles["Normal"]))

        doc.build(story)
        print(f"Invoice generated: {filename}")

    finally:
        session.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_invoice.py <case_id>")
        sys.exit(1)
    generate_invoice(sys.argv[1])