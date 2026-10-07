from agent.gather import build_profile


def test_profile_reads_title_and_topics():
    profile = build_profile("# demo\n\nA Python data pipeline with Docker deploys.", "test")
    assert profile["name"] == "demo"
    assert {"python", "data", "devops"} <= set(profile["topics"])


def test_profile_without_title():
    assert build_profile("no heading here", "test")["name"] == "Untitled project"
