import pytest


def test_settings_loads_from_env(monkeypatch):
    monkeypatch.setenv("LLM_MODEL", "test-model")
    monkeypatch.setenv("AGENT_NAME", "test-agent")
    monkeypatch.setenv("AGENT_PORT", "9000")
    monkeypatch.setenv("LANGFUSE_ENABLED", "false")

    from a2a_agent.config import Settings

    s = Settings(_env_file=None)
    assert s.llm_model == "test-model"
    assert s.agent_name == "test-agent"
    assert s.agent_port == 9000
    assert s.langfuse_enabled is False


def test_settings_defaults(monkeypatch):
    monkeypatch.delenv("LLM_MODEL", raising=False)
    monkeypatch.delenv("AGENT_PORT", raising=False)
    monkeypatch.delenv("LANGFUSE_ENABLED", raising=False)
    monkeypatch.delenv("AGENT_NAME", raising=False)

    from a2a_agent.config import Settings

    s = Settings(_env_file=None)
    assert s.agent_port == 8000
    assert s.langfuse_enabled is False
    assert s.llm_model == "llama3"
