from __future__ import annotations

from collections import defaultdict
from typing import Any

from .base import MemoryRecord, MemoryRetrieval, MemorySystem


class WorkingMemorySystem(MemorySystem):
    system_name = "m5-working"

    def __init__(self, capacity: int = 6) -> None:
        self.capacity = capacity
        self.window: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.archived: dict[str, list[dict[str, Any]]] = defaultdict(list)

    def add(self, record: MemoryRecord) -> None:
        item = {
            "id": record.id,
            "role": record.role,
            "content": record.content,
            "importance": self._importance(record.role, record.content),
            "metadata": record.metadata,
        }
        self.window[record.session_id].append(item)
        self.window[record.session_id].sort(key=lambda entry: entry["importance"], reverse=True)
        while len(self.window[record.session_id]) > self.capacity:
            self.archived[record.session_id].append(self.window[record.session_id].pop())

    def retrieve(self, query: str, session_id: str = "default", limit: int = 5) -> MemoryRetrieval:
        active = self.window[session_id][:limit]
        prompt_context = "\n".join(f"- ({item['importance']}) {item['content']}" for item in active)
        return MemoryRetrieval(self.system_name, prompt_context, active, self.inspect(session_id))

    def summarize(self, session_id: str = "default") -> dict[str, Any]:
        return {
            "session_id": session_id,
            "active_items": len(self.window[session_id]),
            "archived_items": len(self.archived[session_id]),
        }

    def clear(self, session_id: str | None = None) -> None:
        if session_id is None:
            self.window.clear()
            self.archived.clear()
            return
        self.window.pop(session_id, None)
        self.archived.pop(session_id, None)

    def inspect(self, session_id: str = "default") -> dict[str, Any]:
        return {"window": self.window[session_id], "archived": self.archived[session_id]}

    def _importance(self, role: str, content: str) -> int:
        score = 1
        lower = content.lower()
        if role == "assistant":
            score -= 1
        if "remember" in lower or "important" in lower:
            score += 3
        if any(char.isdigit() for char in content):
            score += 1
        if len(content.split()) > 12:
            score += 1
        return max(score, 0)
