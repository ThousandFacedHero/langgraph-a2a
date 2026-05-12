import pytest

from a2a_agent.llm import chat_completion, get_client


@pytest.mark.asyncio
async def test_chat_completion_returns_content():
    result = await chat_completion([{"role": "user", "content": "Say just the word 'hello'"}])
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_chat_completion_passes_model_from_settings():
    from a2a_agent.config import settings

    result = await chat_completion([{"role": "user", "content": "Say just the word 'yes'"}])
    assert isinstance(result, str)
    assert len(result) > 0


def test_get_client_with_ssl_cert_file():
    import a2a_agent.llm as llm_mod

    llm_mod._client = None
    client = get_client()
    assert client is not None
    llm_mod._client = None


def test_get_client_without_ssl_cert_file(monkeypatch):
    monkeypatch.delenv("SSL_CERT_FILE", raising=False)

    import a2a_agent.llm as llm_mod

    llm_mod._client = None
    client = get_client()
    assert client is not None
    llm_mod._client = None
