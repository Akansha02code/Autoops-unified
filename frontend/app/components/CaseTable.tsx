"use client";

import { useMemo, useState } from "react";
import { CaseRecord, formatINR, postAction } from "../lib/api";
import { StatusBadge } from "./StatusBadge";
import { useCaseData } from "./CaseDataProvider";

export function CaseTable({ onNotify }: { onNotify: (message: string, error?: boolean) => void }) {
  const { cases, loading, error, refresh } = useCaseData();
  const [filter, setFilter] = useState("all");
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<CaseRecord | null>(null);
  const [busy, setBusy] = useState("");
  const visible = useMemo(() => cases.filter(record => {
    const matchesStatus = filter === "all" || record.status === filter;
    const term = search.toLowerCase();
    return matchesStatus && (!term || `${record.item ?? ""} ${record.case_id} ${record.requester ?? ""}`.toLowerCase().includes(term));
  }), [cases, filter, search]);

  async function action(record: CaseRecord, kind: "approve" | "reject" | "generate-invoice") {
    setBusy(`${record.case_id}:${kind}`);
    try {
      const payload = kind === "approve" ? { approved_by: "AutoOps User" } : undefined;
      await postAction(`/cases/${encodeURIComponent(record.case_id)}/${kind}`, payload);
      onNotify(kind === "generate-invoice" ? "Invoice generated successfully." : `Case ${kind === "approve" ? "approved" : "rejected"}.`);
      setSelected(null);
      await refresh();
    } catch (reason) { onNotify(reason instanceof Error ? reason.message : "Action failed.", true); }
    finally { setBusy(""); }
  }

  return <>
    {error && <div className="inline-error" role="alert">Can’t connect to the AutoOps backend. Start the FastAPI service at 127.0.0.1:8000, then refresh. ({error})</div>}
    <section className="panel table-panel">
      <div className="panel-header"><h3>Case records <span className="table-meta">{loading ? "Loading" : `${visible.length} shown`}</span></h3><div className="table-toolbar"><input className="search-input" value={search} onChange={event => setSearch(event.target.value)} placeholder="Search cases…" aria-label="Search cases" /><select className="filter-select" value={filter} onChange={event => setFilter(event.target.value)} aria-label="Filter cases by status"><option value="all">All statuses</option><option value="pending_approval">Pending</option><option value="pending_cfo_approval">CFO review</option><option value="approved">Approved</option><option value="rejected">Rejected</option></select></div></div>
      {loading && cases.length === 0 ? <div className="loading-line">Loading cases…</div> : <div className="case-table-wrap"><table className="case-table"><thead><tr><th>Source</th><th>Item</th><th>Qty</th><th>Price</th><th>Status</th><th>Policy flags</th><th>Actions</th></tr></thead><tbody>
        {visible.map(record => <tr className="case-row" key={record.case_id} onClick={() => setSelected(record)}>
          <td><div className="source-cell"><span className={`source-mark ${record.source_type === "request" ? "request" : ""}`}>{record.source_type === "document" ? "▤" : "“"}</span>{record.source_type === "document" ? "Document" : "Request"}</div></td>
          <td className="item-cell">{record.item ?? "Unclassified item"}<small>{record.department ?? "No department"}</small></td><td>{record.quantity ?? "—"}</td>
          <td className="price-cell">{formatINR(record.price)}{record.original_currency && record.original_price != null && <small>{record.original_currency} {record.original_price.toLocaleString()}</small>}</td>
          <td><StatusBadge status={record.status} /></td><td>{record.policy_flags?.length ? record.policy_flags.map(flag => <span className="flag-pill" key={`${flag.rule_id}-${flag.action}`} title={flag.action}>{flag.rule_id}</span>) : <span className="table-meta">—</span>}</td>
          <td onClick={event => event.stopPropagation()}><div className="row-actions">{record.status.startsWith("pending") && <><button className="small-button approve" disabled={!!busy} onClick={() => void action(record, "approve")}>Approve</button><button className="small-button reject" disabled={!!busy} onClick={() => void action(record, "reject")}>Reject</button></>}{record.status === "approved" && <button className="small-button invoice" disabled={!!busy} onClick={() => void action(record, "generate-invoice")}>Generate invoice</button>}</div></td>
        </tr>)}
        {!visible.length && <tr><td colSpan={7} className="empty-state">{error ? "No cases available while the backend is offline." : "No cases match this filter."}</td></tr>}
      </tbody></table></div>}
    </section>
    {selected && <div className="drawer-backdrop" onMouseDown={event => { if (event.target === event.currentTarget) setSelected(null); }}><aside className="detail-drawer" role="dialog" aria-modal="true" aria-label="Case details">
      <div className="drawer-title"><div><h3>{selected.item ?? "Case details"}</h3><small>{selected.case_id}</small></div><button className="icon-button" onClick={() => setSelected(null)} aria-label="Close details">×</button></div>
      <StatusBadge status={selected.status} />
      <div className="drawer-section">CASE INFORMATION</div><div className="drawer-fields">
        <Field label="Case ID" value={selected.case_id} full /><Field label="Source" value={selected.source_type} /><Field label="Requester" value={selected.requester} /><Field label="Item" value={selected.item} /><Field label="Quantity" value={selected.quantity} /><Field label="Department" value={selected.department} /><Field label="Price (INR)" value={formatINR(selected.price)} /><Field label="Original price" value={selected.original_price != null ? `${selected.original_currency ?? "INR"} ${selected.original_price}` : null} /><Field label="Approved by" value={selected.approved_by} /><Field label="Created at" value={new Date(selected.created_at).toLocaleString()} full />
      </div>
      <div className="drawer-section">POLICY FLAGS</div>{selected.policy_flags?.length ? selected.policy_flags.map(flag => <div key={flag.rule_id} className="activity-row"><span className="flag-pill">{flag.rule_id}</span><span className="table-meta">{flag.action}</span></div>) : <span className="table-meta">No policy flags</span>}
      {selected.status.startsWith("pending") && <div className="drawer-actions"><button className="button button-primary" disabled={!!busy} onClick={() => void action(selected, "approve")}>Approve case</button><button className="small-button reject" disabled={!!busy} onClick={() => void action(selected, "reject")}>Reject</button></div>}
      {selected.status === "approved" && <div className="drawer-actions"><button className="button button-primary" disabled={!!busy} onClick={() => void action(selected, "generate-invoice")}>Generate invoice</button></div>}
    </aside></div>}
  </>;
}

function Field({ label, value, full = false }: { label: string; value: unknown; full?: boolean }) {
  return <div className={`drawer-field ${full ? "full" : ""}`}><span>{label}</span><b>{value == null || value === "" ? "—" : String(value)}</b></div>;
}