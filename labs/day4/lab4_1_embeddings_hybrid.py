# %% [markdown]
# # Labs 4.1 & 4.2 — Embeddings, chunking and hybrid search

# %%
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2] if "__file__" in globals() else Path.cwd().parents[1]
sys.path.insert(0, str(ROOT))
from aeroguard import llm  # noqa: E402
from aeroguard.config import DOCS_DIR  # noqa: E402
from aeroguard.rag.ingest import load_directory, split  # noqa: E402
from aeroguard.rag.store import build  # noqa: E402

# %% Embeddings: similar meaning -> similar vectors
sentences = ["Engine 2 vibration high in cruise", "N1 vibration above limits on the right engine",
             "Brake wear pin at limit"]
vectors = np.array(llm.embed(sentences))
vectors /= np.linalg.norm(vectors, axis=1, keepdims=True)
print("cosine similarity matrix:\n", (vectors @ vectors.T).round(2))

# %% Chunking with metadata
docs = load_directory(DOCS_DIR)
chunks = split(docs, chunk_size=700, chunk_overlap=100)
print(len(docs), "documents ->", len(chunks), "chunks")
print(chunks[0].metadata)  # AD number, aircraft model, ATA chapter, effective date, access level
print(chunks[0].page_content[:200])

# %% Vector vs keyword vs hybrid for an exact AD number and for a natural-language question
kb = build()
for query in ["AD 2026-TR-0103 hydraulic pump", "the engine shakes a lot during cruise, what should I check?"]:
    print("\n", query)
    for mode in ("vector", "keyword", "hybrid"):
        print(f"  {mode:8s}", [h.doc.metadata["doc_id"] for h in kb.search(query, k=3, mode=mode)])

# %% Lab 4.2 success check: the exact AD number
query, target = "AD 2026-TR-0103 hydraulic pump", "AD 2026-TR-0103"
for mode in ("vector", "hybrid"):
    ids = [h.doc.metadata["doc_id"] for h in kb.search(query, k=1, mode=mode)]
    print(f"{mode:7s} top-1 = {ids[0]:28s} -> {'FOUND' if ids[0] == target else 'missed'}")
print("Why: an AD number is a rare exact string. Keyword search (BM25) matches it; meaning-based vectors blur it.")
