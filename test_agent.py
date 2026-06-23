from unittest.mock import Mock

from agent import build_workflow, make_answer_node


def test_answer_node_accepts_compliant_response():
    llm = Mock()
    llm.invoke.return_value = {
        "answer": "Paris est la capitale de la France.",
        "confidence": 0.95,
    }

    node = make_answer_node(llm)
    result = node({"question": "Quelle est la capitale de la France ?"})

    assert result["answer"] == "Paris est la capitale de la France."
    assert result["confidence"] == 0.95
    assert result["blocked"] is False


def test_answer_node_blocks_low_confidence_response():
    llm = Mock()
    llm.invoke.return_value = {"answer": "Peut-etre Paris.", "confidence": 0.4}

    node = make_answer_node(llm)
    result = node({"question": "Quelle est la capitale de la France ?"})

    assert result["blocked"] is True
    assert result["reason"] == "compliance_failed"


def test_answer_node_blocks_forbidden_phrase():
    llm = Mock()
    llm.invoke.return_value = {"answer": "Je ne sais pas.", "confidence": 0.9}

    node = make_answer_node(llm)
    result = node({"question": "Question metier critique"})

    assert result["blocked"] is True
    assert result["answer"] == "Reponse non conforme."


def test_answer_node_accepts_simple_string_response():
    llm = Mock()
    llm.invoke.return_value = "La commande est valide."

    node = make_answer_node(llm)
    result = node({"question": "Verifier la commande"})

    assert result["answer"] == "La commande est valide."
    assert result["confidence"] == 1.0


def test_build_workflow_uses_mocked_langgraph_builder():
    compiled_app = Mock(name="compiled_app")
    graph = Mock()
    graph.compile.return_value = compiled_app
    graph_factory = Mock(return_value=graph)
    llm = Mock()

    result = build_workflow(graph_factory, llm)

    assert result is compiled_app
    graph.add_node.assert_called_once()
    graph.set_entry_point.assert_called_once_with("answer")
    graph.set_finish_point.assert_called_once_with("answer")
    graph.compile.assert_called_once_with()
