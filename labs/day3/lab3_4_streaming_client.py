# %% [markdown]
# # Lab 3.4 — Read the streaming endpoint and test session memory
# Start the backend first:  uvicorn api.day3:app --reload

# %%
import json
import os

import httpx

API = os.getenv("API_URL", "http://localhost:8000")


def ask(message: str, session_id: str | None = None) -> str | None:
    payload = {"message": message, "session_id": session_id, "tail_number": "N123AB"}
    with httpx.stream("POST", f"{API}/chat/stream", json=payload, timeout=300) as resp:
        for line in resp.iter_lines():
            if line.startswith("data:"):
                event = json.loads(line[5:])
                if event.get("done"):
                    print()
                    return event["session_id"]
                print(event["delta"], end="", flush=True)
    return None


# %% Turn 1 starts a session; turn 2 relies on memory ("it" = engine 2)
sid = ask("Engine 2 has recurring N1 vibration above 3 units. Remember that. Reply in one sentence.")
ask("Which engine did I say has the problem? Answer with the engine number only.", sid)
