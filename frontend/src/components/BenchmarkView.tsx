"use client";

export function BenchmarkView({
  benchmark,
  onRefresh,
  isLoading
}: {
  benchmark: { systems: Array<Record<string, unknown>> } | null;
  onRefresh: () => void;
  isLoading: boolean;
}) {
  return (
    <section className="panel">
      <div className="panel-header inline">
        <div>
          <h2>Benchmark</h2>
          <p>Cross-session comparison of the six memory engines.</p>
        </div>
        <button onClick={onRefresh} disabled={isLoading}>
          {isLoading ? "Running..." : "Run benchmark"}
        </button>
      </div>
      {!benchmark ? (
        <p className="empty">No benchmark report loaded.</p>
      ) : (
        <div className="benchmark-list">
          {benchmark.systems.map((item, index) => {
            const system = item.system as string;
            const weightedScore = item.weighted_score as number;
            return (
              <article key={`${system}-${index}`} className="benchmark-card">
                <div className="score">{weightedScore.toFixed(2)}</div>
                <div>
                  <h3>{system}</h3>
                  <pre>{JSON.stringify(item.dimensions, null, 2)}</pre>
                </div>
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}

