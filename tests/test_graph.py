def test_build_graph_returns_compiled_graph():
    from a2a_agent.graph import build_graph

    graph = build_graph()
    assert graph is not None
    assert hasattr(graph, "ainvoke")


def test_build_graph_has_process_node():
    from a2a_agent.graph import build_graph

    graph = build_graph()
    node_names = list(graph.get_graph().nodes.keys())
    assert "process" in node_names


def test_build_graph_has_checkpointer():
    from a2a_agent.graph import build_graph

    graph = build_graph()
    assert graph.checkpointer is not None
