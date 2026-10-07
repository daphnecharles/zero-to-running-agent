"""Wire the five stages into one graph.

Gather -> Reason -> Check -> Decide -> (apply_now?) -> Draft -> Review (pause) -> Save
"""
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from agent.act import draft_node, review_node, save_node
from agent.check import check_node
from agent.decide import after_decide, decide_node
from agent.gather import cfp_node, readme_node
from agent.reason import reason_node
from agent.state import AgentState


def build_graph(checkpointer=None):
    graph = StateGraph(AgentState)

    graph.add_node("readme", readme_node)
    graph.add_node("cfps", cfp_node)
    graph.add_node("reason", reason_node)
    graph.add_node("check", check_node)
    graph.add_node("decide", decide_node)
    graph.add_node("draft", draft_node)
    graph.add_node("review", review_node)
    graph.add_node("save", save_node)

    graph.add_edge(START, "readme")
    graph.add_edge("readme", "cfps")
    graph.add_edge("cfps", "reason")
    graph.add_edge("reason", "check")
    graph.add_edge("check", "decide")
    graph.add_conditional_edges("decide", after_decide, {"draft": "draft", "end": END})
    graph.add_edge("draft", "review")
    graph.add_edge("review", "save")
    graph.add_edge("save", END)

    # The checkpointer is what lets the graph pause at review and resume later.
    return graph.compile(checkpointer=checkpointer or MemorySaver())
