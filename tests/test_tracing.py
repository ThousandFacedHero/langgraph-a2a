from unittest.mock import patch, MagicMock


def test_init_tracing_disabled_is_noop(monkeypatch):
    monkeypatch.setenv("LANGFUSE_ENABLED", "false")

    from a2a_agent.config import Settings

    settings = Settings(_env_file=None)

    with patch("a2a_agent.tracing.settings", settings):
        import a2a_agent.tracing as tracing_mod

        tracing_mod._initialized = False
        tracing_mod.init_tracing()

    assert tracing_mod._initialized is False


def test_init_tracing_enabled_imports_langfuse_openai(monkeypatch):
    monkeypatch.setenv("LANGFUSE_ENABLED", "true")
    monkeypatch.setenv("LANGFUSE_PUBLIC_KEY", "pk-test")
    monkeypatch.setenv("LANGFUSE_SECRET_KEY", "sk-test")
    monkeypatch.setenv("LANGFUSE_HOST", "http://localhost:3000")

    from a2a_agent.config import Settings

    settings = Settings(_env_file=None)

    mock_langfuse_openai = MagicMock()

    with patch("a2a_agent.tracing.settings", settings):
        import a2a_agent.tracing as tracing_mod

        tracing_mod._initialized = False

        with patch.dict("sys.modules", {"langfuse.openai": mock_langfuse_openai}):
            tracing_mod.init_tracing()

    assert tracing_mod._initialized is True
