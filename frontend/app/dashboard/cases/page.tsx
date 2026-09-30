"use client";

import { useState } from "react";
import { DashboardShell } from "../../components/DashboardShell";
import { CaseTable } from "../../components/CaseTable";

export default function CasesPage() {
  const [toast, setToast] = useState<{ message: string; error: boolean } | null>(null);
  function notify(message: string, error = false) { setToast({ message, error }); window.setTimeout(() => setToast(null), 3600); }
  return <DashboardShell title="Cases"><main className="page-content"><div className="page-intro"><div><h2>Case management</h2><p>Review submissions, resolve policy checks, and move work forward.</p></div></div><CaseTable onNotify={notify} />{toast && <div className={`toast ${toast.error ? "error" : ""}`} role="status">{toast.message}</div>}</main></DashboardShell>;
}