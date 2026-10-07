"""Gather. Plain code that collects facts. No model calls on purpose.

Prewritten in the repo. In the workshop we read it together and run it.
"""
import json
import re
from pathlib import Path

import httpx

from agent import config
from agent.log import log_event
from agent.state import AgentState

SAMPLE_README = config.DATA_DIR / "sample_readme.md"

# Words that hint at what a project is about. Plain keyword matching, nothing clever.
TOPIC_KEYWORDS = {
    "python": ["python", "pip", "pypi", "fastapi", "django", "flask"],
    "javascript": ["javascript", "typescript", "node", "react", "npm"],
    "data": ["data", "pipeline", "sql", "database", "analytics", "etl", "ml", "llm", "ai", "agent"],
    "devops": ["kubernetes", "docker", "ci", "deploy", "infrastructure", "terraform"],
    "security": ["security", "auth", "vulnerability", "encryption"],
    "opensource": ["open source", "open-source", "contributors", "license", "mit", "apache"],
    "ux": ["design", "ux", "accessibility", "user experience"],
}


def read_readme(source: str | None) -> tuple[str, str]:
    """Return (readme_text, where_it_came_from). Accepts a GitHub repo URL, a local path, or nothing."""
    if source and source.startswith("https://github.com/"):
        owner_repo = "/".join(source.rstrip("/").removeprefix("https://github.com/").split("/")[:2])
        # raw.githubusercontent.com doesn't count against the GitHub API rate limit,
        # which matters when 100 people share one conference wifi.
        for name in ("README.md", "readme.md", "README.rst", "README"):
            url = f"https://raw.githubusercontent.com/{owner_repo}/HEAD/{name}"
            try:
                resp = httpx.get(url, timeout=10, follow_redirects=True)
            except httpx.HTTPError:
                break
            if resp.status_code == 200:
                return resp.text, url
        print(f"Couldn't fetch a README from {source}, using the sample README instead.")
    elif source and Path(source).exists():
        return Path(source).read_text(), source
    return SAMPLE_README.read_text(), str(SAMPLE_README)


def build_profile(readme: str, source: str) -> dict:
    """Turn a README into a small profile. Plain string handling, no model."""
    title_match = re.search(r"^#\s+(.+)$", readme, re.MULTILINE)
    lowered = readme.lower()
    topics = [topic for topic, words in TOPIC_KEYWORDS.items() if any(w in lowered for w in words)]
    return {
        "name": title_match.group(1).strip() if title_match else "Untitled project",
        "source": source,
        "topics": topics,
        # Keep the excerpt short so free-tier token limits aren't a problem.
        "summary": readme[:2000],
    }


def readme_node(state: AgentState) -> dict:
    readme, source = read_readme(state.get("readme_source"))
    profile = build_profile(readme, source)
    log_event(state["run_id"], "gather", "profile_built", project=profile["name"], topics=profile["topics"])
    return {"profile": profile}


def cfp_node(state: AgentState) -> dict:
    data = json.loads((config.DATA_DIR / "cfps.json").read_text())
    log_event(state["run_id"], "gather", "cfps_loaded", count=len(data["cfps"]), snapshot=data["snapshot_date"])
    return {"opportunities": data["cfps"]}
