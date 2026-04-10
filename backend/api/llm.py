from __future__ import annotations

import os

from openai import OpenAI
from openai import OpenAIError


class LLMClient:
    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.model = os.getenv("MEMORYLINK_MODEL", "gpt-4o-mini")
        self.use_real_llm = os.getenv("MEMORYLINK_USE_REAL_LLM", "true").lower() == "true"
        self.last_error: str | None = None
        self._client = OpenAI(api_key=self.api_key) if self.api_key and self.use_real_llm else None

    @property
    def enabled(self) -> bool:
        return self._client is not None

    def generate_reply(self, system_name: str, user_message: str, memory_context: str) -> str:
        if not self._client:
            return self._fallback_reply(system_name, memory_context)

        instructions = (
            "You are part of the MemoryLink lab. Answer the user naturally, but stay grounded in the supplied "
            "memory context. If memory context is empty, answer directly without inventing prior facts."
        )
        try:
            response = self._client.responses.create(
                model=self.model,
                input=[
                    {"role": "system", "content": instructions},
                    {
                        "role": "system",
                        "content": f"Memory system: {system_name}\nMemory context:\n{memory_context or 'No prior memory.'}",
                    },
                    {"role": "user", "content": user_message},
                ],
            )
            return response.output_text.strip()
        except OpenAIError as exc:
            self.last_error = exc.__class__.__name__
            self._client = None
            return self._fallback_reply(system_name, memory_context)

    def _fallback_reply(self, system_name: str, memory_context: str) -> str:
        return (
            f"[{system_name}] I retained context for this turn. "
            f"Key context: {memory_context or 'No prior memory.'}"
        )
