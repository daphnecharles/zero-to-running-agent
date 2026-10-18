from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_repo_url_must_be_github():
    # A local path must never be readable through the API.
    assert client.post("/runs", json={"repo_url": "/etc/passwd"}).status_code == 422
    assert client.post("/runs", json={"repo_url": "http://github.com/a/b"}).status_code == 422


def test_review_action_must_be_known():
    body = [{"cfp_id": "x", "action": "banana"}]
    assert client.post("/runs/anything/review", json=body).status_code == 422


def test_review_unknown_run_is_404():
    body = [{"cfp_id": "x", "action": "approve"}]
    assert client.post("/runs/does-not-exist/review", json=body).status_code == 404
