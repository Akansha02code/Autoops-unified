"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { CaseDataProvider, useCaseData } from "./CaseDataProvider";

const navItems = [
  { label: "Dashboard", href: "/dashboard", icon: "▦" },
  { label: "Cases", href: "/dashboard/cases", icon: "▤" },
  { label: "Submit", href: "/dashboard/submit", icon: "＋" },
  { label: "Pipeline", href: "/dashboard/pipeline", icon: "⌁" },
  { label: "Policies", href: "/dashboard/policies", icon: "◈" },
];

function ShellFrame({ children, title }: { children: React.ReactNode; title: string }) {
  const pathname = usePathname();
  const { refresh } = useCaseData();
  const [menuOpen, setMenuOpen] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  async function refreshData() { setRefreshing(true); await refresh(); setRefreshing(false); }

  return <div className="dashboard-shell">
    {menuOpen && <button className="mobile-scrim" aria-label="Close navigation" onClick={() => setMenuOpen(false)} />}
    <aside className={`sidebar ${menuOpen ? "open" : ""}`}>
      <div className="sidebar-brand"><Link className="brand" href="/"><span className="brand-mark">A</span> AutoOps</Link></div>
      <div className="workspace-switch"><span className="workspace-avatar">AO</span><span className="workspace-copy"><b>AutoOps workspace</b><small>Operations team</small></span><span className="workspace-chevron">⌄</span></div>
      <p className="nav-section">WORKSPACE</p>
      <nav className="nav-list">{navItems.map(item => {
        const active = item.href === "/dashboard" ? pathname === item.href : pathname.startsWith(item.href);
        return <Link key={item.href} href={item.href} onClick={() => setMenuOpen(false)} className={`nav-link ${active ? "active" : ""}`}><span className="nav-icon">{item.icon}</span>{item.label}</Link>;
      })}</nav>
      <div className="sidebar-bottom"><span className="avatar">AO</span><span className="user-copy"><b>Project workspace</b><small>Single-user demo</small></span><span className="workspace-chevron">···</span></div>
    </aside>
    <div className="main-area">
      <header className="topbar"><button className="icon-button mobile-menu" onClick={() => setMenuOpen(true)} aria-label="Open navigation">☰</button><h1>{title}</h1><span className="crumb">/ AutoOps</span><div className="topbar-right"><span className="sync-label">Synced automatically</span><button className="icon-button" onClick={() => void refreshData()} aria-label="Refresh cases" title="Refresh">{refreshing ? "…" : "↻"}</button></div></header>
      {children}
    </div>
  </div>;
}

export function DashboardShell({ children, title }: { children: React.ReactNode; title: string }) {
  return <CaseDataProvider><ShellFrame title={title}>{children}</ShellFrame></CaseDataProvider>;
}