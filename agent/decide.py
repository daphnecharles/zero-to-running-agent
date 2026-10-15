"""Decide. Turn checked scores into a choice, using thresholds you set.

Exercise 2 in the workshop, along with Check.
"""
from agent import config
from agent.log import log_event
from agent.state import AgentState


def route_for(topic_fit: int) -> str:
    if topic_fit >= config.APPLY_NOW_MIN:
        return "apply_now"
    if topic_fit >= config.MAYBE_LATER_MIN:
        return "maybe_later"
    return "skip"


def decide_node(state: AgentState) -> dict:
    scores = [{**fit, "route": route_for(fit["topic_fit"])} for fit in state["scores"]]
    scores.sort(key=lambda fit: fit["topic_fit"], reverse=True)
    counts = {r: sum(1 for f in scores if f["route"] == r) for r in ("apply_now", "maybe_later", "skip")}
    log_event(state["run_id"], "decide", "routed", **counts)
    return {"scores": scores}


def after_decide(state: AgentState) -> str:
    """Conditional edge. Only apply_now opportunities go on to drafting."""
    return "draft" if any(f["route"] == "apply_now" for f in state["scores"]) else "end"
