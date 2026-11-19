# %% [markdown]
# # Lab 5.2b — Multi-agent orchestration (instructor demo)
# A supervisor routes work between two specialist agents, then merges their findings:
#
#     supervisor ─► reliability_agent (prediction + history) ─┐
#         ▲                                                   │
#         └──────── compliance_agent (ADs + documents) ◄──────┘ ─► finish

# %%
import sys
from pathlib import Path
from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[2] if "__file__" in globals() else Path.cwd().parents[1]
sys.path.insert(0, str(ROOT))
from aeroguard import llm, safety  # noqa: E402
from aeroguard.agent.tools import TOOLS  # noqa: E402

AGENTS = ["reliability_agent", "compliance_agent"]
MAX_TURNS = 4  # stop criterion for the supervisor


class Route(BaseModel):
    next: Literal["reliability_agent", "compliance_agent", "finish"]


class TeamState(TypedDict, total=False):
    question: str
    tail_number: str
    engine_id: str
    findings: dict[str, str]
    turns: int
    next: str
    final: str


def supervisor(state: TeamState) -> TeamState:
    done = list(state.get("findings", {}))
    turns = state.get("turns", 0) + 1
    if turns > MAX_TURNS or set(AGENTS) <= set(done):
        return {"next": "finish", "turns": turns}
    try:
        route = llm.chat_json([
            {"role": "system", "content": "You supervise two specialists: reliability_agent (engine health and "
             "past write-ups) and compliance_agent (airworthiness directives and manuals). Choose who works next, "
             "or finish when both have reported."},
            {"role": "user", "content": f"Question: {state['question']}\nAlready reported: {done or 'nobody'}"},
        ], Route)
        nxt = route.next
    except ValueError:
        nxt = "finish"
    if nxt in done or nxt == "finish":  # never repeat an agent; never finish before both reported
        nxt = next((a for a in AGENTS if a not in done), "finish")
    print(f"supervisor (turn {turns}) -> {nxt}")
    return {"next": nxt, "turns": turns}


def _summarise(role: str, facts: dict) -> str:
    return llm.chat([{"role": "system", "content": f"You are the {role}. Summarise the facts for the team in two "
                      "sentences. Do not change numbers. Never declare airworthiness."},
                     {"role": "user", "content": str(facts)}], temperature=0)


def reliability_agent(state: TeamState) -> TeamState:
    facts = {"prediction": TOOLS["predict_failure"].invoke({"engine_id": state["engine_id"]}),
             "history": TOOLS["get_maintenance_history"].invoke({"tail_number": state["tail_number"],
                                                                 "ata_chapter": 72})[:4]}
    return {"findings": state.get("findings", {}) | {"reliability_agent": _summarise("reliability engineer", facts)}}


def compliance_agent(state: TeamState) -> TeamState:
    facts = {"compliance": TOOLS["check_compliance"].invoke({"tail_number": state["tail_number"]}),
             "documents": [d["doc_id"] for d in TOOLS["search_documents"].invoke({"query": state["question"]})]}
    return {"findings": state.get("findings", {}) | {"compliance_agent": _summarise("compliance analyst", facts)}}


def finish(state: TeamState) -> TeamState:
    text = llm.chat([{"role": "system", "content": "Combine the specialists' findings into one recommendation of at "
                      "most four sentences. Advisory only."},
                     {"role": "user", "content": str(state.get("findings", {}))}], temperature=0)
    return {"final": safety.enforce_advisory("", text)}


team = StateGraph(TeamState)
for name, fn in [("supervisor", supervisor), ("reliability_agent", reliability_agent),
                 ("compliance_agent", compliance_agent), ("finish", finish)]:
    team.add_node(name, fn)
team.add_edge(START, "supervisor")
team.add_conditional_edges("supervisor", lambda s: s["next"], ["reliability_agent", "compliance_agent", "finish"])
team.add_edge("reliability_agent", "supervisor")
team.add_edge("compliance_agent", "supervisor")
team.add_edge("finish", END)
app = team.compile()

# %%
result = app.invoke({"question": "Engine 2 on N123AB — is it at risk, and what should we do?",
                     "tail_number": "N123AB", "engine_id": "N123AB-E2"})
for agent, text in result["findings"].items():
    print(f"\n[{agent}] {text}")
print("\n[team recommendation]", result["final"])
