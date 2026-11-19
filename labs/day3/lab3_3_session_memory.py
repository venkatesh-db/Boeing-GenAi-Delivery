# %% [markdown]
# # Lab 3.3 — Session memory per aircraft
# History is stored per session AND tail number, and trimmed so it fits the context window.

# %%
import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2] if "__file__" in globals() else Path.cwd().parents[1]
sys.path.insert(0, str(ROOT))
from aeroguard.app import create_app  # noqa: E402
from aeroguard.routers import sessions  # noqa: E402

client = TestClient(create_app(3))


def say(message: str, session_id: str | None, tail: str) -> dict:
    return client.post("/chat/session", json={"message": message, "session_id": session_id,
                                              "tail_number": tail}).json()


# %% 1. The assistant remembers earlier turns about the same aircraft
first = say("Engine 2 shows N1 vibration of 3.4 units in cruise. Remember this. Reply in one sentence.", None, "N123AB")
sid = first["session_id"]
second = say("Which engine did I report, and what was the vibration value? Answer in one short sentence.", sid, "N123AB")
print("Turn 2:", second["answer"])
print("Remembers engine and value:", "2" in second["answer"] and "3.4" in second["answer"])

# %% 2. Same session, different aircraft -> a separate history (no mixing aircraft)
print("History N123AB:", len(sessions._history(sessions._key(sid, "N123AB"))), "messages")
print("History N456CD:", len(sessions._history(sessions._key(sid, "N456CD"))), "messages (separate)")

# %% 3. Trimming: history never grows past MAX_TURNS pairs or MAX_HISTORY_CHARS
key = sessions._key("trim-demo", "N123AB")
for i in range(25):
    sessions._save_turn(key, f"question {i} " + "x" * 400, f"answer {i} " + "y" * 400)
kept = sessions._history(key)
print(f"Saved 25 turns, kept {len(kept) // 2} (limit {sessions.MAX_TURNS}); "
      f"{sum(len(m['content']) for m in kept):,} chars (limit {sessions.MAX_HISTORY_CHARS:,})")
print("Oldest kept:", kept[0]["content"][:12], "-> the oldest turns are dropped first")
