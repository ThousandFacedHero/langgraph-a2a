"""Full A2A JSON-RPC round-trip tests through the FastAPI + A2A SDK stack."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from a2a_agent.a2a_server import create_app


def _build_send_message_payload(text: str, request_id: str = "test-1") -> dict:
    return {
        "jsonrpc": "2.0",
        "method": "SendMessage",
        "id": request_id,
        "params": {
            "message": {
                "role": "ROLE_USER",
                "parts": [{"text": text}],
                "messageId": f"msg-{request_id}",
            },
        },
    }


@pytest.fixture
def mock_llm_client():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Hello from the A2A agent!"

    mock_client = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
    return mock_client


@pytest.fixture
async def client(mock_llm_client):
    import a2a_agent.llm as llm_module

    original_client = llm_module._client
    llm_module._client = mock_llm_client

    try:
        app = create_app()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac
    finally:
        llm_module._client = original_client


@pytest.mark.asyncio
async def test_message_send_returns_completed_task_with_artifact(client):
    payload = _build_send_message_payload("Say hello")

    response = await client.post(
        "/",
        json=payload,
        headers={"A2A-Version": "1.0"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["jsonrpc"] == "2.0"
    assert data["id"] == "test-1"

    task = data["result"]["task"]

    assert task["status"]["state"] == "TASK_STATE_COMPLETED"

    artifacts = task.get("artifacts", [])
    assert len(artifacts) >= 1
    text_parts = [
        p["text"] for a in artifacts for p in a.get("parts", []) if "text" in p
    ]
    assert any("Hello from the A2A agent!" in t for t in text_parts)


@pytest.mark.asyncio
async def test_message_send_error_returns_failed_task(client, mock_llm_client):
    mock_llm_client.chat.completions.create = AsyncMock(
        side_effect=RuntimeError("LLM down"),
    )

    payload = _build_send_message_payload("This will fail", request_id="test-2")

    response = await client.post(
        "/",
        json=payload,
        headers={"A2A-Version": "1.0"},
    )

    assert response.status_code == 200
    data = response.json()
    task = data["result"]["task"]

    assert task["status"]["state"] == "TASK_STATE_FAILED"

    artifacts = task.get("artifacts", [])
    assert len(artifacts) >= 1
    text_parts = [
        p["text"] for a in artifacts for p in a.get("parts", []) if "text" in p
    ]
    assert any("LLM down" in t for t in text_parts)
