from __future__ import annotations

from collections import defaultdict
from typing import Any
import sqlite3

try:
    import networkx as nx
except Exception:  # pragma: no cover
    nx = None

from .base import MemoryRecord, MemoryRetrieval, MemorySystem


class SemanticMemorySystem(MemorySystem):
    system_name = "m3-semantic"

    def __init__(self) -> None:
        self.graphs: dict[str, Any] = defaultdict(self._make_graph)
        self.db = sqlite3.connect(":memory:", check_same_thread=False)
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS facts (session_id TEXT, subject TEXT, predicate TEXT, object TEXT, source_id TEXT)"
        )

    def add(self, record: MemoryRecord) -> None:
        facts = self._extract_facts(record.content)
        graph = self.graphs[record.session_id]
        for subject, predicate, obj in facts:
            if nx is not None:
                graph.add_edge(subject, obj, predicate=predicate, source_id=record.id)
            self.db.execute(
                "INSERT INTO facts (session_id, subject, predicate, object, source_id) VALUES (?, ?, ?, ?, ?)",
                (record.session_id, subject, predicate, obj, record.id),
            )
        self.db.commit()

    def retrieve(self, query: str, session_id: str = "default", limit: int = 5) -> MemoryRetrieval:
        tokens = [token for token in query.split() if token[:1].isupper()]
        facts: list[dict[str, Any]] = []
        for token in tokens:
            cursor = self.db.execute(
                "SELECT subject, predicate, object, source_id FROM facts WHERE session_id = ? AND (subject = ? OR object = ?) LIMIT ?",
                (session_id, token, token, limit),
            )
            for subject, predicate, obj, source_id in cursor.fetchall():
                facts.append(
                    {"subject": subject, "predicate": predicate, "object": obj, "source_id": source_id}
                )
        prompt_context = "\n".join(f"- {item['subject']} {item['predicate']} {item['object']}" for item in facts[:limit])
        return MemoryRetrieval(self.system_name, prompt_context, facts[:limit], self.inspect(session_id))

    def summarize(self, session_id: str = "default") -> dict[str, Any]:
        cursor = self.db.execute("SELECT COUNT(*) FROM facts WHERE session_id = ?", (session_id,))
        count = cursor.fetchone()[0]
        return {"session_id": session_id, "facts": count}

    def clear(self, session_id: str | None = None) -> None:
        if session_id is None:
            self.db.execute("DELETE FROM facts")
            self.graphs.clear()
            self.db.commit()
            return
        self.db.execute("DELETE FROM facts WHERE session_id = ?", (session_id,))
        self.graphs.pop(session_id, None)
        self.db.commit()

    def inspect(self, session_id: str = "default") -> dict[str, Any]:
        cursor = self.db.execute(
            "SELECT subject, predicate, object, source_id FROM facts WHERE session_id = ? LIMIT 25", (session_id,)
        )
        return {
            "facts": [
                {"subject": subject, "predicate": predicate, "object": obj, "source_id": source_id}
                for subject, predicate, obj, source_id in cursor.fetchall()
            ]
        }

    def _make_graph(self) -> Any:
        return nx.MultiDiGraph() if nx is not None else {"edges": []}

    def _extract_facts(self, content: str) -> list[tuple[str, str, str]]:
        words = [word.strip(".,") for word in content.split() if word.strip(".,")]
        if len(words) >= 3 and words[0][:1].isupper():
            return [(words[0], "related_to", " ".join(words[1:3]))]
        return []

