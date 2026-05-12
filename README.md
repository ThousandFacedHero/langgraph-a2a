# LangGraph A2A Agent

A production-ready template for building [A2A-compliant](https://google.github.io/A2A/) agents with [LangGraph](https://github.com/langchain-ai/langgraph). Fork this repo, replace `graph.py` with your logic, and get a fully wired A2A agent with JSON-RPC, agent discovery, task lifecycle management, and optional observability.

## What it does

This template handles all the A2A protocol plumbing so you can focus on your agent's logic. The included example graph calls an OpenAI-compatible LLM and returns the response — a minimal but complete implementation you can run end-to-end before replacing it with your own.

The A2A layer provides agent discovery (via `/.well-known/agent-card.json`), task state management, and artifact exchange with any A2A-compatible orchestrator. The LangGraph layer provides a stateful, checkpointed graph runtime suitable for multi-step pipelines.

## Key Projects

| Project | Description |
|---------|-------------|
| [Google A2A Protocol](https://google.github.io/A2A/) | Agent-to-agent communication standard |
| [a2a-sdk](https://github.com/google/A2A/tree/main/a2a-sdk/python) | Python SDK for the A2A protocol |
| [LangGraph](https://github.com/langchain-ai/langgraph) | Stateful graph runtime for agents |
| [LangChain](https://github.com/langchain-ai/langchain) | The broader LangChain ecosystem |

## Architecture

```
graph.py          Your LangGraph StateGraph — replace this with your logic
    |
executor.py       A2A bridge — extracts the user message, invokes the graph,
                  emits TaskArtifactUpdateEvent + TaskStatusUpdateEvent
    |
a2a_server.py     FastAPI app — composes the A2A JSON-RPC routes and agent
                  card routes, exposes /healthz and /readyz
```

The A2A protocol layer (`executor.py` + `a2a_server.py`) is intentionally stable. In most forks you only touch `graph.py`, `state.py`, and the agent card in `a2a_server.py`.

**Request flow:** an A2A caller sends a `SendMessage` JSON-RPC request to `/`. The `DefaultRequestHandler` creates a task, calls `A2AAgentExecutor.execute()`, and streams events back. The executor invokes the LangGraph graph and emits two events: a `TaskArtifactUpdateEvent` carrying the output text, and a `TaskStatusUpdateEvent` with `TASK_STATE_COMPLETED` or `TASK_STATE_FAILED`.

## Quickstart

**Prerequisites:** Python 3.12, [uv](https://github.com/astral-sh/uv), an OpenAI-compatible LLM endpoint.

```bash
# 1. Clone
git clone https://github.com/ThousandFacedHero/langgraph-a2a.git my-agent
cd my-agent

# 2. Configure
cp .env.example .env
# Edit .env — set OPENAI_BASE_URL and OPENAI_API_KEY for your endpoint

# 3. Install
uv sync

# 4. Smoke-test the graph directly (no server needed)
uv run python test_local.py "Hello, world!"

# 5. Start the A2A server
uv run python -m a2a_agent
```

Once running:

```
Agent card:   http://localhost:8000/.well-known/agent-card.json
Health check: http://localhost:8000/healthz
Ready check:  http://localhost:8000/readyz
JSON-RPC:     POST http://localhost:8000/
```

Send a request:

```bash
curl -s -X POST http://localhost:8000/ \
  -H "Content-Type: application/json" \
  -H "A2A-Version: 1.0" \
  -d '{
    "jsonrpc": "2.0",
    "method": "SendMessage",
    "id": "1",
    "params": {
      "message": {
        "role": "ROLE_USER",
        "parts": [{"text": "What is the capital of France?"}],
        "messageId": "msg-1"
      }
    }
  }' | python -m json.tool
```

## How to Fork

1. **Clone this repo** into a new directory for your agent.

2. **Rename the package.** In `src/`, rename `a2a_agent/` to your agent's name. Update `pyproject.toml`:
   ```toml
   [project]
   name = "my-agent"

   [tool.hatch.build.targets.wheel]
   packages = ["src/my_agent"]
   ```

3. **Replace `graph.py`.** Define your `build_graph()` function. The only contract is that it returns a compiled LangGraph that accepts `{"input": str, "output": str, "error": str | None}` — or update `state.py` and `executor.py` together if you need a different state shape.

4. **Update `state.py`.** Extend `AgentState` with any additional fields your graph uses.

5. **Update the agent card in `a2a_server.py`.** Set your agent's name, description, version, and skills.

6. **Update `config.py`** if you need additional settings. `pydantic-settings` reads from `.env` automatically.

7. **Update `.env.example`** with any new variables and sensible defaults.

8. **Run the tests** to confirm the A2A plumbing still works: `uv run pytest tests/ -v`

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | — | API key for your LLM endpoint |
| `OPENAI_BASE_URL` | No | `http://localhost:11434/v1` | OpenAI-compatible API base URL |
| `LLM_MODEL` | No | `llama3` | Model name as known to your endpoint |
| `AGENT_NAME` | No | `a2a-agent` | Agent identity in the A2A agent card |
| `AGENT_PORT` | No | `8000` | Port for the A2A server |
| `LANGFUSE_ENABLED` | No | `false` | Enable client-side Langfuse tracing |
| `LANGFUSE_PUBLIC_KEY` | No | — | Langfuse public key |
| `LANGFUSE_SECRET_KEY` | No | — | Langfuse secret key |
| `LANGFUSE_HOST` | No | `http://localhost:3000` | Langfuse server URL |
| `SSL_CERT_FILE` | No | — | Path to custom CA bundle (private LLM endpoints) |

`OPENAI_API_KEY` and `OPENAI_BASE_URL` are read directly by the `openai` SDK from the environment; they do not appear in `config.py`.

## Testing

```bash
# Run all tests (some require a live LLM endpoint configured in .env)
uv run pytest tests/ -v

# Test the graph directly against a live LLM endpoint
uv run python test_local.py "Summarize the A2A protocol in one sentence"
```

The test suite covers:

| File | What it tests |
|------|--------------|
| `test_config.py` | Settings load from env, defaults |
| `test_state.py` | AgentState TypedDict structure |
| `test_llm.py` | LLM client construction, chat completion (live LLM) |
| `test_graph.py` | Graph builds and compiles without error |
| `test_graph_invoke.py` | Graph invocation with mocked LLM |
| `test_executor.py` | Executor emits correct A2A events (mocked graph) |
| `test_server.py` | FastAPI app structure, agent card, health endpoints |
| `test_tracing.py` | Langfuse init is a no-op when disabled |
| `test_a2a_roundtrip.py` | Full JSON-RPC round-trip with mocked LLM |

Round-trip and executor tests use `httpx.AsyncClient` with `ASGITransport` so the async A2A event pipeline runs in-process without a live server. The LLM tests in `test_llm.py` make real calls to the configured endpoint.

## Deployment

### Bare Python

```bash
uv run python -m a2a_agent
```

### Docker

```bash
docker build -t my-agent:0.1.0 .
docker run -p 8000:8000 --env-file .env my-agent:0.1.0
```

The Dockerfile uses a multi-stage build: dependencies are installed in a builder stage, only the virtualenv and source are copied to the runtime image. The runtime container runs as a non-root user.

### Kubernetes

```bash
cp -r deploy.example/ deploy/
# Edit deploy/*.yaml — fill in all <PLACEHOLDER> values
kubectl apply -f deploy/
```

`deploy.example/` contains templated manifests for a `Deployment`, `Service`, and `Ingress`. Placeholders follow the `<UPPER_SNAKE_CASE>` convention. The `deploy/` directory is gitignored so your environment-specific values stay local.

The deployment manifest includes liveness (`/healthz`) and readiness (`/readyz`) probes, resource requests and limits, and commented-out sections for mounting a custom CA certificate from a ConfigMap.

## Project Structure

| Path | Purpose |
|------|---------|
| `src/a2a_agent/graph.py` | **Replace this** — LangGraph `StateGraph` with your logic |
| `src/a2a_agent/state.py` | **Replace/extend this** — `AgentState` TypedDict |
| `src/a2a_agent/executor.py` | A2A-to-graph bridge — keep as-is unless you change state shape |
| `src/a2a_agent/a2a_server.py` | Agent card definition + FastAPI app wiring — update card details |
| `src/a2a_agent/config.py` | `pydantic-settings` config — extend with your settings |
| `src/a2a_agent/llm.py` | Async OpenAI client with optional CA bundle — keep as-is |
| `src/a2a_agent/tracing.py` | Langfuse opt-in via `openai` auto-patching — keep as-is |
| `src/a2a_agent/__main__.py` | Entry point — loads `.env`, starts uvicorn |
| `test_local.py` | CLI harness to invoke the graph directly without A2A |
| `test_interop.py` | A2A interop test against the [LangChain A2A agent](https://github.com/ThousandFacedHero/langchain-a2a) |
| `tests/` | Pytest suite |
| `deploy.example/` | Templated Kubernetes manifests |
| `Dockerfile` | Multi-stage build, non-root runtime |
| `pyproject.toml` | Project metadata, dependencies, tool config |

## A2A Interop Testing

This template is designed to interoperate with the companion [LangChain A2A Agent](https://github.com/ThousandFacedHero/langchain-a2a). To verify A2A communication works across both frameworks:

```bash
# Terminal 1 — start this agent on port 8001
AGENT_PORT=8001 AGENT_NAME=langgraph-a2a uv run python -m a2a_agent

# Terminal 2 — start the LangChain agent on port 8002
cd ../langchain-a2a
AGENT_PORT=8002 AGENT_NAME=langchain-a2a uv run python -m a2a_agent

# Terminal 3 — run the interop test
uv run python test_interop.py
```

The test verifies agent card discovery and A2A `SendMessage` round-trips in both directions. Both agents must be configured with a working LLM endpoint (same `.env` setup).

## Companion Template

For tool-calling agents with a standard ReAct loop, see the [LangChain A2A Agent](https://github.com/ThousandFacedHero/langchain-a2a). It provides the same A2A wiring on top of LangChain's `create_agent()` instead of a raw `StateGraph`.
