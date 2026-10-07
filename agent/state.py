"""The shared notebook every node reads from and writes to.

Each node returns only the fields it changes, and LangGraph merges them in.
"""
from typing import TypedDict


class AgentState(TypedDict, total=False):
    run_id: str
    readme_source: str        # a GitHub URL or local path, set when the run starts

    profile: dict             # Gather. what your project is about, built from the README
    opportunities: list       # Gather. open CFPs from the fixtures file
    scores: list              # Reason, then Check and Decide. one fit per CFP
    rejected: list            # Check. what the gate threw out, and why
    drafts: list              # Act. proposals waiting on you
    decisions: list           # Act. what you approved, edited or rejected
