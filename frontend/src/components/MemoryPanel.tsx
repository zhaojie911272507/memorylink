"use client";

export function MemoryPanel({
  system,
  sessionId,
  memoryState,
  summary
}: {
  system: string;
  sessionId: string;
  memoryState: unknown;
  summary: unknown;
}) {
  return (
    <section className="panel">
      <div className="panel-header">
        <h2>Memory State</h2>
        <p>{system} / session {sessionId}</p>
      </div>
      <div className="state-grid">
        <div>
          <h3>Summary</h3>
          <pre>{JSON.stringify(summary, null, 2)}</pre>
        </div>
        <div>
          <h3>Inspectable State</h3>
          <pre>{JSON.stringify(memoryState, null, 2)}</pre>
        </div>
      </div>
    </section>
  );
}

