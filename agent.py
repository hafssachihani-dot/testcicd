from typing import Any, Callable, TypedDict


class AgentState(TypedDict, total=False):
    question: str
    answer: str
    confidence: float
    blocked: bool
    reason: str


FORBIDDEN_PHRASES = ("je ne sais pas", "aucune idee", "erreur interne")
MIN_CONFIDENCE = 0.7


def is_response_compliant(response: dict[str, Any]) -> bool:
    answer = str(response.get("answer", "")).strip().lower()
    confidence = float(response.get("confidence", 0))

    if not answer:
        return False
    if confidence < MIN_CONFIDENCE:
        return False
    return not any(phrase in answer for phrase in FORBIDDEN_PHRASES)


def make_answer_node(llm: Any) -> Callable[[AgentState], AgentState]:
    def answer_node(state: AgentState) -> AgentState:
        raw_response = llm.invoke(state["question"])

        if isinstance(raw_response, str):
            response = {"answer": raw_response, "confidence": 1.0}
        else:
            response = raw_response

        if not is_response_compliant(response):
            return {
                **state,
                "answer": "Reponse non conforme.",
                "confidence": 0.0,
                "blocked": True,
                "reason": "compliance_failed",
            }

        return {
            **state,
            "answer": str(response["answer"]).strip(),
            "confidence": float(response["confidence"]),
            "blocked": False,
        }

    return answer_node


def build_workflow(graph_factory: Callable[[type[AgentState]], Any], llm: Any) -> Any:
    graph = graph_factory(AgentState)
    graph.add_node("answer", make_answer_node(llm))
    graph.set_entry_point("answer")
    graph.set_finish_point("answer")
    return graph.compile()
