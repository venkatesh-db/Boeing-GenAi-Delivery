# %% [markdown]
# # Lab 5.5 — Security II: allowlist, safe mode, roles, audit log, MCP token
# The agent can never close a work order or certify airworthiness, and every decision is recorded.

# %%
import os
import sys
import uuid
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2] if "__file__" in globals() else Path.cwd().parents[1]
sys.path.insert(0, str(ROOT))
from aeroguard import security  # noqa: E402
from aeroguard.agent.graph import build_graph  # noqa: E402
from aeroguard.app import create_app  # noqa: E402

# %% 1. Tool allowlist: only read-only tools exist for the agent; anything else is blocked and audited
print("Allowlist:", sorted(security.TOOL_ALLOWLIST))
for tool in ("check_compliance", "close_work_order", "sign_off_aircraft"):
    try:
        security.check_tool(tool)
        print(f"  {tool:20s} allowed")
    except security.PermissionDenied as err:
        print(f"  {tool:20s} BLOCKED - {err}")

# %% 2. Roles (RBAC)
for role, perms in security.PERMISSIONS.items():
    print(f"{role:10s} {sorted(perms)}")

# %% 3. Safe mode: the agent reports, but takes no action (no work order is drafted)
os.environ["AEROGUARD_SAFE_MODE"] = "1"
tid = "safe-" + uuid.uuid4().hex[:6]
out = build_graph().invoke({"question": "Engine 2 on N123AB — is it at risk?", "role": "technician", "thread_id": tid})
print("\nSafe mode steps:", out["steps"], "| work order:", out.get("work_order"))
os.environ["AEROGUARD_SAFE_MODE"] = "0"

# %% 4. Technician cannot approve; every decision lands in the audit log
client = TestClient(create_app(5))
run = client.post("/agent/run", json={"question": "Engine 2 on N123AB — is it at risk?", "role": "technician"}).json()
tid = run["thread_id"]
r = client.post("/agent/approve", json={"thread_id": tid, "approve": True, "approver": "J. Tech", "role": "technician"})
print("\nTechnician approval ->", r.status_code)
client.post("/agent/approve", json={"thread_id": tid, "approve": False, "approver": "A. Inspector", "role": "inspector"})
print("Audit trail for this run:")
for row in client.get("/agent/audit", params={"thread_id": tid}).json():
    print(f"  {row['time']}  {row['event']:22s} {({k: v for k, v in row.items() if k not in ('time', 'event', 'thread_id')})}")
denied = [r for r in security.read_audit(limit=500) if r["event"] == "permission_denied"]
print("Permission-denied events recorded:", len(denied))

# %% 5. MCP server authentication: see Lab 5.3 (a wrong token is refused by the server)
