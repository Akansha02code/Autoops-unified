"use client";

import Link from "next/link";
import { DashboardShell } from "../components/DashboardShell";
import { StatusBadge } from "../components/StatusBadge";
import { useCaseData } from "../components/CaseDataProvider";
import { relativeTime } from "../lib/api";

export default function DashboardPage() {
  return <DashboardShell title="Dashboard"><Overview /></DashboardShell>;
}

function Overview() {
  const { cases, loading, error } = useCaseData();
  const pending = cases.filter(record => record.status === "pending_approval").length;
  const approved = cases.filter(record => record.status === "approved").length;
  const cfo = cases.filter(record => record.status === "pending_cfo_approval").length;
  const recent = [...cases].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()).slice(0, 5);
  const stats = [
    { label: "Total cases", value: cases.length, icon: "▤", tone: "" },
    { label: "Pending approval", value: pending, icon: "◷", tone: "tone-amber" },
    { label: "Approved", value: approved, icon: "✓", tone: "tone-green" },
    { label: "Flagged for CFO review", value: cfo, icon: "⚑", tone: "tone-red" },
  ];

  return <main className="page-content">
    <div className="page-intro"><div><h2>Good to see you.</h2><p>Here’s what’s happening across your operations today.</p></div><span className="table-meta">Live overview · refreshes every 15 sec</span></div>
    {error && <div className="inline-error" role="alert">Backend unavailable. Dashboard data will appear as soon as FastAPI at 127.0.0.1:8000 is running. ({error})</div>}
    <p className="section-label">WORKFLOW OVERVIEW</p>
    <div className="stats-grid">{stats.map((stat, index) => <article className={`stat-card ${stat.tone}`} key={stat.label} style={{ animationDelay: `${index * 55}ms` }}><div className="stat-top">{stat.label}<span className="stat-icon">{stat.icon}</span></div><strong>{loading && !cases.length ? "—" : stat.value}</strong><div className="stat-sub">Across all processed cases</div></article>)}</div>
    <div className="overview-grid">
      <section className="panel"><div className="panel-header"><h3>Recent activity</h3><Link href="/dashboard/cases">View all cases →</Link></div><div className="activity-list">
        {recent.map(record => <Link className="activity-row" href="/dashboard/cases" key={record.case_id}><span className={`source-mark ${record.source_type === "request" ? "request" : ""}`}>{record.source_type === "document" ? "▤" : "“"}</span><span className="activity-main"><b>{record.item ?? "New case"}</b><small>{record.source_type === "document" ? "Document" : "Request"} · {record.case_id.slice(0, 12)}</small></span><StatusBadge status={record.status} /><span className="activity-time">{relativeTime(record.created_at)}</span></Link>)}
        {loading && !cases.length && <div className="loading-line">Loading recent activity…</div>}
        {!loading && !recent.length && <div className="empty-state">No activity yet. Submit a request or document to start a workflow.</div>}
      </div></section>
      <section className="panel"><div className="panel-header"><h3>Start a workflow</h3></div><div className="quick-actions">
        <Link href="/dashboard/submit?mode=request" className="action-tile"><span className="action-icon">“</span><span><b>Submit a request</b><small>Describe what your team needs</small></span><span className="action-arrow">↗</span></Link>
        <Link href="/dashboard/submit?mode=document" className="action-tile upload"><span className="action-icon">↑</span><span><b>Upload a document</b><small>Process an invoice or purchase order</small></span><span className="action-arrow">↗</span></Link>
      </div></section>
    </div>
  </main>;
}