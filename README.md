# From Zero to Running Agent

The starter repo for the All Things Open 2026 deep dive. You'll build Mic Check, an agent that reads your GitHub project, finds conference CFPs (a CFP is a call for proposals, where a conference invites people to apply to speak) that fit it, checks them, ranks them, and drafts a proposal that waits for your approval.

It's a simplified version of the architecture behind the [Sparx Growth Engine](https://github.com/daphnecharles/sparx-growth-engine), built with LangGraph, LangChain, FastAPI and Claude.

## Before the workshop

You need **Python 3.10 or newer** and git. On macOS the command is `python3`, because there is no plain `python` until your virtual environment is active (so `python -m venv` fails on a fresh Mac). Use `python3` for the `venv` line only. macOS also ships Python 3.9, which is too old (`pip install` fails with `No matching distribution found for langgraph>=1.0`). Check with `python3 --version`. If it is older, install a newer one (`brew install python@3.12`) and use `python3.12` in place of `python` for the `python -m venv` line below. After that, `python` inside the virtual environment is the right version.

macOS or Linux

```bash
git clone https://github.com/daphnecharles/zero-to-running-agent
cd zero-to-running-agent
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/setup_check.py
```

Windows (Command Prompt or PowerShell)

```bat
git clone https://github.com/daphnecharles/zero-to-running-agent
cd zero-to-running-agent
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python scripts/setup_check.py
```

In PowerShell, `.venv\Scripts\activate` can fail with "running scripts is disabled on this system". Allow scripts for this window only with `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, then run `.venv\Scripts\activate` again. Or skip activation and put `.venv\Scripts\` in front of each command, for example `.venv\Scripts\python run.py`.

You should see `READY`. If your local Python setup fights you, [open the repo in GitHub Codespaces](https://codespaces.new/daphnecharles/zero-to-running-agent) instead. The dev container installs everything for you.

Cloned before October 18? Run `git pull`.

Tip: `python scripts/setup_check.py` also works before `pip install`. It reports a Python that is too old first.

## Setting a variable for one run

Some commands in this repo put a variable in front, like `TODAY=2026-10-19 python run.py`. That form only works in macOS and Linux shells. Pick the form for your shell.

| Shell | Form |
|---|---|
| macOS, Linux | `TODAY=2026-10-19 python run.py` |
| Windows PowerShell | `$env:TODAY="2026-10-19"; python run.py` (then `Remove-Item Env:TODAY` when you are done) |
| Windows Command Prompt | `set TODAY=2026-10-19&& python run.py` (then `set TODAY=` when you are done) |
| Any shell | Add `TODAY=2026-10-19` as a line in `.env` (delete it when you are done) |

The same goes for `LET_MODEL_SUGGEST=true` and any other variable in `.env.example`. `cat` and `tail` in EXERCISES.md also have Windows equivalents, which are listed there.

## Pick your model

| Option | When | Set in `.env` |
|---|---|---|
| Claude | Default | `MODEL_PROVIDER=claude` and `ANTHROPIC_API_KEY` |
| Gemini 3.5 Flash Lite | No Claude credits. Free key from [AI Studio](https://aistudio.google.com), no credit card | `MODEL_PROVIDER=gemini` and `GOOGLE_API_KEY` |
| Mock | Neither works | `MODEL_PROVIDER=mock` |

Everything the agent sends to a model is a public README and public CFP listings. If you use the Gemini free tier, read Google's free-tier data terms first.

Mock mode is the quickest way through, but it skips the model code: the tool loop and structured output in Reason, and the drafting in Act, never run. Try a real model when you can.

## Run it

```bash
python run.py                                  # the sample project
TODAY=2026-10-19 python run.py                 # match the dates in EXERCISES.md
python run.py https://github.com/you/your-repo # your own project
uvicorn main:app --reload                      # the API, then open localhost:8000/docs
```

`main.py` is the agent's own web API, built with FastAPI. Start it with the `uvicorn` command, then open [localhost:8000/docs](http://localhost:8000/docs). That page lists every endpoint and lets you start a run, read the drafts and approve or reject them from your browser.

## Exercises

New to this? Work through [EXERCISES.md](EXERCISES.md). It has three guided exercises, one per build, with a time box, the files to open, numbered steps that match the `TODO` comments in the code, the output you should see, common errors and a catch-up command.

Run `python -m pytest` (or just `pytest`) any time. The Check and Decide tests fail on `main` and `step-1` until you finish Exercise 2, and pass on `step-2` and `step-3`.

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
| `step-1` | + Reason (end of Exercise 1) |
| `step-2` | + Check and Decide (end of Exercise 2) |
| `step-3` | + Act and the API. The finished agent |

`step-N` means Exercise N is finished.

Fallen behind? `git stash && git checkout step-N` and keep going.

## Try these

- **Prompt injection.** Run `python run.py data/injected_readme.md`. That README hides instructions aimed at the model. See whether they change anything, and notice which stages couldn't be fooled either way. This only means something with a real model (`claude` or `gemini`). Mock mode scores by keyword overlap, so nothing in the README can influence it. With a real model, Decide trusts the model's score, so an injected 10 would reach `apply_now`. The `<project>` tags in the draft prompt help but are not a guarantee (a README can contain `</project>`). The human approval step is the control that holds.
- **Rehearse another day.** `TODAY=2026-11-02 python run.py` shows what the gate does once more deadlines pass.

## Take it further

- Add podcast or newsletter opportunities as a second Gather source.
- Read every repo in a GitHub account and run the pipeline on each one in parallel with LangGraph's `Send`.
- Replace the code gate with a second model pass for judgment calls, and keep a human at the end.

## CFP data

`data/cfps.json` is a snapshot of the open [confs.tech](https://confs.tech) dataset ([tech-conferences/conference-data](https://github.com/tech-conferences/conference-data)). Refresh it with `python scripts/refresh_fixtures.py --as-of YYYY-MM-DD`.

## License

MIT
