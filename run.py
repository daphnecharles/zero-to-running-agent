"""Run the agent in your terminal.

    python run.py                                   # uses the sample README
    python run.py https://github.com/owner/repo     # uses your project's README
    python run.py data/injected_readme.md           # the prompt injection example
"""
import sys
import uuid

from langgraph.types import Command

from agent.graph import build_graph


def show_results(state: dict) -> None:
    print("\nRanked opportunities")
    for fit in state.get("scores", []):
        print(f"  {fit['topic_fit']:>2}/10  {fit['route']:<12} {fit['cfp_name']}  (closes {fit['cfp_deadline']})")
    for r in state.get("rejected", []):
        print(f"  rejected     {r['cfp_name']}  ({r['why']})")


def ask_human(drafts: list[dict]) -> list[dict]:
    decisions = []
    for d in drafts:
        print(f"\n--- Draft for {d['cfp_name']} ---\n{d['title']}\n\n{d['abstract']}\n")
        choice = input("Approve, edit or reject? [a/e/r] ").strip().lower()
        if choice.startswith("e"):
            decisions.append({"cfp_id": d["cfp_id"], "action": "edit", "abstract": input("New abstract: ")})
        elif choice.startswith("a"):
            decisions.append({"cfp_id": d["cfp_id"], "action": "approve"})
        else:
            decisions.append({"cfp_id": d["cfp_id"], "action": "reject"})
    return decisions


def main() -> None:
    run_id = uuid.uuid4().hex[:8]
    graph = build_graph()
    config = {"configurable": {"thread_id": run_id}}
    source = sys.argv[1] if len(sys.argv) > 1 else None

    result = graph.invoke({"run_id": run_id, "readme_source": source}, config)
    show_results(result)

    if "__interrupt__" in result:
        drafts = result["__interrupt__"][0].value["drafts"]
        result = graph.invoke(Command(resume=ask_human(drafts)), config)
        approved = [d for d in result["drafts"] if d["status"] == "approved"]
        print(f"\n{len(approved)} draft(s) approved and saved to outputs/. Nothing was submitted.")
    print(f"Run {run_id} done. Logs are in logs/runs.jsonl")


if __name__ == "__main__":
    main()
