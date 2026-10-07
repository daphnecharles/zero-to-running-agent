"""Structured logs. One JSON line per event, so you can trace any run after the fact."""
import json
from datetime import datetime, timezone

from agent import config


def log_event(run_id: str, stage: str, event: str, **details) -> None:
    record = {
        "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "run_id": run_id,
        "stage": stage,
        "event": event,
        **details,
    }
    config.LOG_DIR.mkdir(exist_ok=True)
    with open(config.LOG_DIR / "runs.jsonl", "a") as f:
        f.write(json.dumps(record) + "\n")
    summary = ", ".join(f"{k}={v}" for k, v in details.items() if not isinstance(v, (list, dict)))
    print(f"[{stage}] {event}" + (f" ({summary})" if summary else ""))
