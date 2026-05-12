from __future__ import annotations

import os
import ssl

import httpx
from openai import AsyncOpenAI

from a2a_agent.config import settings

_client: AsyncOpenAI | None = None


def get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        ca_bundle = os.environ.get("SSL_CERT_FILE")
        ssl_ctx = ssl.create_default_context(cafile=ca_bundle) if ca_bundle else None
        http_client = httpx.AsyncClient(verify=ssl_ctx) if ssl_ctx else None
        _client = AsyncOpenAI(http_client=http_client)
    return _client


async def chat_completion(messages: list[dict], **kwargs) -> str:
    response = await get_client().chat.completions.create(
        model=settings.llm_model,
        messages=messages,
        **kwargs,
    )
    return response.choices[0].message.content
