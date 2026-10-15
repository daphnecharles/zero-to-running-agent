"""Rebuild data/cfps.json from the open confs.tech dataset.

Run this the day before the workshop so deadlines are current:
    python scripts/refresh_fixtures.py --as-of 2026-10-19

"Open" means the CFP is still open on the --as-of date (default today).
The UXLx conference is always kept in the open set while it is still open, because a
workshop knowledge-check question uses it.
"""
import argparse
import json
import re
from datetime import date, timedelta
from pathlib import Path

import httpx

SOURCE = "https://raw.githubusercontent.com/tech-conferences/conference-data/main/conferences/{year}/{topic}.json"
TOPICS = ["python", "javascript", "devops", "data", "general", "opensource", "security", "ux", "java", "dotnet"]
OUT = Path(__file__).resolve().parent.parent / "data" / "cfps.json"

MAX_OPEN = 9      # CFPs still open, so the agent has real choices
MAX_CLOSED = 3    # recently closed CFPs, so the Check gate has something to catch
ALWAYS_KEEP = ("UXLx",)  # conference names that must stay in the open set while still open


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def fetch(today: date) -> dict:
    found = {}
    for year in (today.year, today.year + 1):
        for topic in TOPICS:
            resp = httpx.get(SOURCE.format(year=year, topic=topic), timeout=20)
            if resp.status_code != 200:
                continue
            for conf in resp.json():
                if not (conf.get("cfpUrl") and conf.get("cfpEndDate")):
                    continue
                key = f'{slug(conf["name"])}-{(conf.get("startDate") or str(year))[:4]}'
                entry = found.setdefault(key, {
                    "id": key,
                    "name": conf["name"],
                    "url": conf.get("url"),
                    "cfp_url": conf["cfpUrl"],
                    "cfp_deadline": conf["cfpEndDate"],
                    "start_date": conf.get("startDate"),
                    "location": "Online" if conf.get("online") else f"{conf.get('city', '')}, {conf.get('country', '')}".strip(", "),
                    "topics": [],
                })
                if topic not in entry["topics"]:
                    entry["topics"].append(topic)
    return found


def pick(found, today: date) -> tuple[list[dict], list[dict]]:
    """Choose the open and recently closed CFPs. Returns (open, closed)."""
    open_cfps = sorted((c for c in found if c["cfp_deadline"] >= today.isoformat()), key=lambda c: c["cfp_deadline"])
    # Pinned conferences take their place first, then the earliest deadlines fill the rest.
    pinned = [c for c in open_cfps if c["name"].startswith(ALWAYS_KEEP)]
    rest = [c for c in open_cfps if c not in pinned]
    keep = pinned + rest[: MAX_OPEN - len(pinned)]
    chosen = [c for c in open_cfps if c in keep]  # keeps the deadline order
    recent = (today - timedelta(days=90)).isoformat()
    closed = sorted((c for c in found if recent <= c["cfp_deadline"] < today.isoformat()), key=lambda c: c["cfp_deadline"], reverse=True)
    return chosen, closed[:MAX_CLOSED]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--as-of", default=date.today().isoformat(), help="YYYY-MM-DD, usually the workshop date")
    today = date.fromisoformat(parser.parse_args().as_of)
    open_picked, closed_picked = pick(list(fetch(today).values()), today)
    picked = open_picked + closed_picked
    OUT.write_text(json.dumps({
        "source": "https://github.com/tech-conferences/conference-data (confs.tech)",
        "snapshot_date": date.today().isoformat(),
        "open_as_of": today.isoformat(),
        "cfps": picked,
    }, indent=2) + "\n")
    print(f"Wrote {len(picked)} CFPs ({len(open_picked)} open, {len(closed_picked)} closed) to {OUT}")


if __name__ == "__main__":
    main()
