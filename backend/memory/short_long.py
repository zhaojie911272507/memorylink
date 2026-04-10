from __future__ import annotations

from collections import defaultdict, deque
from typing import Any

from .base import MemoryRecord, MemoryRetrieval, MemorySystem, tokenize


class ShortLongMemorySystem(MemorySystem):
    system_name = "m1-short-long"

    def __init__(self, short_window: int = 8) -> None:
        self.short_window = short_window
        self.short_term: dict[str, deque[MemoryRecord]] = defaultdict(lambda: deque(maxlen=self.short_window))
        self.long_term: dict[str, list[dict[str, Any]]] = defaultdict(list)

    def add(self, record: MemoryRecord) -> None:
        session_buffer = self.short_term[record.session_id]
        session_buffer.append(record)
        if len(session_buffer) >= self.short_window:
            self.long_term[record.session_id].append(
                {
                    "summary": self._summarize_records(list(session_buffer)[-4:]),
                    "source_ids": [item.id for item in list(session_buffer)[-4:]],
                }
            )

    def retrieve(self, query: str, session_id: str = "default", limit: int = 5) -> MemoryRetrieval:
        short_matches = [self._serialize(record) for record in self.short_term[session_id]]
        scored_long = []
        query_tokens = tokenize(query)
        for chunk in self.long_term[session_id]:
            score = len(query_tokens & tokenize(chunk["summary"]))
            scored_long.append((score, chunk))
        scored_long.sort(key=lambda item: item[0], reverse=True)
        recalled = short_matches[-limit:] + [item[1] for item in scored_long[: max(0, limit - len(short_matches[-limit:]))]]
        prompt_context = "\n".join(
            f"- {entry.get('role', 'memory')}: {entry.get('content') or entry.get('summary')}" for entry in recalled
        )
        return MemoryRetrieval(
            system=self.system_name,
            prompt_context=prompt_context,
            recalled=recalled,
            state=self.inspect(session_id),
        )

    def summarize(self, session_id: str = "default") -> dict[str, Any]:
        return {
            "session_id": session_id,
            "short_summary": self._summarize_records(list(self.short_term[session_id])),
            "long_term_items": len(self.long_term[session_id]),
        }

    def clear(self, session_id: str | None = None) -> None:
        if session_id is None:
            self.short_term.clear()
            self.long_term.clear()
            return
        self.short_term.pop(session_id, None)
        self.long_term.pop(session_id, None)

    def inspect(self, session_id: str = "default") -> dict[str, Any]:
        return {
            "short_window": self.short_window,
            "short_term": [self._serialize(record) for record in self.short_term[session_id]],
            "long_term": self.long_term[session_id],
        }

    def _summarize_records(self, records: list[MemoryRecord]) -> str:
        if not records:
            return ""
        text = " ".join(record.content for record in records)
        return text[:240]

    def _serialize(self, record: MemoryRecord) -> dict[str, Any]:
        return {
            "id": record.id,
            "role": record.role,
            "content": record.content,
            "created_at": record.created_at.isoformat(),
            "metadata": record.metadata,
        }

