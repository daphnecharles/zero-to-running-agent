"""Node-level tests for the finished agent (step-3 only). They call each node with a hand-built state."""
import pytest

from agent import config
from agent.act import save_node
from agent.check import check_node
from agent.decide import after_decide, decide_node


@pytest.fixture(autouse=True)
def isolated_dirs(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "LOG_DIR", tmp_path / "logs")
    monkeypatch.setattr(config, "OUTPUT_DIR", tmp_path / "outputs")
    monkeypatch.setenv("TODAY", "2026-10-19")


def fit(cfp_id, score=9, name=None):
    return {"cfp_id": cfp_id, "cfp_name": name or cfp_id, "topic_fit": score, "reason": "r"}


CFPS = [
    {"id": "open", "name": "Open", "cfp_url": "https://example.com/cfp", "cfp_deadline": "2026-10-19"},
    {"id": "closed", "name": "Closed", "cfp_url": "https://example.com/cfp", "cfp_deadline": "2026-10-18"},
    {"id": "insecure", "name": "Insecure", "cfp_url": "http://example.com/cfp", "cfp_deadline": "2026-12-01"},
    {"id": "nolink", "name": "No link", "cfp_deadline": "2026-12-01"},
]


def test_check_keeps_real_open_cfps_and_takes_facts_from_source():
    state = {"run_id": "t", "opportunities": CFPS, "scores": [fit("open")]}
    out = check_node(state)
    assert out["rejected"] == []
    assert out["scores"][0]["cfp_url"] == "https://example.com/cfp"
    assert out["scores"][0]["cfp_deadline"] == "2026-10-19"


def test_check_rejects_invented_closed_and_bad_links_with_reasons():
    ids = ["invented", "closed", "insecure", "nolink"]
    out = check_node({"run_id": "t", "opportunities": CFPS, "scores": [fit(i) for i in ids]})
    assert out["scores"] == []
    why = {r["cfp_id"]: r["why"] for r in out["rejected"]}
    assert why["invented"].startswith("not in source data")
    assert why["closed"] == "deadline passed on 2026-10-18"
    assert why["insecure"] == why["nolink"] == "link is missing or not a working https URL"


def test_decide_routes_and_sorts_highest_first():
    out = decide_node({"run_id": "t", "scores": [fit("a", 2), fit("b", 9), fit("c", 5)]})
    assert [(f["cfp_id"], f["route"]) for f in out["scores"]] == [
        ("b", "apply_now"), ("c", "maybe_later"), ("a", "skip")]


def test_after_decide_drafts_only_when_something_is_apply_now():
    assert after_decide({"scores": [{"route": "skip"}, {"route": "apply_now"}]}) == "draft"
    assert after_decide({"scores": [{"route": "maybe_later"}]}) == "end"


def draft(cfp_id):
    return {"cfp_id": cfp_id, "cfp_name": cfp_id, "cfp_url": "https://example.com", "cfp_deadline": "2026-10-31",
            "title": "T", "abstract": "original", "status": "waiting_for_approval"}


def run_save(decisions, ids=("a", "b")):
    return save_node({"run_id": "t", "drafts": [draft(i) for i in ids], "decisions": decisions})["drafts"]


def test_save_defaults_to_reject_for_missing_and_unknown_actions():
    out = run_save([{"cfp_id": "a", "action": "banana"}])
    assert [d["status"] for d in out] == ["rejected", "rejected"]
    assert not config.OUTPUT_DIR.exists()


def test_save_approves_and_applies_edits_and_writes_only_approved():
    out = run_save([{"cfp_id": "a", "action": "edit", "abstract": "new"}, {"cfp_id": "b", "action": "reject"}])
    assert [(d["status"], d["abstract"]) for d in out] == [("approved", "new"), ("rejected", "original")]
    text = (config.OUTPUT_DIR / "approved_t.md").read_text()
    assert "new" in text and "## b" not in text


def test_save_edit_without_abstract_keeps_the_original():
    out = run_save([{"cfp_id": "a", "action": "edit"}, {"cfp_id": "b", "action": "edit", "abstract": ""}])
    assert [d["abstract"] for d in out] == ["original", "original"]


def test_save_writes_non_ascii_text_as_utf8():
    ds = [{**draft("a"), "abstract": "snapshots → faster, naïve ü"}]
    save_node({"run_id": "t", "drafts": ds, "decisions": [{"cfp_id": "a", "action": "approve"}]})
    assert "snapshots → faster" in (config.OUTPUT_DIR / "approved_t.md").read_text(encoding="utf-8")
