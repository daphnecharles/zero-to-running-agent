"""Check. An independent gate between thinking and acting.

BUILD 2. Every question here has a yes or no answer, so plain code answers it
the same way every time. The model is never asked.
Stuck? git stash && git checkout step-2
"""
from datetime import date
from urllib.parse import urlparse

import httpx

from agent import config
from agent.log import log_event
from agent.state import AgentState


def is_real(cfp_id: str, known: dict) -> bool:
    """Is this conference in our source data, or did the model make it up?"""
    # TODO 1a.
    return True


def link_works(url: str | None) -> bool:
    """Is the CFP link a real https URL? With CHECK_LINKS_LIVE=true, also request it."""
    # TODO 1b.
    return True


def deadline_open(deadline: str, today: date) -> bool:
    """Is the CFP deadline today or later?"""
    # TODO 1c.
    return True


def check_node(state: AgentState) -> dict:
    # TODO 2. For each fit in state["scores"], run the three checks against the source data.
    # Keep the ones that pass, adding cfp_url and cfp_deadline FROM THE SOURCE DATA.
    # Drop the rest into a rejected list with the reason, and log each one.
    print("Check isn't built yet. That's Build 2.")
    return {"rejected": []}
