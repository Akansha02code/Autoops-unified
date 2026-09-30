"""
AutoOps unified platform - backend API.

Wires the existing pipeline scripts (run_pipeline, run_request_pipeline,
approve_case, generate_invoice) into real HTTP endpoints the web
dashboard can call, instead of running them from the command line.

Run with:
    uvicorn app.main:app --reload --port 8000
"""
import os
import shutil
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.app.db import SessionLocal, Case
from run_pipeline import run as run_document_pipeline
from run_request_pipeline import run as run_request_pipeline
from generate_invoice import generate_invoice

app = FastAPI(title="AutoOps Unified Platform")

# Allow the Next.js dev server (localhost:3000) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","http://localhost:3002"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploaded_documents"


@app.get("/health")
def health():
    return {"status": "ok", "service": "autoops-backend"}


# ---- Cases (used by the approval dashboard) ----

@app.get("/cases")
def list_cases(status: str | None = None):
    """List all cases, optionally filtered by status
    (e.g. ?status=pending_approval)."""
    session = SessionLocal()
    try:
        query = session.query(Case)
        if status:
            query = query.filter(Case.status == status)
        cases = query.order_by(Case.created_at.desc()).all()
        return [
            {
                "case_id": c.case_id,
                "source_type": c.source_type,
                "item": c.item,
                "quantity": c.quantity,
                "department": c.department,
                "price": c.price,
                "original_currency": c.original_currency,
                "original_price": c.original_price,
                "requester": c.requester,
                "status": c.status,
                "policy_flags": c.policy_flags,
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "approved_by": c.approved_by,
            }
            for c in cases
        ]
    finally:
        session.close()


class ApproveRequest(BaseModel):
    approved_by: str = "manager_demo"


@app.post("/cases/{case_id}/approve")
def approve_case_endpoint(case_id: str, body: ApproveRequest):
    session = SessionLocal()
    try:
        case = session.query(Case).filter(Case.case_id == case_id).first()
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        case.status = "approved"
        case.approved_by = body.approved_by
        session.commit()
        return {"case_id": case_id, "status": "approved"}
    finally:
        session.close()


@app.post("/cases/{case_id}/reject")
def reject_case_endpoint(case_id: str):
    session = SessionLocal()
    try:
        case = session.query(Case).filter(Case.case_id == case_id).first()
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        case.status = "rejected"
        session.commit()
        return {"case_id": case_id, "status": "rejected"}
    finally:
        session.close()


@app.post("/cases/{case_id}/generate-invoice")
def generate_invoice_endpoint(case_id: str):
    generate_invoice(case_id)
    filepath = f"generated_invoices/invoice_{case_id}.pdf"
    if not os.path.exists(filepath):
        raise HTTPException(status_code=400, detail="Invoice could not be generated (case may not be approved)")
    return {"case_id": case_id, "invoice_path": filepath}


# ---- Document path: upload a file, run it through the pipeline ----

@app.post("/submit-document")
async def submit_document(file: UploadFile = File(...)):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(UPLOAD_DIR, f"{timestamp}_{file.filename}")

    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        run_document_pipeline(filepath)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {e}")

    return {"filename": file.filename, "status": "processed"}


# ---- Request path: submit plain-language text ----

class RequestIn(BaseModel):
    text: str


@app.post("/submit-request")
def submit_request(payload: RequestIn):
    try:
        run_request_pipeline(payload.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {e}")

    return {"received": payload.text, "status": "processed"}