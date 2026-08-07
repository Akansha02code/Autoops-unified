"""
AutoOps unified platform - backend entrypoint.

Run locally with:
    uvicorn app.main:app --reload --port 8000

This is intentionally minimal for day 1. As you build agents, wire them
in as routes here (e.g. /submit-document, /submit-request) that call into
agents/graph.py.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="AutoOps Unified Platform")

# Allow local Next.js dev servers to call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    """Sanity check - hit this first after `uvicorn app.main:app --reload`."""
    return {"status": "ok", "service": "autoops-backend"}


class RequestIn(BaseModel):
    text: str


@app.post("/submit-request")
def submit_request(payload: RequestIn):
    """
    Entry point for the natural-language request path.
    Today: just echoes back. Next: call the intent/planning agent graph.
    """
    return {"received": payload.text, "status": "not_yet_processed"}


# Document upload endpoint goes here once the OCR/extraction agent exists:
# @app.post("/submit-document")
# async def submit_document(file: UploadFile): ...
