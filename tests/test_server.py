import pytest
from fastapi.testclient import TestClient

from a2a_agent.a2a_server import create_app


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)


def test_healthz(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readyz(client):
    response = client.get("/readyz")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_agent_card(client):
    response = client.get("/.well-known/agent-card.json")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "a2a-agent"
    assert len(data["skills"]) == 1
    assert data["skills"][0]["id"] == "chat"
