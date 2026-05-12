from __future__ import annotations

from typing import TypedDict


class AgentState(TypedDict):
    input: str
    output: str
    error: str | None
