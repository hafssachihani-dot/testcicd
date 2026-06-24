from typing import Callable, TypedDict
from uuid import uuid4

import requests
from langgraph.graph import END, START, StateGraph


class AgentState(TypedDict, total=False):
    question: str
    correlation_id: str
    wikipedia_result: str
    answer: str
    api_failed: bool
    status: str


def search_wikipedia(question: str) -> str:
    response = requests.get(
        "https://en.wikipedia.org/w/api.php",
        params={
            "action": "query",
            "list": "search",
            "srsearch": question,
            "format": "json",
        },
        timeout=10,
    )
    response.raise_for_status()
    results = response.json()["query"]["search"]

    if not results:
        raise ValueError("Aucun resultat Wikipedia")

    return results[0]["snippet"]


def send_to_dlq(question: str, correlation_id: str) -> None:
    requests.post(
        "http://127.0.0.1:3000/dlq/messages",
        json={
            "question": question,
            "correlation_id": correlation_id,
            "status": "FAILED_ROUTED_TO_DLQ",
        },
        timeout=5,
    )


def build_workflow(
    wikipedia_tool: Callable[[str], str] = search_wikipedia,
    dlq_tool: Callable[[str, str], None] = send_to_dlq,
):
    def wikipedia_node(state: AgentState) -> AgentState:
        try:
            result = wikipedia_tool(state["question"])
            return {"wikipedia_result": result, "api_failed": False}
        except (requests.RequestException, ValueError):
            return {"api_failed": True}

    def answer_node(state: AgentState) -> AgentState:
        return {
            "answer": state["wikipedia_result"],
            "status": "SUCCESS",
        }

    def dlq_node(state: AgentState) -> AgentState:
        dlq_tool(state["question"], state["correlation_id"])
        return {
            "answer": "Service Wikipedia indisponible.",
            "status": "FAILED_ROUTED_TO_DLQ",
        }

    def route_after_wikipedia(state: AgentState) -> str:
        return "dlq" if state["api_failed"] else "answer"

    graph = StateGraph(AgentState)
    graph.add_node("wikipedia", wikipedia_node)
    graph.add_node("answer", answer_node)
    graph.add_node("dlq", dlq_node)
    graph.add_edge(START, "wikipedia")
    graph.add_conditional_edges(
        "wikipedia",
        route_after_wikipedia,
        {"answer": "answer", "dlq": "dlq"},
    )
    graph.add_edge("answer", END)
    graph.add_edge("dlq", END)
    return graph.compile()


def run_agent(
    question: str,
    wikipedia_tool: Callable[[str], str] = search_wikipedia,
    dlq_tool: Callable[[str, str], None] = send_to_dlq,
    correlation_id: str | None = None,
) -> AgentState:
    correlation_id = correlation_id or str(uuid4())
    workflow = build_workflow(wikipedia_tool, dlq_tool)
    return workflow.invoke(
        {
            "question": question,
            "correlation_id": correlation_id,
        },
        config={
            "run_name": "wikipedia-agent",
            "tags": ["wikipedia", "langgraph"],
            "metadata": {
                "correlation_id": correlation_id,
            },
        },
    )
