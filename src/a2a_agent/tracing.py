from __future__ import annotations

from a2a_agent.config import settings

_initialized = False


def init_tracing() -> None:
    """Enable Langfuse tracing by patching the OpenAI client.

    Call once at startup. When enabled, all OpenAI SDK calls are
    automatically traced via Langfuse's openai integration. When
    disabled, this is a no-op.
    """
    global _initialized
    if _initialized or not settings.langfuse_enabled:
        return

    import os

    os.environ.setdefault("LANGFUSE_PUBLIC_KEY", settings.langfuse_public_key)
    os.environ.setdefault("LANGFUSE_SECRET_KEY", settings.langfuse_secret_key)
    os.environ.setdefault("LANGFUSE_HOST", settings.langfuse_host)

    import langfuse.openai  # noqa: F401 — patches openai module on import

    _initialized = True
