from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


MemorySystemId = Literal[
    "m1-short-long",
    "m2-episodic",
    "m3-semantic",
    "m4-procedural",
    "m5-working",
    "m6-hierarchical",
]


class ChatRequest(BaseModel):
    system: MemorySystemId = "m1-short-long"
    session_id: str = "default"
    user_message: str = Field(..., min_length=1)


class ChatResponse(BaseModel):
    system: str
    session_id: str
    reply: str
    recalled: list[dict]
    summary: dict


class InspectResponse(BaseModel):
    system: str
    session_id: str
    state: dict


class LLMConfigResponse(BaseModel):
    api_key: str
    base_url: str
    model: str
    use_real_llm: bool
    enabled: bool
    last_error: str | None = None


class LLMConfigUpdateRequest(BaseModel):
    api_key: str | None = None
    base_url: str | None = None
    model: str | None = None
    use_real_llm: bool | None = None
