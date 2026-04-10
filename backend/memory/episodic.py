from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Any

from .base import MemoryRecord, MemoryRetrieval, MemorySystem, tokenize


class EpisodicMemorySystem(MemorySystem):
    system_name = "m2-episodic"

    def __init__(self) -> None:
        self.episodes: dict[str, list[dict[str, Any]]] = defaultdict(list)

    def add(self, record: MemoryRecord) -> None:
        emotion = self._infer_emotion(record.content)
        entities = self._extract_entities(record.content)
        self.episodes[record.session_id].append(
            {
                "id": record.id,
                "timestamp": record.created_at.isoformat(),
                "role": record.role,
                "content": record.content,
                "emotion": emotion,
                "entities": entities,
                "metadata": record.metadata,
            }
        )

    def retrieve(self, query: str, session_id: str = "default", limit: int = 5) -> MemoryRetrieval:
        query_tokens = tokenize(query)
        ranked = []
        for event in self.episodes[session_id]:
            content_score = len(query_tokens & tokenize(event["content"]))
            entity_score = len(query_tokens & {entity.lower() for entity in event["entities"]})
            timestamp = datetime.fromisoformat(event["timestamp"]).timestamp()
            ranked.append((content_score * 2 + entity_score, timestamp, event))
        ranked.sort(key=lambda item: (item[0], item[1]), reverse=True)
        recalled = [item[2] for item in ranked[:limit]]
        prompt_context = "\n".join(
            f"- [{entry['emotion']}] {entry['timestamp']}: {entry['content']}" for entry in recalled
        )
        return MemoryRetrieval(self.system_name, prompt_context, recalled, self.inspect(session_id))

    def summarize(self, session_id: str = "default") -> dict[str, Any]:
        events = self.episodes[session_id]
        return {
            "session_id": session_id,
            "episodes": len(events),
            "dominant_emotions": sorted([event["emotion"] for event in events])[-5:],
        }

    def clear(self, session_id: str | None = None) -> None:
        if session_id is None:
            self.episodes.clear()
            return
        self.episodes.pop(session_id, None)

    def inspect(self, session_id: str = "default") -> dict[str, Any]:
        return {"episodes": self.episodes[session_id]}

    def _infer_emotion(self, content: str) -> str:
        lower = content.lower()
        if any(word in lower for word in ["love", "great", "happy", "excited"]):
            return "positive"
        if any(word in lower for word in ["sad", "angry", "upset", "frustrated"]):
            return "negative"
        return "neutral"

    def _extract_entities(self, content: str) -> list[str]:
        return [word.strip(".,") for word in content.split() if word[:1].isupper()]

