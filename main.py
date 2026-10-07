"""The agent behind an API.

    uvicorn main:app --reload
    then open http://localhost:8000/docs
"""
import uuid

from fastapi import FastAPI, HTTPException
from langgraph.types import Command
from pydantic import BaseModel

from agent.graph import build_graph

app = FastAPI(title="From Zero to Running Agent")
graph = build_graph()  # in-memory checkpoints, so runs live as long as the server does


class RunRequest(BaseModel):
    repo_url: str | None = None  # a GitHub repo URL, or leave empty for the sample README


class Decision(BaseModel):
    cfp_id: str
    action: str  # "approve", "edit" or "reject"
    abstract: str | None = None


def config_for(run_id: str) -> dict:
    return {"configurable": {"thread_id": run_id}}


@app.post("/runs")
def start_run(req: RunRequest):
    """Start a run. It goes until the pause and returns the drafts waiting for review."""
    run_id = uuid.uuid4().hex[:8]
    result = graph.invoke({"run_id": run_id, "readme_source": req.repo_url}, config_for(run_id))
    return {
        "run_id": run_id,
        "waiting_for_review": "__interrupt__" in result,
        "scores": result.get("scores", []),
        "rejected": result.get("rejected", []),
    }


@app.get("/runs/{run_id}/drafts")
def list_drafts(run_id: str):
    """List the drafts for a run, with their status."""
    snapshot = graph.get_state(config_for(run_id))
    if not snapshot.values:
        raise HTTPException(404, "No run with that id")
    return {"run_id": run_id, "paused": bool(snapshot.next), "drafts": snapshot.values.get("drafts", [])}


@app.post("/runs/{run_id}/review")
def review(run_id: str, decisions: list[Decision]):
    """Approve, edit or reject drafts. This resumes the graph. Nothing is ever submitted for you."""
    snapshot = graph.get_state(config_for(run_id))
    if not snapshot.next:
        raise HTTPException(409, "This run isn't waiting for review")
    result = graph.invoke(Command(resume=[d.model_dump() for d in decisions]), config_for(run_id))
    return {"run_id": run_id, "drafts": result.get("drafts", [])}


@app.get("/health")
def health():
    return {"ok": True}
