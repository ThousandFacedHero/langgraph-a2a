def test_agent_state_has_required_fields():
    from a2a_agent.state import AgentState

    hints = AgentState.__annotations__
    assert "input" in hints
    assert "output" in hints
    assert "error" in hints


def test_agent_state_can_be_instantiated():
    from a2a_agent.state import AgentState

    state: AgentState = {"input": "hello", "output": "", "error": None}
    assert state["input"] == "hello"
    assert state["error"] is None
