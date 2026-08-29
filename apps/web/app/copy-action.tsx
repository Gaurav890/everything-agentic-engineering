"use client";

import {useState} from "react";

export function CopyAction({text, label, destination}: {text: string; label: string; destination: "terminal" | "assistant"}) {
  const [status, setStatus] = useState("");
  const [pending, setPending] = useState(false);
  async function copy() {
    setPending(true);
    setStatus("Copying…");
    try {
      await navigator.clipboard.writeText(text);
      setStatus(destination === "terminal" ? "Copied. Paste it in this project’s terminal." : "Copied. Paste it in your assistant’s conversation.");
    } catch {
      setStatus("Copy is unavailable. Select and copy the text shown on this page.");
    } finally {
      setPending(false);
    }
  }
  return <>
    <button type="button" onClick={copy} disabled={pending}>{pending ? "Copying…" : label}</button>
    <span role="status" aria-live="polite">{status}</span>
  </>;
}
