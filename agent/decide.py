"""Decide. Turn checked scores into a choice, using thresholds you set.

BUILD 2 (Exercise 2 in EXERCISES.md), along with Check.
"""
from agent import config
from agent.log import log_event
from agent.state import AgentState


def route_for(topic_fit: int) -> str:
    # TODO 3a (see EXERCISES.md, Exercise 2, step 3a). Return "apply_now", "maybe_later" or "skip" using
    # config.APPLY_NOW_MIN and config.MAYBE_LATER_MIN.
    return "skip"


def decide_node(state: AgentState) -> dict:
    # TODO 3b (see EXERCISES.md, Exercise 2, step 3b). Add a "route" to every fit and sort by topic_fit, highest first.
    return {}


def after_decide(state: AgentState) -> str:
    """Conditional edge. Only apply_now opportunities go on to drafting."""
    # TODO 3c (see EXERCISES.md, Exercise 2, step 3c). Return "draft" if anything is apply_now, otherwise "end".
    return "end"
