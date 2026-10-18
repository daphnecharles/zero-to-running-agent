"""Run this before the workshop. It tells you exactly what to fix.

    python scripts/setup_check.py
"""
import json
import os
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
problems, notes = [], []

if sys.version_info < (3, 10):
    problems.append(f"Python 3.10 or newer is required, you have {sys.version.split()[0]}")

try:
    import fastapi, httpx, langgraph, langchain_core  # noqa: F401,E401
except ImportError as err:
    problems.append(f"Missing package ({err.name}). Run pip install -r requirements.txt")

if not problems:
    from agent import config

    provider = config.MODEL_PROVIDER
    if provider == "claude" and not os.getenv("ANTHROPIC_API_KEY"):
        problems.append("MODEL_PROVIDER is claude but ANTHROPIC_API_KEY isn't set. Add your key to .env, or set MODEL_PROVIDER=mock (no key needed) or MODEL_PROVIDER=gemini in .env")
    elif provider == "gemini" and not os.getenv("GOOGLE_API_KEY"):
        problems.append("MODEL_PROVIDER is gemini but GOOGLE_API_KEY isn't set. Get a free key at aistudio.google.com and add it to .env, or set MODEL_PROVIDER=mock (no key needed)")
    elif provider not in ("claude", "gemini", "mock"):
        problems.append(f"MODEL_PROVIDER must be claude, gemini or mock, not {provider!r}")
    notes.append(f"Model provider is {provider}")

    fixtures = json.loads((config.DATA_DIR / "cfps.json").read_text())
    if fixtures.get("open_as_of", "") < date.today().isoformat():
        notes.append("CFP fixtures are older than today. Run python scripts/refresh_fixtures.py to update them")

    # Dry run of Gather, which needs no model and no network.
    os.environ["MODEL_PROVIDER"] = "mock"
    from agent.gather import build_profile, read_readme

    profile = build_profile(*read_readme(None))
    notes.append(f"Gather works, read the sample project {profile['name']!r}")

for note in notes:
    print(f"  - {note}")
if problems:
    print("\nNot ready yet. Fix these and run this again.")
    for p in problems:
        print(f"  x {p}")
    sys.exit(1)
print("\nREADY. See you at the workshop.")
