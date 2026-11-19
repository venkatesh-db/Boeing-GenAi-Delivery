# %% [markdown]
# # Lab 3.2 — API contracts and validation
# Bad inputs must get a clear 4xx error in ONE standard shape - never a crash.
# Uses FastAPI's TestClient, so no server and no LLM call are needed.

# %%
import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2] if "__file__" in globals() else Path.cwd().parents[1]
sys.path.insert(0, str(ROOT))
from aeroguard.app import create_app  # noqa: E402

client = TestClient(create_app(3))

# %% Every case below is invalid on purpose
cases = [
    ("bad tail number", "post", "/chat", {"json": {"message": "hi", "tail_number": "XYZ123"}}),
    ("empty message", "post", "/chat", {"json": {"message": ""}}),
    ("message too long (4,001 chars)", "post", "/chat", {"json": {"message": "x" * 4001}}),
    ("body over 64 KB", "post", "/chat", {"content": b"{" + b" " * 70_000 + b"}",
                                          "headers": {"content-type": "application/json"}}),
    ("not JSON at all", "post", "/parse-defect", {"content": b"hello", "headers": {"content-type": "application/json"}}),
    ("squawk text too short", "post", "/parse-defect", {"json": {"text": "hi"}}),
    ("bad engine id format", "get", "/predict-failure/ENGINE2", {}),
    ("unknown engine", "get", "/predict-failure/N999ZZ-E1", {}),
    ("unknown aircraft", "get", "/aircraft/N999ZZ", {}),
    ("unsafe session id", "post", "/chat/session", {"json": {"message": "hi", "session_id": "../../etc"}}),
]
shapes_ok = 0
for name, method, path, kwargs in cases:
    resp = getattr(client, method)(path, **kwargs)
    body = resp.json()
    shape_ok = set(body) == {"error"} and set(body["error"]) == {"code", "message"}
    shapes_ok += shape_ok and 400 <= resp.status_code < 500
    print(f"{resp.status_code}  {name:32s} {body['error']['code']:18s} {body['error']['message'][:60]}")
print(f"\n{shapes_ok}/{len(cases)} bad inputs got a 4xx with the standard error shape.")
