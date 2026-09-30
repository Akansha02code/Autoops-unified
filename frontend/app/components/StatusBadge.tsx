import { CaseRecord } from "../lib/api";

export function StatusBadge({ status }: { status: CaseRecord["status"] }) {
  const labels: Record<string, string> = {
    pending_approval: "Pending approval",
    pending_cfo_approval: "CFO review",
    approved: "Approved",
    rejected: "Rejected",
  };
  const classes: Record<string, string> = {
    pending_approval: "status-pending",
    pending_cfo_approval: "status-cfo",
    approved: "status-approved",
    rejected: "status-rejected",
  };
  return <span className={`status-badge ${classes[status] ?? "status-unknown"}`}>{labels[status] ?? status.replaceAll("_", " ")}</span>;
}