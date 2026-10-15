# Exercises

Three exercises turn this repo from "Gather only" into the finished agent. Each one gives you a few stub files with `TODO` comments. Every `TODO` points back to a numbered step in this file, for example `# TODO 2 (see EXERCISES.md, Exercise 1, step 2)`.

| Exercise | What you build | Hands-on time | Files | Catch-up branch |
|---|---|---|---|---|
| 1. Reason | Tools and a schema so the model scores every CFP | 20 minutes | `agent/reason.py` | `step-1` |
| 2. Check and Decide | A plain-code gate and routing | 15 minutes | `agent/check.py`, `agent/decide.py` | `step-2` |
| 3. Act and ship | Drafting and the human pause | 20 minutes | `agent/act.py` | `step-3` |

The times are hands-on minutes only. They cover your own typing and running, not the talk and walkthrough around each exercise.

You are not meant to finish every step perfectly. If the timer runs out, use the catch-up command and keep going. Nobody gets left behind.

## Before you start

1. You are on the `main` branch in the repo folder, with your virtual environment active.
2. `python scripts/setup_check.py` prints `READY`.
3. You know which model you are using. Mock mode needs no key and works for every exercise. A real model (Claude or Gemini) shows you more, and each exercise says what.

**The expected output below is from mock mode.** It was captured with `TODAY=2026-10-19`, the workshop day. If you run on another day, some deadlines will be judged differently. To match this file exactly, put `TODAY=2026-10-19` in front of any command, for example `TODAY=2026-10-19 python run.py`. Run IDs (like `416826d2`) and file paths are different on every run.

**About `pytest`.** `tests/test_check_decide.py` checks the Check and Decide code. On `main` and `step-1` it fails on purpose, because that code does not exist yet. You will see `4 failed, 2 passed`. Think of it as a progress bar. It turns green when Exercise 2 is done, and stays green on `step-2` and `step-3`.

**Stuck on anything?** Every exercise ends with a catch-up command and a tip for asking Claude Code to explain a `TODO`.

---

## Exercise 1. Reason (20 minutes hands-on)

**Done when.** `python run.py` shows a score for every conference.

**Goal.** Give the model two tools to read the facts Gather collected, and a schema to answer in, so the next stage gets scores it can use instead of a paragraph.

**Open.** `agent/reason.py`. It is the only file you edit. Read `mock_fits` in the same file first. It shows the shape of one score.

**Where you start.** `python run.py` on `main` prints your project and the open CFPs, and says `Reason isn't built yet`. There is no ranking, because nothing has scored anything.

### Steps

**1. Write the two tools (TODO 1, in `make_tools`).**
Write two functions decorated with `@tool` named `get_project_profile` and `list_open_cfps`. Each returns JSON text. Then return both from `make_tools` as a list.

```python
@tool
def get_project_profile() -> str:
    """One clear sentence. This text is the only thing the model reads to decide when to call you."""
    return json.dumps(...)   # which key of state holds the profile?
```

*Why.* The model never sees your Python. It sees the tool's name and docstring, so the docstring is a prompt. `state` is available inside the functions because they are defined inside `make_tools`.

Check your work (works in every mode).

```bash
python -c "from agent.reason import make_tools; print([t.name for t in make_tools({'profile': {}, 'opportunities': []})])"
```

```text
['get_project_profile', 'list_open_cfps']
```

**2. Write the schema (TODO 2, class `CFPFit`).**
Replace `pass` with six fields. `cfp_id`, `cfp_name` and `reason` are strings. `topic_fit` is an integer from 0 to 10. `audience_level` is one of `"beginner"`, `"mid"`, `"advanced"`. `format` is one of `"talk"`, `"workshop"`, `"lightning"`.

```python
topic_fit: int = Field(ge=0, le=10, description="...")
audience_level: Literal["beginner", "mid", "advanced"]
```

*Why.* A schema turns the model's answer into data. If it returns a score of 11 or invents an audience level, Pydantic raises an error right away instead of letting a bad value travel downstream.

Check your work.

```bash
python -c "from agent.reason import CFPFit; print(CFPFit(cfp_id='x', cfp_name='X', topic_fit=7, audience_level='mid', format='talk', reason='ok'))"
```

```text
cfp_id='x' cfp_name='X' topic_fit=7 audience_level='mid' format='talk' reason='ok'
```

Now break it on purpose by changing `topic_fit=7` to `topic_fit=11`. You should get a `ValidationError` that names the field.

```text
pydantic_core._pydantic_core.ValidationError: 1 validation error for CFPFit
topic_fit
  Input should be less than or equal to 10 [type=less_than_equal, input_value=11, input_type=int]
```

**3. Write the Reason node (TODO 3, in `reason_node`).**
Work through the sub-steps in order. Delete the `print("Reason isn't built yet...")` and the placeholder `return` when you are done.

- **3a. Mock mode.** When `llm is None`, call `mock_fits(state)`, log it with `log_event(state["run_id"], "reason", "scored", mode="mock", count=...)`, and return `{"scores": fits}`. *Why.* This is what lets people with no API key keep going.
- **3b. Messages.** Build `messages = [SystemMessage(SYSTEM), HumanMessage(task)]`. The `task` asks the model to score every CFP. When `config.LET_MODEL_SUGGEST` is true, add `SUGGEST` to it. *Why.* `SYSTEM` tells the model to treat README text as data. `SUGGEST` powers the failure demo in Exercise 2.
- **3c. Tool loop.** Bind the tools with `llm.bind_tools(tools)`. Loop at most twice. Each time, call the model, append its reply to `messages`, stop if `response.tool_calls` is empty, and otherwise run each call and append a `ToolMessage(content=result, tool_call_id=call["id"])`. Log each one with `log_event(..., "reason", "tool_call", tool=call["name"])`. *Why.* Two rounds is plenty here. A cap means a confused model can never loop forever.
- **3d. Ask for the answer as data.** Append `HumanMessage("Now return your scores for every CFP.")`, then call `llm.with_structured_output(FitBatch, method="json_schema").invoke(messages)`. *Why.* One batched call for all CFPs uses far fewer requests than one call each, which matters on free tiers. `method="json_schema"` is needed because Claude Sonnet 5.5 does not support the default method.
- **3e. Return.** Log `scored` with `mode=config.MODEL_PROVIDER` and the count, then return `{"scores": [fit.model_dump() for fit in batch.fits]}`.

### Run it

```bash
python run.py
```

Expected output in mock mode.

```text
[gather] profile_built (project=pgsnap)
[gather] cfps_loaded (count=12, snapshot=2026-10-07)
[reason] scored (mode=mock, count=12)
Check isn't built yet. That's Exercise 2.

Ranked opportunities
   2/10  -            Voxxed Days Zürich
  10/10  -            Build It Summit
   8/10  -            Java Day Istanbul
   2/10  -            Digital Crafts Day
   4/10  -            AI Conf Asia
   4/10  -            SCaLE
   2/10  -            INTED
   4/10  -            Big Data Europe
   0/10  -            UXLx: User Experience Lisbon
   4/10  -            AI Con USA
   8/10  -            Global Summit on Data Science and Cloud Computing
   2/10  -            GENAIX: Global Generative & Agentic AI Summit
Run 416826d2 done. Logs are in logs/runs.jsonl
```

**Mock mode only runs step 3a.** Your tools, schema and model calls (steps 1, 2 and 3b to 3e) never run without a model. To exercise them, set `MODEL_PROVIDER=claude` or `gemini` in `.env` and run again. You should also see the model ask for both tools.

```text
[reason] tool_call (tool=get_project_profile)
[reason] tool_call (tool=list_open_cfps)
[reason] scored (mode=claude, count=12)
```

The scores will differ from the mock ones. They come from a model reading the README, not from keyword matching. There is no `route` yet, so the middle column shows `-`.

### Common errors and fixes

| You see | What it means | Fix |
|---|---|---|
| `Reason isn't built yet. That's Exercise 1.` still prints, and no ranking appears | The stub is still in place | Delete the `print` and placeholder `return`. In mock mode, finish step 3a |
| `MODEL_PROVIDER is claude but ANTHROPIC_API_KEY isn't set` (or `GOOGLE_API_KEY` for Gemini) from `setup_check.py` | Your key is missing from `.env` | Open `.env`, paste the key after the `=` with no quotes, save, run `python scripts/setup_check.py` again. No key yet? Set `MODEL_PROVIDER=mock` |
| `This API key is not scoped to a workspace` | A Claude key created outside a workspace | In the Claude Console, create the key inside a workspace and replace it in `.env` |
| `429 RESOURCE_EXHAUSTED` from Gemini | The free tier allows about 15 requests per minute | The repo waits and retries by itself (`Gemini free tier is rate limited, waiting...`). If it still fails, wait a minute and avoid running back to back. A full run uses 4 to 6 requests |
| `ValidationError: ... CFPFit` naming a field | A value broke your schema, such as a score above 10 or an audience level you did not list | Read the field name on line 2 of the error. Make your `Literal` values match the TODO exactly |
| `ModuleNotFoundError: No module named 'agent'` or `'langgraph'` | You are in the wrong folder, or the virtual environment is off | `cd` to the repo root and run `source .venv/bin/activate` |
| `Your local changes ... would be overwritten by checkout` | You ran `git checkout step-1` with unsaved edits | Use the full catch-up command below, which stashes first |
| `CONFLICT` after `git stash pop` | Your edits clash with the finished code | You do not need to pop. The step branch already has the finished code. If you already popped, run `git reset --hard` to go back to the finished version (git keeps your stash when a pop conflicts), then `git stash drop` when you no longer need it. To keep a copy of your own attempt, run `cp agent/reason.py ~/my_reason.py` before catching up |

### Catch up

```bash
git stash && git checkout step-1
```

This saves your edits out of the way and switches you to a branch where Exercise 1 is finished.

### Tip

Not sure what a `TODO` wants? Ask Claude Code. For example, "Explain TODO 3 in agent/reason.py and what it should return". Ask it to explain, not to write the answer, and you will learn more.

### Stretch goal (for early finishers)

Add a third tool, `get_cfp_details(cfp_id)`, that returns one CFP from `state["opportunities"]` as JSON text. If the id is not found, return a short error message as JSON instead of crashing. Add it to the list that `make_tools` returns, then run the check from step 1 again. You should see three names.

```text
['get_project_profile', 'list_open_cfps', 'get_cfp_details']
```

With a real model, the model decides whether it needs the tool. You can nudge it by telling it, in your step 3b message, that it may look up any CFP by id.

---

## Exercise 2. Check and Decide (15 minutes hands-on)

**Done when.** `pytest` shows `6 passed`, and `LET_MODEL_SUGGEST=true python run.py` shows the gate rejecting AgentCon Atlantis 2026.

**Goal.** Write a gate made of plain code that rejects invented, unreachable and closed conferences, then route what is left into apply now, maybe later or skip.

**Start from.** Your finished Exercise 1, or `git stash && git checkout step-1`.

**Open.** `agent/check.py` and `agent/decide.py`. Read `tests/test_check_decide.py` too. It describes exactly what each function must do.

**Why plain code.** Every question here has a yes or no answer. Code gives the same answer every time, so the model is never asked. The gate checks facts, not fit. Whether a conference suits you is still a judgment call, which is why a person approves at the end.

### Steps

**1. Three yes or no checks (TODO 1a, 1b, 1c in `check.py`).** Each function currently returns `True` no matter what.

- **1a. `is_real(cfp_id, known)`.** Is the id in our source data? `known` is a dict keyed by CFP id. *Why.* A model can invent a conference that sounds perfect.
- **1b. `link_works(url)`.** Return `False` when `url` is empty or its scheme is not `https`. Use `urlparse(url).scheme`. If `config.CHECK_LINKS_LIVE` is on, also request the URL with `httpx.head(url, timeout=8, follow_redirects=True)`. Some sites refuse `HEAD` (status 405), so retry with `httpx.get`. Treat a status below 400 as working, and any `httpx.HTTPError` as not working. *Why.* A proposal for a dead link is wasted work. Live requests are off by default so the workshop survives bad wifi.
- **1c. `deadline_open(deadline, today)`.** The deadline is text like `"2026-10-31"` and `today` is a `date`. Convert with `date.fromisoformat(...)` and compare. A deadline of today is still open. *Why.* Last year's deadline sounds just as confident as this year's.

**2. The Check node (TODO 2, `check_node`).**
Build `known = {cfp["id"]: cfp for cfp in state["opportunities"]}` and `today = config.today()`. For each fit in `state["scores"]`, run the three checks **in this order**. Keep the ones that pass and add `cfp_url` and `cfp_deadline` taken from the source data, not from the model's answer. Put the rest in a `rejected` list with a short reason, and log each with `log_event(..., "check", "rejected", cfp=..., why=...)`. Return `{"scores": passed, "rejected": rejected}`, and log a `done` event with both counts. Remove the `print("Check isn't built yet...")`.

*Why.* Facts must come from your data because the model's version of a deadline might be wrong. Check `is_real` first. For an invented conference, `known.get(...)` is `None`, and reading a field from `None` crashes.

**3. Decide (TODO 3a, 3b, 3c in `decide.py`).**

- **3a. `route_for(topic_fit)`.** Return `"apply_now"` when the score is at least `config.APPLY_NOW_MIN`, `"maybe_later"` when it is at least `config.MAYBE_LATER_MIN`, otherwise `"skip"`. *Why.* Thresholds live in config, so you can tune them without touching code.
- **3b. `decide_node(state)`.** Add `"route"` to every fit, sort by `topic_fit` with the highest first, log how many landed in each bucket, and return `{"scores": scores}`.
- **3c. `after_decide(state)`.** This is a conditional edge. Return `"draft"` if any fit is `apply_now`, otherwise `"end"`. *Why.* Only the best opportunities go on to drafting. Everything else stops with its reason attached.

### Run it

First the tests. They should go from red to green.

```bash
pytest
```

Before you start, you will see this.

```text
FAILED tests/test_check_decide.py::test_invented_conference_is_not_real - Ass...
FAILED tests/test_check_decide.py::test_link_must_be_https - AssertionError: ...
FAILED tests/test_check_decide.py::test_deadline - AssertionError: assert not...
FAILED tests/test_check_decide.py::test_routes - AssertionError: assert 'skip...
4 failed, 2 passed in 0.04s
```

When you are done, you should see this.

```text
......                                                                   [100%]
6 passed in 0.04s
```

Now the agent.

```bash
python run.py
```

Expected output in mock mode.

```text
[gather] profile_built (project=pgsnap)
[gather] cfps_loaded (count=12, snapshot=2026-10-07)
[reason] scored (mode=mock, count=12)
[check] rejected (cfp=AI Con USA, why=deadline passed on 2026-10-18)
[check] rejected (cfp=Global Summit on Data Science and Cloud Computing, why=deadline passed on 2026-10-15)
[check] rejected (cfp=GENAIX: Global Generative & Agentic AI Summit, why=deadline passed on 2026-10-15)
[check] done (passed=9, rejected=3)
[decide] routed (apply_now=2, maybe_later=3, skip=4)
Act isn't built yet. That's Exercise 3.

Ranked opportunities
  10/10  apply_now    Build It Summit  (closes 2026-10-31)
   8/10  apply_now    Java Day Istanbul  (closes 2026-10-31)
   4/10  maybe_later  AI Conf Asia  (closes 2026-11-01)
   4/10  maybe_later  SCaLE  (closes 2026-11-01)
   4/10  maybe_later  Big Data Europe  (closes 2026-11-23)
   2/10  skip         Voxxed Days Zürich  (closes 2026-10-23)
   2/10  skip         Digital Crafts Day  (closes 2026-10-31)
   2/10  skip         INTED  (closes 2026-11-19)
   0/10  skip         UXLx: User Experience Lisbon  (closes 2026-11-30)
  rejected     AI Con USA  (deadline passed on 2026-10-18)
  rejected     Global Summit on Data Science and Cloud Computing  (deadline passed on 2026-10-15)
  rejected     GENAIX: Global Generative & Agentic AI Summit  (deadline passed on 2026-10-15)
```

The ranked list now has a route and a closing date, and the rejected list explains itself.

### Watch the gate work

Let the model suggest conferences from its own memory, then see what the gate does with them.

```bash
LET_MODEL_SUGGEST=true python run.py
```

Expected output in mock mode. Look for the fourth `rejected` line.

```text
[gather] profile_built (project=pgsnap)
[gather] cfps_loaded (count=12, snapshot=2026-10-07)
[reason] scored (mode=mock, count=13)
[check] rejected (cfp=AI Con USA, why=deadline passed on 2026-10-18)
[check] rejected (cfp=Global Summit on Data Science and Cloud Computing, why=deadline passed on 2026-10-15)
[check] rejected (cfp=GENAIX: Global Generative & Agentic AI Summit, why=deadline passed on 2026-10-15)
[check] rejected (cfp=AgentCon Atlantis 2026, why=not in source data, the model may have invented it)
[check] done (passed=9, rejected=4)
```

Reason scored 13 conferences instead of 12. The extra one, "AgentCon Atlantis 2026", is made up, and the model gave it a 9 out of 10 in the same confident tone as the real ones. Check rejected it because its id is not in `data/cfps.json`.

With a real model, the suggestions are real conferences that are not in our data. The gate still rejects them. "Not in source data" means we could not verify it here, not that it does not exist anywhere.

You can also rehearse another day, which closes more deadlines.

```bash
TODAY=2026-11-02 python run.py
```

### Common errors and fixes

| You see | What it means | Fix |
|---|---|---|
| Tests still fail | A function still returns the stub value | Run `pytest -x` and read the first failure. It names the function and the assertion |
| `link_works(None)` returns `True` | You skipped the empty check | Test `not url` before parsing |
| `deadline_open` always returns `True` | The stub is still in place | Replace the stub's `return True` with a real comparison |
| `TypeError: '>=' not supported between instances of 'str' and 'datetime.date'` | You compared text to a date | Convert the deadline with `date.fromisoformat(...)` first |
| `TypeError: 'NoneType' object is not subscriptable` in `check_node` | You read a field from an unknown CFP | Run `is_real` before anything that uses `known[...]` |
| Everything is rejected as `deadline passed` | `TODAY` is set far in the future | Run `unset TODAY`, or set `TODAY=2026-10-19` |
| `routed (apply_now=0 ...)` and every row says `skip` | `route_for` still returns `"skip"` | Finish step 3a. Check the thresholds in `agent/config.py` |
| Live link checks are slow or fail | Conference wifi | Leave `CHECK_LINKS_LIVE=false`, which is the default |
| Provider or git errors | Same as Exercise 1 | See the table in Exercise 1 |

### Catch up

```bash
git stash && git checkout step-2
```

### Tip

Ask Claude Code, for example "Explain TODO 2 in agent/check.py and why is_real runs first". Or paste a failing `pytest` message and ask what it means before you ask for a fix.

### Stretch goal (for early finishers)

Add a fourth check to the gate. Reject a CFP when the conference itself has already started. Each CFP in `data/cfps.json` has a `start_date` such as `"2027-03-09"`, and a few may be missing it, so treat a missing date as fine.

```python
def starts_in_future(start_date: str | None, today: date) -> bool:
    ...
```

Call it from `check_node` **before** the deadline check, with a reason of your own such as `conference already started on <date>`. Why before? A deadline always passes before the event starts, so if the deadline check came first it would catch every CFP and you would never see your new reason. Add a test to `tests/test_check_decide.py` too. Then rehearse a day when one conference has started.

```bash
TODAY=2026-10-20 python run.py
```

Look for the Global Summit on Data Science and Cloud Computing, which started on 2026-10-19. Your wording will differ.

```text
[check] rejected (cfp=Global Summit on Data Science and Cloud Computing, why=conference already started on 2026-10-19)
```

---

## Exercise 3. Act and ship (20 minutes hands-on)

**Done when.** A draft waits for your approval, and the one you approve is saved in `outputs/`.

**Goal.** Draft a proposal for each apply now conference, pause for a human to approve, edit or reject, and save only what they approve. If you have time, try the web API that wraps the whole agent.

**Start from.** Your finished Exercise 2, or `git stash && git checkout step-2`.

**Open.** `agent/act.py`. Also read `agent/graph.py` and `main.py`. You only edit `act.py`. `main.py` is already written and is the web API (see below).

**The pause comes after drafting.** The graph runs `draft`, then `review`, then `save`. The `review` step calls `interrupt(...)`. The graph saves its state and stops there, and nothing leaves the system. It only continues when a person answers. The agent never submits anything. Approved drafts are saved to `outputs/` for you to submit yourself.

### Steps

**1. Draft (TODO 1, `draft_node`).**
Take the fits routed `apply_now` (at most `config.MAX_DRAFTS`) from `state["scores"]`. For each one, make a `Draft`. In mock mode (`llm is None`) build a placeholder with a title and abstract from the project name and the fit. Otherwise write a prompt with the conference, the reason it fits, and `profile["summary"]` inside `<project>` tags, then call `llm.with_structured_output(Draft, method="json_schema").invoke([...])`. Append a dict to `drafts` with the fit's id, name, url and deadline, the draft's fields, and `"status": "waiting_for_approval"`. Log a `drafted` event and return `{"drafts": drafts}`.

*Why.* The project text came from a stranger's README, so it goes in tags and `SYSTEM` tells the model to treat it as data. Capping drafts stops free-tier keys running out.

**2. The pause (TODO 2, `review_node`).**
Call `interrupt({"drafts": state["drafts"]})`. It returns whatever the human sends when the graph resumes. Log a `reviewed` event with the number of decisions and return `{"decisions": decisions}`.

```python
decisions = interrupt({"drafts": state["drafts"]})
```

*Why.* This one line is the most important safety feature in the project. The checkpointer in `graph.py` is what lets the graph remember where it stopped.

**3. Save (TODO 3, `save_node`).**
Index the decisions by `cfp_id`. For each draft, find its decision. If there is none, treat it as a reject. For `edit`, replace the abstract with the one the human supplied. Set the status to `rejected` or `approved`. Write the approved ones to `outputs/approved_<run_id>.md` (create the folder if needed), log a `saved` event, and return `{"drafts": drafts}`. Never submit anything.

*Why.* Defaulting to reject means a missing answer can never publish something. This is the safe default.

### Run it in the terminal

```bash
python run.py
```

You will be asked about each draft. Answer `a` to approve, `e` to edit (then type a new abstract), or `r` to reject. Expected output in mock mode, answering `a` for the first draft and `e` for the second.

```text
[gather] profile_built (project=pgsnap)
[gather] cfps_loaded (count=12, snapshot=2026-10-07)
[reason] scored (mode=mock, count=12)
[check] rejected (cfp=AI Con USA, why=deadline passed on 2026-10-18)
[check] rejected (cfp=Global Summit on Data Science and Cloud Computing, why=deadline passed on 2026-10-15)
[check] rejected (cfp=GENAIX: Global Generative & Agentic AI Summit, why=deadline passed on 2026-10-15)
[check] done (passed=9, rejected=3)
[decide] routed (apply_now=2, maybe_later=3, skip=4)
[act] drafted (count=2)

Ranked opportunities
  10/10  apply_now    Build It Summit  (closes 2026-10-31)
   8/10  apply_now    Java Day Istanbul  (closes 2026-10-31)
   4/10  maybe_later  AI Conf Asia  (closes 2026-11-01)
   4/10  maybe_later  SCaLE  (closes 2026-11-01)
   4/10  maybe_later  Big Data Europe  (closes 2026-11-23)
   2/10  skip         Voxxed Days Zürich  (closes 2026-10-23)
   2/10  skip         Digital Crafts Day  (closes 2026-10-31)
   2/10  skip         INTED  (closes 2026-11-19)
   0/10  skip         UXLx: User Experience Lisbon  (closes 2026-11-30)
  rejected     AI Con USA  (deadline passed on 2026-10-18)
  rejected     Global Summit on Data Science and Cloud Computing  (deadline passed on 2026-10-15)
  rejected     GENAIX: Global Generative & Agentic AI Summit  (deadline passed on 2026-10-15)

--- Draft for Build It Summit ---
Shipping pgsnap: lessons for Build It Summit

[mock draft] A talk on pgsnap. Mock score from topic overlap: ['data', 'devops', 'opensource']

Approve, edit or reject? [a/e/r]
--- Draft for Java Day Istanbul ---
Shipping pgsnap: lessons for Java Day Istanbul

[mock draft] A talk on pgsnap. Mock score from topic overlap: ['data', 'opensource']

Approve, edit or reject? [a/e/r] New abstract: [act] reviewed (decisions=2)
[act] saved (approved=2, path=/Users/you/zero-to-running-agent/outputs/approved_80a9b6ba.md)

2 draft(s) approved and saved to outputs/. Nothing was submitted.
Run 80a9b6ba done. Logs are in logs/runs.jsonl
```

Open the file it saved (use your own run ID).

```bash
cat outputs/approved_80a9b6ba.md
```

```text
## Build It Summit
Submit by 2026-10-31 at https://builditsummit.com/call-for-speakers

### Shipping pgsnap: lessons for Build It Summit

[mock draft] A talk on pgsnap. Mock score from topic overlap: ['data', 'devops', 'opensource']

## Java Day Istanbul
Submit by 2026-10-31 at https://bilgi711.wixforms.com/f/7479128754174821378

### Shipping pgsnap: lessons for Java Day Istanbul

A tighter abstract about copy-on-write snapshots.
```

Every event is also logged. Each line is one JSON object, so you can trace a run afterwards.

```bash
tail -n 3 logs/runs.jsonl
```

```text
{"time": "2026-10-15T18:27:51+00:00", "run_id": "80a9b6ba", "stage": "act", "event": "drafted", "count": 2}
{"time": "2026-10-15T18:27:51+00:00", "run_id": "80a9b6ba", "stage": "act", "event": "reviewed", "decisions": 2}
{"time": "2026-10-15T18:27:51+00:00", "run_id": "80a9b6ba", "stage": "act", "event": "saved", "approved": 2, "path": "/Users/you/zero-to-running-agent/outputs/approved_80a9b6ba.md"}
```

### If you have time. Put it behind the API

`main.py` is the agent's own web API, built with FastAPI. It runs the same graph you just ran in the terminal, but over HTTP, so other programs can start runs and review drafts. FastAPI also builds a page where you can try every endpoint from your browser.

```bash
uvicorn main:app --reload
```

Open http://localhost:8000/docs. Then try the three endpoints in order. For each one, click the endpoint, click **Try it out**, fill in the fields, and click **Execute**.

1. **`POST /runs`** starts a run. Use `{}` as the body for the sample project, or `{"repo_url": "https://github.com/you/your-repo"}`. The run goes until the pause and returns this (shortened).

   ```json
   {
     "run_id": "563d9c62",
     "waiting_for_review": true,
     "scores": [
       {
         "cfp_id": "build-it-summit-2026",
         "cfp_name": "Build It Summit",
         "topic_fit": 10,
         "audience_level": "mid",
         "format": "talk",
         "reason": "Mock score from topic overlap: ['data', 'devops', 'opensource']",
         "cfp_url": "https://builditsummit.com/call-for-speakers",
         "cfp_deadline": "2026-10-31",
         "route": "apply_now"
       },
       "..."
     ],
     "rejected": [ "..." ]
   }
   ```

   Copy the `run_id`.

2. **`GET /runs/{run_id}/drafts`** lists the drafts waiting for you. Paste your `run_id` into the path field. Note `"paused": true` and each draft's `"status": "waiting_for_approval"`.

   ```json
   {
     "run_id": "563d9c62",
     "paused": true,
     "drafts": [
       {
         "cfp_id": "build-it-summit-2026",
         "cfp_name": "Build It Summit",
         "cfp_url": "https://builditsummit.com/call-for-speakers",
         "cfp_deadline": "2026-10-31",
         "title": "Shipping pgsnap: lessons for Build It Summit",
         "abstract": "[mock draft] A talk on pgsnap. Mock score from topic overlap: ['data', 'devops', 'opensource']",
         "status": "waiting_for_approval"
       }
     ]
   }
   ```

3. **`POST /runs/{run_id}/review`** sends your decisions and resumes the graph. The body is a list. Use the `cfp_id` values from step 2.

   ```json
   [
     {"cfp_id": "build-it-summit-2026", "action": "approve"},
     {"cfp_id": "java-day-istanbul-2027", "action": "reject"}
   ]
   ```

   The response lists the drafts again with their new statuses, `approved` and `rejected`. The approved one is now in `outputs/`.

Try sending the same review a second time. You should get a `409` with `This run isn't waiting for review`, because the graph already finished. A run ID that does not exist gets a `404` with `No run with that id`.

Runs live in the server's memory. If the server restarts (including when `--reload` notices you saved a file), old run IDs are forgotten. Start a new run.

### If you have time. Finish by running it on your own repo

Point the agent at a public GitHub project of yours. This reads the README from `raw.githubusercontent.com`.

```bash
python run.py https://github.com/you/your-repo
```

Use a real model for this one if you can, because mock scores only count keyword overlap. Read the top apply now draft and decide honestly whether you would submit it. If the README cannot be fetched, the agent tells you and falls back to the sample.

```text
Couldn't fetch a README from https://github.com/you/does-not-exist, using the sample README instead.
```

You can do the same through the API by putting your URL in `repo_url` in `POST /runs`.

### Common errors and fixes

| You see | What it means | Fix |
|---|---|---|
| `EOFError: EOF when reading a line` | `run.py` has no terminal to ask you questions in | Run it in an interactive terminal, not piped or in the background |
| `Act isn't built yet. That's Exercise 3.` still prints, and no draft prompt appears | The stub is still in place | Finish step 1 and delete the `print` and the placeholder `return` |
| The run finishes without ever asking you | `review_node` is not calling `interrupt(...)` | Finish step 2 |
| A `422` response from `/review` | The body is not a list of decisions | Send `[ {...}, {...} ]`, with each item holding `cfp_id` and `action` |
| `409` `This run isn't waiting for review` | The run already finished, or the server restarted | Start a new run with `POST /runs` |
| `404` `No run with that id` | Wrong id, or the server restarted | Copy the `run_id` from a fresh `POST /runs` |
| `address already in use` when starting uvicorn | Another server is on port 8000 | Stop it with Ctrl+C, or run `uvicorn main:app --reload --port 8001` |
| `ValidationError` for `Draft` | The model returned a field of the wrong type | Read the field name in the error. Check `Draft` matches the TODO |
| Provider, key, rate limit or git errors | Same as Exercise 1 | See the table in Exercise 1 |

### Catch up

```bash
git stash && git checkout step-3
```

This is the finished agent.

### Tip

Ask Claude Code, for example "Explain TODO 2 in agent/act.py and what happens to the graph when interrupt is called". It is also good at explaining `main.py` line by line.

### Stretch goal (for early finishers)

Put the CFP deadline into each draft's title, so a reviewer sees it at a glance. After you build a draft's dict in `draft_node`, add the deadline to its title.

```python
drafts[-1]["title"] += f" ..."   # which fit field holds the deadline?
```

Run `python run.py` again. In mock mode each draft heading should now look like this, and the approved file in `outputs/` shows the same title.

```text
Shipping pgsnap: lessons for Build It Summit (submit by 2026-10-31)
```

---

## After the exercises

Take it further with the ideas in the README. Add podcasts or newsletters as a second Gather source, run the pipeline on every repo in a GitHub account in parallel, or replace the code gate with a second model pass for judgment calls and keep a human at the end.
