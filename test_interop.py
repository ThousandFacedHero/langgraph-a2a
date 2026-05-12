"""A2A interop test — verify this agent can communicate with the LangChain A2A agent.

Prerequisites:
  1. Both agents configured with .env (same LLM endpoint)
  2. Start the LangChain A2A agent on port 8002:
       cd ../langchain-a2a && AGENT_PORT=8002 AGENT_NAME=langchain-a2a uv run python -m a2a_agent
  3. Start this agent on port 8001:
       AGENT_PORT=8001 AGENT_NAME=langgraph-a2a uv run python -m a2a_agent
  4. Run this script:
       uv run python test_interop.py

See also: https://github.com/ThousandFacedHero/langchain-a2a
"""
from __future__ import annotations

import httpx
import json
import sys


LANGGRAPH_URL = "http://localhost:8001"
LANGCHAIN_URL = "http://localhost:8002"


def send_message(base_url: str, text: str, request_id: str) -> dict:
    payload = {
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
    r = httpx.post(
        f"{base_url}/",
        json=payload,
        headers={"A2A-Version": "1.0"},
        timeout=120.0,
    )
    r.raise_for_status()
    return r.json()


def check_agent_card(base_url: str, name: str) -> bool:
    r = httpx.get(f"{base_url}/.well-known/agent-card.json", timeout=5.0)
    r.raise_for_status()
    card = r.json()
    print(f"  Agent: {card['name']} — {card.get('description', '')[:80]}")
    print(f"  Skills: {[s['id'] for s in card.get('skills', [])]}")
    return True


def main():
    passed = 0
    failed = 0

    print("1. Checking agent cards...\n")
    for name, url in [("LangGraph", LANGGRAPH_URL), ("LangChain", LANGCHAIN_URL)]:
        try:
            check_agent_card(url, name)
            passed += 1
        except Exception as e:
            print(f"  FAIL: {name} agent card — {e}")
            print(f"  Is the {name} agent running on {url}?")
            failed += 1
    print()

    if failed > 0:
        print("Agent card checks failed. Start both agents before running this test.")
        sys.exit(1)

    print("2. Sending message to LangGraph agent...\n")
    try:
        result = send_message(LANGGRAPH_URL, "Say just the word 'hello'", "lg-1")
        task = result["result"]["task"]
        state = task["status"]["state"]
        artifacts = task.get("artifacts", [])
        text = artifacts[0]["parts"][0]["text"] if artifacts else "(no output)"
        print(f"  Status: {state}")
        print(f"  Output: {text[:200]}")
        assert state == "TASK_STATE_COMPLETED", f"Expected COMPLETED, got {state}"
        passed += 1
    except Exception as e:
        print(f"  FAIL: {e}")
        failed += 1
    print()

    print("3. Sending message to LangChain agent...\n")
    try:
        result = send_message(LANGCHAIN_URL, "Say just the word 'hello'", "lc-1")
        task = result["result"]["task"]
        state = task["status"]["state"]
        artifacts = task.get("artifacts", [])
        text = artifacts[0]["parts"][0]["text"] if artifacts else "(no output)"
        print(f"  Status: {state}")
        print(f"  Output: {text[:200]}")
        assert state == "TASK_STATE_COMPLETED", f"Expected COMPLETED, got {state}"
        passed += 1
    except Exception as e:
        print(f"  FAIL: {e}")
        failed += 1
    print()

    print(f"Results: {passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
