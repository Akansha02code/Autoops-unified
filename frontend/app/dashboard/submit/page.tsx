"use client";

import { ChangeEvent, DragEvent, FormEvent, Suspense, useRef, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { DashboardShell } from "../../components/DashboardShell";
import { API_BASE, CaseRecord, fetchCases, formatINR, postAction } from "../../lib/api";
import { StatusBadge } from "../../components/StatusBadge";

export default function SubmitPage() {
  return <DashboardShell title="Submit"><Suspense fallback={<main className="page-content"><div className="skeleton" /></main>}><SubmitWorkflow /></Suspense></DashboardShell>;
}

function SubmitWorkflow() {
  const params = useSearchParams();
  const initialMode = params.get("mode") === "document" ? "document" : "request";
  const [mode, setMode] = useState<"request" | "document">(initialMode);
  const [text, setText] = useState("");
  const [requestBusy, setRequestBusy] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [dragging, setDragging] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadBusy, setUploadBusy] = useState(false);
  const [result, setResult] = useState<CaseRecord | null>(null);
  const [error, setError] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  async function submitRequest(event: FormEvent) {
    event.preventDefault(); setError(""); setResult(null); setRequestBusy(true);
    try {
      const response = await postAction("/submit-request", { text });
      const possibleCase = response.case ?? response;
      const direct = possibleCase.case_id ? possibleCase as CaseRecord : undefined;
      const current = direct ?? (await fetchCases()).sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())[0];
      if (!current) throw new Error("Request was accepted, but no resulting case was returned.");
      setResult(current); setText("");
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Could not submit request."); }
    finally { setRequestBusy(false); }
  }

  function chooseFile(candidate?: File) {
    if (!candidate) return;
    if (!/\.(pdf|jpe?g|png)$/i.test(candidate.name)) { setError("Choose a PDF, JPG, or PNG file."); return; }
    setFile(candidate); setError(""); setResult(null); setUploadProgress(0);
  }

  function uploadDocument() {
    if (!file) { setError("Choose a document before uploading."); return; }
    setError(""); setResult(null); setUploadBusy(true); setUploadProgress(0);
    const body = new FormData(); body.append("file", file);
    const xhr = new XMLHttpRequest();
    xhr.open("POST", `${API_BASE}/submit-document`);
    xhr.upload.onprogress = event => { if (event.lengthComputable) setUploadProgress(Math.round(event.loaded / event.total * 100)); };
    xhr.onerror = () => { setError("Could not connect to the AutoOps backend."); setUploadBusy(false); };
    xhr.onload = async () => {
      try {
        if (xhr.status < 200 || xhr.status >= 300) {
          const text = xhr.responseText;
          let message = `Upload failed (${xhr.status}).`;
          if (text) {
            try {
              const data = JSON.parse(text);
              message = typeof data.detail === "string" ? data.detail : message;
            } catch {
              message = text.length > 500 ? `${text.slice(0, 500)}…` : text;
            }
          }
          throw new Error(message);
        }
        const response = xhr.responseText ? JSON.parse(xhr.responseText) : {};
        const possibleCase = response.case ?? response;
        const direct = possibleCase.case_id ? possibleCase as CaseRecord : undefined;
        const current = direct ?? (await fetchCases()).sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())[0];
        if (!current) throw new Error("Document was accepted, but no resulting case was returned.");
        setUploadProgress(100); setResult(current); setFile(null);
      } catch (reason) { setError(reason instanceof Error ? reason.message : "Upload failed."); }
      finally { setUploadBusy(false); }
    };
    xhr.send(body);
  }

  return <main className="page-content"><div className="page-intro"><div><h2>Bring work into AutoOps</h2><p>Start from a purchase request or let the agents read the source document.</p></div></div>
    <div className="tabs" role="tablist" aria-label="Submission type"><button role="tab" aria-selected={mode === "request"} className={`tab-button ${mode === "request" ? "active" : ""}`} onClick={() => setMode("request")}>Natural-language request</button><button role="tab" aria-selected={mode === "document"} className={`tab-button ${mode === "document" ? "active" : ""}`} onClick={() => setMode("document")}>Document upload</button></div>
    {error && <div className="inline-error" role="alert">{error} If the backend is offline, start FastAPI at 127.0.0.1:8000 and try again.</div>}
    <div className="submit-grid">
      {mode === "request" ? <form className="panel submit-panel" onSubmit={submitRequest}><h3>Submit a request</h3><p>Describe the business need in plain language. The pipeline will classify and plan it.</p><label className="form-label" htmlFor="request-text">What does your team need?</label><textarea id="request-text" className="request-textarea" required minLength={3} maxLength={2000} value={text} onChange={event => setText(event.target.value)} placeholder="5 laptops for new interns" /><div className="form-footer"><span className="help-text">Be specific about quantity and purpose.</span><button className="button button-primary" type="submit" disabled={requestBusy || !text.trim()}>{requestBusy ? "Submitting…" : "Submit request →"}</button></div></form> : <section className="panel submit-panel"><h3>Upload a document</h3><p>Upload an invoice or purchase order for automatic extraction and review.</p><span className="form-label">Choose a source file</span>
        <div className={`drop-zone ${dragging ? "dragging" : ""}`} onDragOver={(event: DragEvent) => { event.preventDefault(); setDragging(true); }} onDragLeave={() => setDragging(false)} onDrop={(event: DragEvent) => { event.preventDefault(); setDragging(false); chooseFile(event.dataTransfer.files[0]); }}>
          <div className="drop-inner"><span className="drop-icon">↑</span><b>{file ? file.name : "Drop your file here, or browse"}</b><small>{file ? `${(file.size / 1024 / 1024).toFixed(2)} MB · Ready to upload` : "PDF, JPG or PNG · up to 20 MB"}</small><input ref={inputRef} className="file-input" type="file" accept=".pdf,.jpg,.jpeg,.png,application/pdf,image/jpeg,image/png" aria-label="Choose document file" onChange={(event: ChangeEvent<HTMLInputElement>) => chooseFile(event.target.files?.[0])} /></div>
        </div>
        {uploadBusy && <div className="upload-progress" aria-label={`Upload ${uploadProgress}%`}><span style={{ width: `${uploadProgress}%` }} /></div>}
        <div className="form-footer"><span className="help-text">{uploadBusy ? `Uploading ${uploadProgress}%` : "Your file is sent securely to the processing API."}</span><button className="button button-primary" disabled={!file || uploadBusy} onClick={uploadDocument}>{uploadBusy ? "Processing…" : "Upload document ↑"}</button></div>
      </section>}
      <section className="panel submit-panel"><h3>One process, clear decisions</h3><p>Every submission follows the same policy and approval controls.</p><div className="activity-list"><div className="activity-row"><span className="source-mark">01</span><span className="activity-main"><b>Classify and extract</b><small>Turn source material into structured data</small></span></div><div className="activity-row"><span className="source-mark">02</span><span className="activity-main"><b>Check policy</b><small>Apply shared business rules and flags</small></span></div><div className="activity-row"><span className="source-mark">03</span><span className="activity-main"><b>Review and execute</b><small>Keep people in the loop at decision points</small></span></div></div></section>
    </div>
    {result && <section className="result-card"><h4>Submission received</h4><div className="result-data"><span>CASE ID<b>{result.case_id}</b></span><span>ITEM<b>{result.item ?? "Awaiting extraction"}</b></span><span>QUANTITY<b>{result.quantity ?? "—"}</b></span><span>PRICE (INR)<b>{formatINR(result.price)}</b></span><span>STATUS<b><StatusBadge status={result.status} /></b></span></div><Link className="result-link" href={`/dashboard/cases?case_id=${encodeURIComponent(result.case_id)}`}>View this case in case management →</Link></section>}
  </main>;
}