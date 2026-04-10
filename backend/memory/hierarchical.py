from __future__ import annotations

from collections import defaultdict
from typing import Any

from .base import MemoryRecord, MemoryRetrieval, MemorySystem


class HierarchicalMemorySystem(MemorySystem):
    system_name = "m6-hierarchical"

    def __init__(self) -> None:
        self.layers: dict[str, dict[str, Any]] = defaultdict(
            lambda: {"raw": [], "segment_summaries": [], "session_summary": "", "profile": ""}
        )

    def add(self, record: MemoryRecord) -> None:
        layer = self.layers[record.session_id]
        layer["raw"].append({"id": record.id, "role": record.role, "content": record.content})
        layer["segment_summaries"] = self._chunk(layer["raw"])
        layer["session_summary"] = " ".join(item["summary"] for item in layer["segment_summaries"])[-300:]
        layer["profile"] = self._profile(layer["raw"])

    def retrieve(self, query: str, session_id: str = "default", limit: int = 5) -> MemoryRetrieval:
        layer = self.layers[session_id]
        recalled = layer["segment_summaries"][:limit]
        prompt_context = "\n".join(
            [f"Profile: {layer['profile']}", f"Session: {layer['session_summary']}"]
            + [f"- {item['summary']}" for item in recalled]
        )
        return MemoryRetrieval(self.system_name, prompt_context, recalled, self.inspect(session_id))

    def summarize(self, session_id: str = "default") -> dict[str, Any]:
        layer = self.layers[session_id]
        return {
            "session_id": session_id,
            "segments": len(layer["segment_summaries"]),
            "session_summary": layer["session_summary"],
            "profile": layer["profile"],
        }

    def clear(self, session_id: str | None = None) -> None:
        if session_id is None:
            self.layers.clear()
            return
        self.layers.pop(session_id, None)

    def inspect(self, session_id: str = "default") -> dict[str, Any]:
        return self.layers[session_id]

    def _chunk(self, raw: list[dict[str, Any]]) -> list[dict[str, str]]:
        chunks = []
        for index in range(0, len(raw), 3):
            items = raw[index : index + 3]
            user_first = [item["content"] for item in items if item["role"] == "user"]
            assistant_next = [item["content"] for item in items if item["role"] != "user"]
            chunks.append({"summary": " ".join(user_first + assistant_next)[:180]})
        return chunks

    def _profile(self, raw: list[dict[str, Any]]) -> str:
        user_text = " ".join(item["content"] for item in raw if item["role"] == "user")
        if not user_text:
            return "No stable profile yet."
        return f"User profile focus: {user_text[:180]}"
