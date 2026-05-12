from unittest.mock import AsyncMock, patch, MagicMock
import pytest


@pytest.mark.asyncio
async def test_graph_invoke_returns_output():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "The capital is Paris."

    mock_client = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    with patch("a2a_agent.llm.get_client", return_value=mock_client):
        from a2a_agent.graph import build_graph

        graph = build_graph()
        result = await graph.ainvoke(
            {"input": "What is the capital of France?", "output": "", "error": None},
            config={"configurable": {"thread_id": "test-1"}},
        )

    assert result["output"] == "The capital is Paris."
    assert result["error"] is None
