from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import uuid


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def tokenize(text: str) -> set[str]:
    return {token.strip(".,!?;:()[]{}\"'").lower() for token in text.split() if token.strip()}


@dataclass
class MemoryRecord:
    role: str
    content: str
    session_id: str = "default"
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=utc_now)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class MemoryRetrieval:
    system: str
    prompt_context: str
    recalled: list[dict[str, Any]]
    state: dict[str, Any]


class MemorySystem(ABC):
    system_name = "base"

    @abstractmethod
    def add(self, record: MemoryRecord) -> None:
        raise NotImplementedError

    @abstractmethod
    def retrieve(self, query: str, session_id: str = "default", limit: int = 5) -> MemoryRetrieval:
        raise NotImplementedError

    @abstractmethod
    def summarize(self, session_id: str = "default") -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def clear(self, session_id: str | None = None) -> None:
        raise NotImplementedError

    @abstractmethod
    def inspect(self, session_id: str = "default") -> dict[str, Any]:
        raise NotImplementedError

