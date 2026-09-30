"use client";

import { useEffect, useState } from "react";
import { DashboardShell } from "../../components/DashboardShell";
import { PipelineFlow } from "../../components/PipelineFlow";
import { useCaseData } from "../../components/CaseDataProvider";

export default function PipelinePage() {
  return <DashboardShell title="Pipeline"><PipelineView /></DashboardShell>;
}

function PipelineView() {
  const { cases, loading, error } = useCaseData();
  const [selectedId, setSelectedId] = useState("");
  useEffect(() => { if (!selectedId && cases.length) setSelectedId(cases[0].case_id); }, [cases, selectedId]);
  const selected = cases.find(record => record.case_id === selectedId);
  return <main className="page-content"><div className="page-intro"><div><h2>Execution engine</h2><p>Follow a selected case across the shared automation pipeline.</p></div><span className="table-meta">LIVE MONITORING</span></div>
    {error && <div className="inline-error" role="alert">Pipeline data is unavailable while the backend is offline. ({error})</div>}
    <section className="panel" style={{ padding: 18 }}><div className="pipeline-toolbar"><label htmlFor="pipeline-case">Tracking case</label><select className="pipeline-select" id="pipeline-case" value={selectedId} onChange={event => setSelectedId(event.target.value)}><option value="">{loading && !cases.length ? "Loading cases…" : cases.length ? "Select a case" : "No cases available"}</option>{cases.map(record => <option key={record.case_id} value={record.case_id}>{record.case_id} · {record.item ?? "New case"} · {record.status.replaceAll("_", " ")}</option>)}</select>{selected && <span className="table-meta">Last updated from case status</span>}</div><PipelineFlow record={selected} /></section>
    <div className="overview-grid" style={{ marginTop: 17 }}><section className="panel"><div className="panel-header"><h3>Unified intake</h3></div><div className="activity-list"><div className="activity-row"><span className="source-mark">▤</span><span className="activity-main"><b>Document-triggered</b><small>OCR and extraction prepare structured fields.</small></span></div><div className="activity-row"><span className="source-mark request">“</span><span className="activity-main"><b>Request-triggered</b><small>Intent and planning turn natural language into actions.</small></span></div></div></section><section className="panel"><div className="panel-header"><h3>Current monitor</h3></div><div className="activity-list"><div className="activity-row"><span className="live-dot" /><span className="activity-main"><b>{loading ? "Connecting" : error ? "Backend unavailable" : "Polling active"}</b><small>{error ? "Reconnect the API to resume monitoring." : "Case state refreshes every 15 seconds."}</small></span></div></div></section></div>
  </main>;
}