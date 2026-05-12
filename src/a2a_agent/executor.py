from __future__ import annotations

import uuid

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import (
    Artifact,
    Part,
    TaskArtifactUpdateEvent,
    TaskState,
    TaskStatus,
    TaskStatusUpdateEvent,
)

from a2a_agent.graph import build_graph


graph = build_graph()


class A2AAgentExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        user_message = ""
        for part in context.message.parts:
            if part.text:
                user_message += part.text

        if not user_message:
            user_message = "No input provided"

        error = None
        try:
            result = await graph.ainvoke(
                {"input": user_message, "output": "", "error": None},
                config={"configurable": {"thread_id": context.task_id}},
            )
        except Exception as e:
            result = {"output": f"Error: {e}", "error": str(e)}
            error = e

        output = result.get("output", "No output produced.")
        if result.get("error"):
            output = f"Error: {result['error']}"

        artifact = Artifact(
            artifact_id=str(uuid.uuid4()),
            parts=[Part(text=output)],
        )
        await event_queue.enqueue_event(
            TaskArtifactUpdateEvent(
                task_id=context.task_id,
                context_id=context.context_id,
                artifact=artifact,
                last_chunk=True,
            )
        )

        state = TaskState.TASK_STATE_FAILED if error else TaskState.TASK_STATE_COMPLETED
        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                task_id=context.task_id,
                context_id=context.context_id,
                status=TaskStatus(state=state),
            )
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        pass
