# From Zero to Running Agent

The starter repo for the All Things Open 2026 deep dive. You'll build an agent that reads your GitHub project, finds conference CFPs that fit it, checks them, ranks them, and drafts a proposal that waits for your approval.

It's a simplified version of the architecture behind the [Sparx Growth Engine](https://github.com/daphnecharles/sparx-growth-engine), built with LangGraph, LangChain, FastAPI and Claude.

## Before the workshop

```bash
git clone https://github.com/daphnecharles/zero-to-running-agent
cd zero-to-running-agent
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/setup_check.py
```

You should see `READY`. If your local Python setup fights you, open the repo in GitHub Codespaces instead. The dev container installs everything for you.

## Pick your model

| Option | When | Set in `.env` |
|---|---|---|
| Claude | Default | `MODEL_PROVIDER=claude` and `ANTHROPIC_API_KEY` |
| Gemini 3.5 Flash Lite | No Claude credits. Free key from [AI Studio](https://aistudio.google.com), no credit card | `MODEL_PROVIDER=gemini` and `GOOGLE_API_KEY` |
| Mock | Neither works | `MODEL_PROVIDER=mock` |

Everything the agent sends to a model is a public README and public CFP listings. If you use the Gemini free tier, read Google's free-tier data terms first.

## Run it

```bash
python run.py                                  # the sample project
python run.py https://github.com/you/your-repo # your own project
uvicorn main:app --reload                      # the API, then open localhost:8000/docs
```

## How it works

Five stages, each with one job.

| Stage | File | What it does |
|---|---|---|
| Gather | `agent/gather.py` | Reads your README and loads CFPs. Plain code, no model |
| Reason | `agent/reason.py` | Claude scores every CFP through tools and a Pydantic schema |
| Check | `agent/check.py` | Code checks that each CFP is real, has a working link and is still open |
| Decide | `agent/decide.py` | Routes each CFP to apply now, maybe later or skip |
| Act | `agent/act.py` | Drafts proposals, then pauses until a human approves, edits or rejects |

`agent/state.py` is the shared state every stage reads and writes, and `agent/graph.py` wires the stages together. Every event is logged to `logs/runs.jsonl`.

The agent never submits anything. Approved drafts are saved to `outputs/` for you to submit yourself.

## Workshop branches

| Branch | What's done |
|---|---|
| `main` | Gather. Where the workshop starts |
| `step-1` | + Reason (end of Build 1) |
| `step-2` | + Check and Decide (end of Build 2) |
| `step-3` | + Act and the API. The finished agent |

Fallen behind? `git stash && git checkout step-N` and keep going.

## Try these

- **Watch the gate work.** Set `LET_MODEL_SUGGEST=true` and the model suggests conferences from memory. Check rejects the ones that don't exist.
- **Prompt injection.** Run `python run.py data/injected_readme.md`. That README hides instructions aimed at the model. See whether they change anything, and notice which stages couldn't be fooled either way.
- **Rehearse another day.** `TODAY=2026-11-02 python run.py` shows what the gate does once more deadlines pass.

## Take it further

- Add podcast or newsletter opportunities as a second Gather source.
- Read every repo in a GitHub account and run the pipeline on each one in parallel with LangGraph's `Send`.
- Replace the code gate with a second model pass for judgment calls, and keep a human at the end.

## CFP data

`data/cfps.json` is a snapshot of the open [confs.tech](https://confs.tech) dataset ([tech-conferences/conference-data](https://github.com/tech-conferences/conference-data)). Refresh it with `python scripts/refresh_fixtures.py --as-of YYYY-MM-DD`.

## License

MIT
