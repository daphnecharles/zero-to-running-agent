"""Decide. Turn checked scores into a choice, using thresholds you set.

BUILD 2, along with Check.
"""
from agent import config
from agent.log import log_event
from agent.state import AgentState


def route_for(topic_fit: int) -> str:
    # TODO 3. Return "apply_now", "maybe_later" or "skip" using
    # config.APPLY_NOW_MIN and config.MAYBE_LATER_MIN.
    return "skip"


def decide_node(state: AgentState) -> dict:
    # TODO 3. Add a "route" to every fit and sort by topic_fit, highest first.
    return {}


def after_decide(state: AgentState) -> str:
    """Conditional edge. Only apply_now opportunities go on to drafting."""
    # TODO 3. Return "draft" if anything is apply_now, otherwise "end".
    return "end"
