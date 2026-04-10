"use client";

import type { LLMConfig } from "../lib/api";

type SettingsDraft = {
  api_key: string;
  base_url: string;
  model: string;
  use_real_llm: boolean;
};

export function SettingsPanel({
  config,
  draft,
  onDraftChange,
  onSave,
  isSaving
}: {
  config: LLMConfig | null;
  draft: SettingsDraft;
  onDraftChange: (draft: SettingsDraft) => void;
  onSave: () => void;
  isSaving: boolean;
}) {
  return (
    <section className="panel">
      <div className="panel-header inline">
        <div>
          <h2>LLM Settings</h2>
          <p>Configure an OpenAI-compatible endpoint at runtime.</p>
        </div>
        <span className={`status-pill ${config?.enabled ? "live" : "local"}`}>
          {config?.enabled ? "Remote LLM" : "Local Fallback"}
        </span>
      </div>

      <div className="settings-grid">
        <label>
          Model
          <input
            value={draft.model}
            onChange={(event) => onDraftChange({ ...draft, model: event.target.value })}
            placeholder="gpt-4o-mini"
          />
        </label>
        <label>
          Base URL
          <input
            value={draft.base_url}
            onChange={(event) => onDraftChange({ ...draft, base_url: event.target.value })}
            placeholder="https://your-openai-compatible-endpoint/v1"
          />
        </label>
        <label className="wide">
          API Key
          <input
            value={draft.api_key}
            onChange={(event) => onDraftChange({ ...draft, api_key: event.target.value })}
            placeholder={config?.api_key || "sk-..."}
          />
        </label>
        <label className="toggle-row">
          <span>Use real LLM</span>
          <input
            type="checkbox"
            checked={draft.use_real_llm}
            onChange={(event) => onDraftChange({ ...draft, use_real_llm: event.target.checked })}
          />
        </label>
      </div>

      <div className="settings-footer">
        <button onClick={onSave} disabled={isSaving}>
          {isSaving ? "Saving..." : "Apply Settings"}
        </button>
        <div className="settings-meta">
          <span>Current key: {config?.api_key || "not set"}</span>
          <span>Last error: {config?.last_error || "none"}</span>
        </div>
      </div>
    </section>
  );
}
