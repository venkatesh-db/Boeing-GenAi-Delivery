# %% [markdown]
# # Lab 5.4 — Capstone: "Engine 2 on N123AB — at risk?"
# One question -> prediction, history, cited evidence, compliance status and a draft work order awaiting approval.
# Runs the Day 5 API in-process (TestClient); the Streamlit "Agent" tab calls the same endpoints.

# %%
import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2] if "__file__" in globals() else Path.cwd().parents[1]
sys.path.insert(0, str(ROOT))
from aeroguard.app import create_app  # noqa: E402

client = TestClient(create_app(5))

# %% 1. Run the agent
run = client.post("/agent/run", json={"question": "Engine 2 on N123AB — is it at risk, and what should we do?",
                                      "role": "technician"}).json()
print("Steps:", run["steps"])
print("\n" + run["report"])
print("\nCitations:", [(c["source_id"], c["doc_id"]) for c in run["citations"]])
wo = run["work_order"]
print("\nDraft work order:", wo["work_order_id"], wo["status"])
for task in wo["tasks"]:
    print("  -", task)
print("References:", wo["references"], "| pending approval:", run["pending_approval"])

# %% 2. Rubric check: does the capstone return everything?
report = run["report"]
checks = {
    "prediction (risk)": "### Risk" in report and "predict_failure: ok" in run["steps"],
    "maintenance history": "### History" in report and "get_maintenance_history: ok" in run["steps"],
    "cited evidence": bool(run["citations"]),
    "compliance status": "### Compliance" in report and "check_compliance: ok" in run["steps"],
    "draft work order awaiting approval": wo["status"] == "draft" and run["pending_approval"],
}
# ML numbers unchanged: every number the model produced appears exactly in the report
from aeroguard import pdm  # noqa: E402

pred = pdm.predict("N123AB-E2")
numbers = [str(pred["predicted_rul_cycles"]), f"{pred['failure_probability_30_cycles']:.0%}"] + \
          [d.split(" is ")[1].split()[0] for d in pred["drivers"]]
checks["ML numbers unchanged by the LLM"] = all(n in report for n in numbers)
for name, ok in checks.items():
    print(f"{'PASS' if ok else 'FAIL'}  {name}")

# %% 3. Human approval: a technician cannot approve, an inspector can
tid = run["thread_id"]
deny = client.post("/agent/approve", json={"thread_id": tid, "approve": True, "approver": "J. Tech", "role": "technician"})
print("\nTechnician approves ->", deny.status_code, deny.json()["error"]["message"])
ok = client.post("/agent/approve", json={"thread_id": tid, "approve": True, "approver": "A. Inspector",
                                         "role": "inspector"}).json()
print("Inspector approves ->", ok["work_order"]["status"], "| still pending:", ok["pending_approval"])
