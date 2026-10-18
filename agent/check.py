"""Check. An independent gate between thinking and acting.

Exercise 2 in the workshop. Every question here has a yes or no answer,
so plain code answers it the same way every time. The model is never asked.
"""
from datetime import date
from urllib.parse import urlparse

import httpx

from agent import config
from agent.log import log_event
from agent.state import AgentState


def is_real(cfp_id: str, known: dict) -> bool:
    """Is this conference in our source data, or did the model make it up?"""
    return cfp_id in known


def link_works(url: str | None) -> bool:
    """Is the CFP link a real https URL? With CHECK_LINKS_LIVE=true, also request it."""
    if not url or urlparse(url).scheme != "https":
        return False
    if not config.CHECK_LINKS_LIVE:
        return True
    try:
        resp = httpx.head(url, timeout=8, follow_redirects=True)
        if resp.status_code == 405:  # some sites don't allow HEAD
            resp = httpx.get(url, timeout=8, follow_redirects=True)
        return resp.status_code < 400
    except httpx.HTTPError:
        return False


def deadline_open(deadline: str, today: date) -> bool:
    """Is the CFP deadline today or later?"""
    return date.fromisoformat(deadline) >= today


def check_node(state: AgentState) -> dict:
    known = {cfp["id"]: cfp for cfp in state["opportunities"]}
    today = config.today()
    passed, rejected = [], []

    for fit in state["scores"]:
        cfp = known.get(fit["cfp_id"])
        if not is_real(fit["cfp_id"], known):
            reason = "not in source data, the model may have invented it"
        elif not link_works(cfp.get("cfp_url")):
            reason = "link is missing or not a working https URL"
        elif not deadline_open(cfp["cfp_deadline"], today):
            reason = f"deadline passed on {cfp['cfp_deadline']}"
        else:
            # Facts come from the source data, never from the model's answer.
            passed.append({**fit, "cfp_url": cfp["cfp_url"], "cfp_deadline": cfp["cfp_deadline"]})
            continue
        rejected.append({"cfp_id": fit["cfp_id"], "cfp_name": fit["cfp_name"], "why": reason})
        log_event(state["run_id"], "check", "rejected", cfp=fit["cfp_name"], why=reason)

    log_event(state["run_id"], "check", "done", passed=len(passed), rejected=len(rejected))
    return {"scores": passed, "rejected": rejected}
