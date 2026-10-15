from datetime import date

from agent.check import deadline_open, is_real, link_works
from agent.decide import route_for


def test_invented_conference_is_not_real():
    assert not is_real("agentcon-atlantis-2026", {"scale-2027": {}})


def test_link_must_be_https():
    assert link_works("https://example.com/cfp")
    assert not link_works("http://example.com/cfp")
    assert not link_works(None)


def test_deadline():
    assert deadline_open("2026-10-19", date(2026, 10, 19))
    assert not deadline_open("2026-10-18", date(2026, 10, 19))


def test_routes():
    assert route_for(9) == "apply_now"
    assert route_for(5) == "maybe_later"
    assert route_for(1) == "skip"
