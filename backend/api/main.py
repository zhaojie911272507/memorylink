from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from api.chat import ChatRequest, ChatResponse, InspectResponse
from api.eval import BenchmarkResponse
from api.llm import LLMClient
from eval.benchmark import run_benchmark
from memory import (
    EpisodicMemorySystem,
    HierarchicalMemorySystem,
    MemoryRecord,
    ProceduralMemorySystem,
    SemanticMemorySystem,
    ShortLongMemorySystem,
    WorkingMemorySystem,
)


app = FastAPI(title="MemoryLink", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
llm_client = LLMClient()

SYSTEMS = {
    "m1-short-long": ShortLongMemorySystem(),
    "m2-episodic": EpisodicMemorySystem(),
    "m3-semantic": SemanticMemorySystem(),
    "m4-procedural": ProceduralMemorySystem(),
    "m5-working": WorkingMemorySystem(),
    "m6-hierarchical": HierarchicalMemorySystem(),
}


class ClearRequest(BaseModel):
    system: str
    session_id: str | None = None


def generate_reply(system_name: str, session_id: str, user_message: str) -> dict:
    system = SYSTEMS[system_name]
    system.add(MemoryRecord(role="user", content=user_message, session_id=session_id))
    retrieval = system.retrieve(user_message, session_id=session_id)
    reply = llm_client.generate_reply(system_name, user_message, retrieval.prompt_context)
    system.add(MemoryRecord(role="assistant", content=reply, session_id=session_id))
    return {
        "system": system_name,
        "session_id": session_id,
        "reply": reply,
        "recalled": retrieval.recalled,
        "summary": {**system.summarize(session_id), "llm_enabled": llm_client.enabled, "model": llm_client.model},
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> dict:
    return generate_reply(request.system, request.session_id, request.user_message)


@app.get("/memory/inspect", response_model=InspectResponse)
def inspect(system: str, session_id: str = "default") -> dict:
    return {"system": system, "session_id": session_id, "state": SYSTEMS[system].inspect(session_id)}


@app.post("/memory/clear")
def clear_memory(request: ClearRequest) -> dict[str, str]:
    SYSTEMS[request.system].clear(request.session_id)
    return {"status": "cleared"}


@app.get("/benchmark", response_model=BenchmarkResponse)
def benchmark() -> dict:
    return run_benchmark(SYSTEMS, generate_reply)
