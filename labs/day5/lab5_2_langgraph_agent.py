# %% [markdown]
# # Lab 5.2 — The LangGraph agent: state, nodes, routing, stop rule, persistence, approval interrupt
#
#     plan ─► execute ⟲ (one tool per step, stop after MAX_STEPS) ─► report ─► draft_work_order ─► approval (human)
#       └─► answer_direct (no tools needed, mini model)               └─► END (nothing to act on)

# %%
import sqlite3
import sys
import uuid
from pathlib import Path

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command

ROOT = Path(__file__).resolve().parents[2] if "__file__" in globals() else Path.cwd().parents[1]
sys.path.insert(0, str(ROOT))
from aeroguard.agent import graph as agent  # noqa: E402
from aeroguard.config import STORAGE_DIR  # noqa: E402

# %% 1. State and nodes
print("State fields:", list(agent.AgentState.__annotations__))
print("Nodes:", [n for n in agent.build_graph().get_graph().nodes if not n.startswith("__")])
print("Stop rule: MAX_STEPS =", agent.MAX_STEPS)

# %% 2. Conditional routing: a general question needs no tools -> answer_direct
out = agent.build_graph().invoke({"question": "What does MEL stand for?", "role": "technician", "thread_id": "demo"})
print("General question route:", out["steps"])

# %% 3. Persistence + approval interrupt: the run pauses before the work order is released
DB = STORAGE_DIR / "lab5_2_checkpoints.sqlite"
config = {"configurable": {"thread_id": uuid.uuid4().hex[:8]}}
g1 = agent.build_graph(SqliteSaver(sqlite3.connect(DB, check_same_thread=False)))
g1.invoke({"question": "Engine 2 on N123AB — is it at risk, and what should we do?", "role": "technician",
           "thread_id": config["configurable"]["thread_id"]}, config)
state = g1.get_state(config)
print("Steps:", state.values["steps"])
print("Paused at:", state.next, "| work order:", state.values["work_order"]["work_order_id"],
      state.values["work_order"]["status"])

# %% 4. "Restart the server": a brand-new graph object reads the paused run from SQLite and resumes it
g2 = agent.build_graph(SqliteSaver(sqlite3.connect(DB, check_same_thread=False)))
print("After restart, still waiting at:", g2.get_state(config).next)
final = g2.invoke(Command(resume={"approve": True, "approver": "A. Inspector", "role": "inspector"}), config)
print("Resumed ->", final["work_order"]["status"], "|", final["steps"][-1])
print("Finished:", g2.get_state(config).next == ())
