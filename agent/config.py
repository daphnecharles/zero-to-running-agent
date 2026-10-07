"""Settings read from environment variables (see .env.example)."""
import os
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

# Which model powers Reason and Act. "claude" (default), "gemini" (free backup) or "mock" (no key needed).
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "claude").strip().lower()
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

# Check stage. Off by default so the workshop works on bad wifi.
CHECK_LINKS_LIVE = os.getenv("CHECK_LINKS_LIVE", "false").lower() == "true"

# Build 2 failure demo. Lets the model suggest conferences from its own memory.
LET_MODEL_SUGGEST = os.getenv("LET_MODEL_SUGGEST", "false").lower() == "true"

# Decide stage thresholds on topic_fit (0 to 10).
APPLY_NOW_MIN = int(os.getenv("APPLY_NOW_MIN", "7"))
MAYBE_LATER_MIN = int(os.getenv("MAYBE_LATER_MIN", "4"))

# Act stage. Cap drafts so free-tier keys don't run out.
MAX_DRAFTS = int(os.getenv("MAX_DRAFTS", "3"))

DATA_DIR = ROOT / "data"
LOG_DIR = ROOT / "logs"
OUTPUT_DIR = ROOT / "outputs"


def today() -> date:
    """The date the Check stage treats as 'now'. Set TODAY=YYYY-MM-DD to rehearse a future day."""
    override = os.getenv("TODAY")
    return date.fromisoformat(override) if override else date.today()
