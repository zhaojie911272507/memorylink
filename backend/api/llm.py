from __future__ import annotations

import os
from typing import Any

from openai import OpenAI
from openai import OpenAIError


class LLMClient:
    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.base_url = os.getenv("OPENAI_BASE_URL", "").strip() or os.getenv("OPENAI_API_BASE", "").strip() or None
        self.model = os.getenv("MEMORYLINK_MODEL", "gpt-4o-mini")
        self.use_real_llm = os.getenv("MEMORYLINK_USE_REAL_LLM", "true").lower() == "true"
        self.last_error: str | None = None
        self._client = None
        self._refresh_client()

    @property
    def enabled(self) -> bool:
        return self._client is not None

    def snapshot(self) -> dict[str, Any]:
        return {
            "api_key": self._mask_api_key(self.api_key),
            "base_url": self.base_url or "",
            "model": self.model,
            "use_real_llm": self.use_real_llm,
            "enabled": self.enabled,
            "last_error": self.last_error,
        }

    def update_config(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        use_real_llm: bool | None = None,
    ) -> dict[str, Any]:
        if api_key is not None:
            self.api_key = api_key.strip()
        if base_url is not None:
            self.base_url = base_url.strip() or None
        if model is not None:
            self.model = model.strip() or "gpt-4o-mini"
        if use_real_llm is not None:
            self.use_real_llm = use_real_llm
        self.last_error = None
        self._refresh_client()
        return self.snapshot()

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

    def _refresh_client(self) -> None:
        self._client = OpenAI(api_key=self.api_key, base_url=self.base_url) if self.api_key and self.use_real_llm else None

    def _mask_api_key(self, api_key: str) -> str:
        if not api_key:
            return ""
        if len(api_key) <= 8:
            return "*" * len(api_key)
        return f"{api_key[:6]}...{api_key[-4:]}"
