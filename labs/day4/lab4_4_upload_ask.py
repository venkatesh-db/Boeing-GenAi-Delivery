# %% [markdown]
# # Lab 4.4 — Milestone 3: /upload and /ask
# Upload a new document and ask about it straight away. TestClient runs the API in-process (no server needed).

# %%
import sys
import uuid
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2] if "__file__" in globals() else Path.cwd().parents[1]
sys.path.insert(0, str(ROOT))
from aeroguard.app import create_app  # noqa: E402

client = TestClient(create_app(4))
code = f"SB-{uuid.uuid4().hex[:4].upper()}"   # a fact that exists only in our new document
page = f"""---
doc_id: Service Bulletin {code}
doc_type: service_bulletin
aircraft_model: 737-800
ata_chapter: 30
---
# Service Bulletin {code} — Pitot probe heater check (TRAINING SAMPLE)
## Action
Measure pitot probe heater resistance every 600 flight hours. Replace the probe if resistance is above 45 ohms.
"""

# %% 1. Before the upload the assistant cannot answer
question = f"Under Service Bulletin {code}, when must the pitot probe be replaced?"
print("Before upload:", client.post("/ask", json={"question": question}).json()["answer"][:120])

# %% 2. Upload, then ask again: the new document is searchable immediately
up = client.post("/upload", files={"file": ("pitot_sb.md", page.encode())}).json()
print("Uploaded:", up)
after = client.post("/ask", json={"question": question}).json()
print("After upload:", after["answer"])
print("Citations:", [(c["source_id"], c["doc_id"]) for c in after["citations"]])
print("Cites the uploaded bulletin:", any(code in c["doc_id"] for c in after["citations"]))

# %% 3. Upload rules: only .md / .txt / .pdf, at most 2 MB
bad = client.post("/upload", files={"file": ("macro.exe", b"MZ...")})
print("\n.exe upload ->", bad.status_code, bad.json()["error"]["message"])
