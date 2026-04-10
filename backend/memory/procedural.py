from __future__ import annotations

from collections import defaultdict
from typing import Any

from .base import MemoryRecord, MemoryRetrieval, MemorySystem


class ProceduralMemorySystem(MemorySystem):
    system_name = "m4-procedural"

    def __init__(self) -> None:
        self.rules: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.records: dict[str, list[dict[str, Any]]] = defaultdict(list)

    def add(self, record: MemoryRecord) -> None:
        self.records[record.session_id].append(
            {"id": record.id, "role": record.role, "content": record.content, "metadata": record.metadata}
        )
        if record.role != "user":
            return
        rule = self._distill_rule(record.content)
        if rule and rule not in self.rules[record.session_id]:
            self.rules[record.session_id].append(rule)

    def retrieve(self, query: str, session_id: str = "default", limit: int = 5) -> MemoryRetrieval:
        selected_rules = self._rank_rules(query, self.rules[session_id])[:limit]
        prompt_context = "\n".join(f"- {rule['type']}: {rule['value']}" for rule in selected_rules)
        return MemoryRetrieval(self.system_name, prompt_context, selected_rules, self.inspect(session_id))

    def summarize(self, session_id: str = "default") -> dict[str, Any]:
        return {
            "session_id": session_id,
            "rules": len(self.rules[session_id]),
            "recent_rules": self.rules[session_id][-5:],
        }

    def clear(self, session_id: str | None = None) -> None:
        if session_id is None:
            self.rules.clear()
            self.records.clear()
            return
        self.rules.pop(session_id, None)
        self.records.pop(session_id, None)

    def inspect(self, session_id: str = "default") -> dict[str, Any]:
        return {"rules": self.rules[session_id], "records": self.records[session_id][-10:]}

    def _distill_rule(self, content: str) -> dict[str, Any] | None:
        lower = content.lower()
        if "prefer" in lower or "like" in lower:
            return {"type": "preference", "value": content[:160]}
        if "always" in lower or "never" in lower:
            return {"type": "instruction", "value": content[:160]}
        return None

    def _rank_rules(self, query: str, rules: list[dict[str, Any]]) -> list[dict[str, Any]]:
        query_terms = {term.lower() for term in query.split()}
        ranked = sorted(
            rules,
            key=lambda rule: (
                len(query_terms & {term.lower() for term in rule["value"].split()}),
                rule["type"] == "instruction",
            ),
            reverse=True,
        )
        return ranked or rules
