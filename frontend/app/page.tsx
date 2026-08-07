"use client";
import { useState } from "react";

export default function Home() {
  const [status, setStatus] = useState<string>("not checked yet");
  const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

  async function checkBackend() {
    try {
      const res = await fetch(`${apiBase}/health`);
      if (!res.ok) {
        throw new Error(`backend responded with ${res.status}`);
      }
      const data = await res.json();
      setStatus(JSON.stringify(data));
    } catch (e) {
      const msg = e instanceof Error ? e.message : "unknown error";
      setStatus(`backend not reachable (${msg})`);
    }
  }

  return (
    <main style={{ padding: 40, fontFamily: "sans-serif" }}>
      <h1>AutoOps - Day 1 skeleton</h1>
      <button onClick={checkBackend}>Check backend health</button>
      <p>Status: {status}</p>
    </main>
  );
}
