"use client";

import { useEffect, useState, useTransition } from "react";

import { BenchmarkView } from "../components/BenchmarkView";
import { ChatWindow } from "../components/ChatWindow";
import { MemoryPanel } from "../components/MemoryPanel";
import { inspectMemory, MemorySystemId, runBenchmark, sendChat } from "../lib/api";

const SYSTEM_OPTIONS: Array<{ id: MemorySystemId; label: string }> = [
  { id: "m1-short-long", label: "M1 Short + Long" },
  { id: "m2-episodic", label: "M2 Episodic" },
  { id: "m3-semantic", label: "M3 Semantic" },
  { id: "m4-procedural", label: "M4 Procedural" },
  { id: "m5-working", label: "M5 Working" },
  { id: "m6-hierarchical", label: "M6 Hierarchical" }
];

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

export default function Page() {
  const [system, setSystem] = useState<MemorySystemId>("m1-short-long");
  const [sessionId, setSessionId] = useState("demo-session");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [memoryState, setMemoryState] = useState<unknown>({});
  const [summary, setSummary] = useState<unknown>({});
  const [benchmark, setBenchmark] = useState<{ systems: Array<Record<string, unknown>> } | null>(null);
  const [isSending, startSending] = useTransition();
  const [isRunningBenchmark, startBenchmark] = useTransition();

  async function refreshMemory(nextSystem: MemorySystemId, nextSessionId: string) {
    const state = await inspectMemory(nextSystem, nextSessionId);
    setMemoryState(state.state);
  }

  useEffect(() => {
    void refreshMemory(system, sessionId);
  }, [system, sessionId]);

  function onSubmit() {
    startSending(async () => {
      const userMessage = input.trim();
      if (!userMessage) {
        return;
      }
      setMessages((current) => [...current, { role: "user", content: userMessage }]);
      setInput("");
      const response = await sendChat(system, sessionId, userMessage);
      setMessages((current) => [...current, { role: "assistant", content: response.reply }]);
      setSummary(response.summary);
      setMemoryState((await inspectMemory(system, sessionId)).state);
    });
  }

  function onRunBenchmark() {
    startBenchmark(async () => {
      const report = await runBenchmark();
      setBenchmark(report);
    });
  }

  return (
    <main className="shell">
      <section className="hero">
        <div>
          <p className="eyebrow">MemoryLink</p>
          <h1>AI Memory Systems Lab</h1>
          <p className="lead">
            Compare six memory architectures across chat behavior, recall quality, and benchmark stability.
          </p>
        </div>
        <div className="controls">
          <label>
            Memory System
            <select value={system} onChange={(event) => setSystem(event.target.value as MemorySystemId)}>
              {SYSTEM_OPTIONS.map((option) => (
                <option key={option.id} value={option.id}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
          <label>
            Session ID
            <input value={sessionId} onChange={(event) => setSessionId(event.target.value)} />
          </label>
        </div>
      </section>

      <section className="grid">
        <ChatWindow
          messages={messages}
          input={input}
          onInputChange={setInput}
          onSubmit={onSubmit}
          isLoading={isSending}
        />
        <MemoryPanel system={system} sessionId={sessionId} memoryState={memoryState} summary={summary} />
      </section>

      <BenchmarkView benchmark={benchmark} onRefresh={onRunBenchmark} isLoading={isRunningBenchmark} />
    </main>
  );
}

