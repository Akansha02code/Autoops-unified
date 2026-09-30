export type PolicyFlag = { rule_id: string; action: string };
export type CaseRecord = {
  case_id: string;
  source_type: "document" | "request";
  item: string | null;
  quantity: number | null;
  department: string | null;
  price: number | null;
  original_currency: string | null;
  original_price: number | null;
  requester: string | null;
  status: string;
  policy_flags: PolicyFlag[];
  created_at: string;
  approved_by: string | null;
};

export const API_BASE = "/api/backend";

export async function fetchCases(): Promise<CaseRecord[]> {
  const response = await fetch(`${API_BASE}/cases`, { cache: "no-store" });
  if (!response.ok) throw new Error(`Backend responded with ${response.status}`);
  const data: unknown = await response.json();
  if (!Array.isArray(data)) throw new Error("Unexpected response from /cases");
  return data as CaseRecord[];
}

export async function postAction(path: string, body?: unknown): Promise<any> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: body === undefined ? undefined : { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try { const data = await response.json(); detail = data.detail ?? detail; } catch { /* response may not be JSON */ }
    throw new Error(detail);
  }
  const text = await response.text();
  return text ? JSON.parse(text) : {};
}

export function formatINR(value: number | null | undefined): string {
  if (value == null) return "—";
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 2 }).format(value);
}

export function relativeTime(value: string): string {
  const elapsed = Math.max(0, Date.now() - new Date(value).getTime());
  if (!Number.isFinite(elapsed)) return "Unknown time";
  const minutes = Math.floor(elapsed / 60000);
  if (minutes < 1) return "Just now";
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return days < 30 ? `${days}d ago` : new Date(value).toLocaleDateString();
}