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

