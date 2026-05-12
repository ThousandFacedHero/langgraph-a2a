from __future__ import annotations

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END

from a2a_agent.llm import chat_completion
from a2a_agent.state import AgentState


async def process_node(state: AgentState) -> dict:
    result = await chat_completion([
        {"role": "user", "content": state["input"]}
    ])
    return {"output": result}


def build_graph():
    builder = StateGraph(AgentState)
    builder.add_node("process", process_node)
    builder.add_edge(START, "process")
    builder.add_edge("process", END)
    return builder.compile(checkpointer=InMemorySaver())
