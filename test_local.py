"""Local test harness — invoke the graph directly, no A2A, no server.

Usage:
    uv run python test_local.py "What is the capital of France?"
    echo "Hello" | uv run python test_local.py
"""
from __future__ import annotations

import asyncio
import sys

from dotenv import load_dotenv

load_dotenv()

from a2a_agent.tracing import init_tracing
from a2a_agent.graph import build_graph

init_tracing()


async def main() -> None:
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
    elif not sys.stdin.isatty():
        user_input = sys.stdin.read().strip()
    else:
        print("Usage: uv run python test_local.py 'your message here'")
        sys.exit(1)

    graph = build_graph()

    print(f"Input: {user_input}")
    print("---")

    result = await graph.ainvoke(
        {"input": user_input, "output": "", "error": None},
        config={"configurable": {"thread_id": "local-test"}},
    )

    if result.get("error"):
        print(f"Error: {result['error']}")
        sys.exit(1)

    print(f"Output: {result['output']}")


if __name__ == "__main__":
    asyncio.run(main())
