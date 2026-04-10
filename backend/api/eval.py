from __future__ import annotations

from pydantic import BaseModel


class BenchmarkResponse(BaseModel):
    systems: list[dict]

