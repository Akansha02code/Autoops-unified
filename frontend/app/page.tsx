"use client";
import { useState } from "react";

export default function Home() {
  const [status, setStatus] = useState<string>("not checked yet");

  async function checkBackend() {
    try {
      const res = await fetch("http://localhost:8000/health");
      const data = await res.json();
      setStatus(JSON.stringify(data));
    } catch (e) {
      setStatus("backend not reachable - is uvicorn running on :8000?");
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
