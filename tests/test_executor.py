from unittest.mock import AsyncMock, patch, MagicMock
import pytest
from a2a.types import Part, Message, TaskState


@pytest.mark.asyncio
async def test_executor_invokes_graph_and_emits_artifact_and_completed():
    mock_graph = AsyncMock()
    mock_graph.ainvoke = AsyncMock(return_value={
        "input": "hello", "output": "world", "error": None
    })

    with patch("a2a_agent.executor.graph", mock_graph):
        from a2a_agent.executor import A2AAgentExecutor

        executor = A2AAgentExecutor()

        context = MagicMock()
        context.message = Message(parts=[Part(text="hello")])
        context.task_id = "test-task-id"
        context.context_id = "test-context-id"

        event_queue = AsyncMock()
        event_queue.enqueue_event = AsyncMock()

        await executor.execute(context, event_queue)

    mock_graph.ainvoke.assert_called_once()
    assert event_queue.enqueue_event.call_count == 2

    artifact_event = event_queue.enqueue_event.call_args_list[0][0][0]
    assert artifact_event.task_id == "test-task-id"
    assert artifact_event.last_chunk is True
    assert artifact_event.artifact.parts[0].text == "world"

    status_event = event_queue.enqueue_event.call_args_list[1][0][0]
    assert status_event.task_id == "test-task-id"
    assert status_event.status.state == TaskState.TASK_STATE_COMPLETED


@pytest.mark.asyncio
async def test_executor_handles_graph_error():
    mock_graph = AsyncMock()
    mock_graph.ainvoke = AsyncMock(side_effect=RuntimeError("LLM connection failed"))

    with patch("a2a_agent.executor.graph", mock_graph):
        from a2a_agent.executor import A2AAgentExecutor

        executor = A2AAgentExecutor()

        context = MagicMock()
        context.message = Message(parts=[Part(text="hello")])
        context.task_id = "test-task-id"
        context.context_id = "test-context-id"

        event_queue = AsyncMock()
        event_queue.enqueue_event = AsyncMock()

        await executor.execute(context, event_queue)

    assert event_queue.enqueue_event.call_count == 2

    artifact_event = event_queue.enqueue_event.call_args_list[0][0][0]
    assert "Error:" in artifact_event.artifact.parts[0].text
    assert "LLM connection failed" in artifact_event.artifact.parts[0].text

    status_event = event_queue.enqueue_event.call_args_list[1][0][0]
    assert status_event.status.state == TaskState.TASK_STATE_FAILED


@pytest.mark.asyncio
async def test_executor_handles_empty_message():
    mock_graph = AsyncMock()
    mock_graph.ainvoke = AsyncMock(return_value={
        "input": "No input provided", "output": "I can help", "error": None
    })

    with patch("a2a_agent.executor.graph", mock_graph):
        from a2a_agent.executor import A2AAgentExecutor

        executor = A2AAgentExecutor()

        context = MagicMock()
        context.message = Message(parts=[])
        context.task_id = "test-task-id"
        context.context_id = "test-context-id"

        event_queue = AsyncMock()
        event_queue.enqueue_event = AsyncMock()

        await executor.execute(context, event_queue)

    call_args = mock_graph.ainvoke.call_args[0][0]
    assert call_args["input"] == "No input provided"

    status_event = event_queue.enqueue_event.call_args_list[1][0][0]
    assert status_event.status.state == TaskState.TASK_STATE_COMPLETED
