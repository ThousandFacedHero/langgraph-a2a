from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.routes import create_jsonrpc_routes, create_agent_card_routes
from a2a.types import AgentCard, AgentSkill

from a2a_agent.config import settings
from a2a_agent.executor import A2AAgentExecutor


def build_agent_card() -> AgentCard:
    return AgentCard(
        name=settings.agent_name,
        description="A2A-compliant LangGraph agent. Fork and replace graph.py to build your own.",
        version="0.1.0",
        skills=[
            AgentSkill(
                id="chat",
                name="General Chat",
                description="Send a message and get a response from the LLM.",
                tags=["chat", "llm"],
            ),
        ],
    )


def create_app() -> FastAPI:
    agent_card = build_agent_card()
    task_store = InMemoryTaskStore()
    executor = A2AAgentExecutor()

    handler = DefaultRequestHandler(
        agent_executor=executor,
        task_store=task_store,
        agent_card=agent_card,
    )

    card_routes = create_agent_card_routes(agent_card)
    jsonrpc_routes = create_jsonrpc_routes(handler, rpc_url="/")

    app = FastAPI(routes=card_routes + jsonrpc_routes)

    @app.get("/healthz")
    async def healthz():
        return JSONResponse({"status": "ok"})

    @app.get("/readyz")
    async def readyz():
        return JSONResponse({"status": "ready"})

    return app
