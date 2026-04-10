const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

export type MemorySystemId =
  | "m1-short-long"
  | "m2-episodic"
  | "m3-semantic"
  | "m4-procedural"
  | "m5-working"
  | "m6-hierarchical";

export type LLMConfig = {
  api_key: string;
  base_url: string;
  model: string;
  use_real_llm: boolean;
  enabled: boolean;
  last_error: string | null;
};

export async function sendChat(system: MemorySystemId, sessionId: string, userMessage: string) {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ system, session_id: sessionId, user_message: userMessage })
  });
  if (!response.ok) {
    throw new Error(`Chat request failed: ${response.status}`);
  }
  return response.json();
}

export async function inspectMemory(system: MemorySystemId, sessionId: string) {
  const params = new URLSearchParams({ system, session_id: sessionId });
  const response = await fetch(`${API_BASE_URL}/memory/inspect?${params.toString()}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Inspect request failed: ${response.status}`);
  }
  return response.json();
}

export async function runBenchmark() {
  const response = await fetch(`${API_BASE_URL}/benchmark`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Benchmark request failed: ${response.status}`);
  }
  return response.json();
}

export async function getLLMConfig(): Promise<LLMConfig> {
  const response = await fetch(`${API_BASE_URL}/config/llm`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Config request failed: ${response.status}`);
  }
  return response.json();
}

export async function updateLLMConfig(payload: Partial<LLMConfig> & { api_key?: string }): Promise<LLMConfig> {
  const response = await fetch(`${API_BASE_URL}/config/llm`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    throw new Error(`Config update failed: ${response.status}`);
  }
  return response.json();
}

