import { DashboardShell } from "../../components/DashboardShell";

const rules = [
  { id: "cfo_threshold", name: "CFO approval threshold", condition: "price > 10,000", action: "Require CFO approval" },
  { id: "high_value_review", name: "High-value manual review", condition: "price > 30,000", action: "Flag for manual review" },
];

export default function PoliciesPage() {
  return <DashboardShell title="Policies"><main className="page-content"><div className="page-intro"><div><h2>Business policies</h2><p>Shared rules that guide approval and review decisions.</p></div><span className="status-badge status-approved">READ ONLY</span></div>
    <section className="panel table-panel"><table className="policy-table"><thead><tr><th>Rule</th><th>Condition</th><th>Action</th></tr></thead><tbody>{rules.map(rule => <tr key={rule.id}><td><span className="rule-name">{rule.name}</span><span className="rule-id">{rule.id}</span></td><td><code className="condition-code">{rule.condition}</code></td><td>{rule.action}</td></tr>)}</tbody></table></section>
    <p className="policy-note">Policy thresholds shown in INR. {/* Replace this local list with a real policy endpoint when the backend exposes one. */}Rules are currently configured in this frontend demo.</p>
  </main></DashboardShell>;
}