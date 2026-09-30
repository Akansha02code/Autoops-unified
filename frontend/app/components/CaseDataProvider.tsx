"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { CaseRecord, fetchCases } from "../lib/api";

type CaseData = { cases: CaseRecord[]; loading: boolean; error: string; refresh: () => Promise<void> };
const Context = createContext<CaseData | null>(null);

export function CaseDataProvider({ children }: { children: React.ReactNode }) {
  const [cases, setCases] = useState<CaseRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const refresh = useCallback(async () => {
    try { setCases(await fetchCases()); setError(""); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Could not reach the AutoOps API."); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => {
    void refresh();
    const timer = window.setInterval(() => void refresh(), 15000);
    return () => window.clearInterval(timer);
  }, [refresh]);

  return <Context.Provider value={{ cases, loading, error, refresh }}>{children}</Context.Provider>;
}

export function useCaseData() {
  const context = useContext(Context);
  if (!context) throw new Error("useCaseData must be used inside CaseDataProvider");
  return context;
}