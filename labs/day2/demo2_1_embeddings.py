# %% [markdown]
# # Demo 2.1 — Embeddings: meaning as numbers
# Session 1, trainer demo.
# An embedding turns text into a long list of numbers. Texts
# with similar meaning get similar numbers, even with different
# words. This is the idea behind search on Day 4 (RAG).

# %%
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__) if "__file__" in globals() else None
ROOT = (HERE.resolve().parents[2] if HERE
        else Path.cwd().parents[1])
sys.path.insert(0, str(ROOT))
from aeroguard import llm  # noqa: E402

texts = ["Engine 2 oil filter bypass message",
         "Engine 1 oil filter bypass message",
         "Engine 2 low oil pressure indication",
         "Main gear tire 2 cut found on walkaround"]
vectors = np.array(llm.embed(texts))
print("Each text becomes", vectors.shape[1], "numbers")

# %% Cosine similarity: 1.0 = same meaning, lower = less related
unit = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
similar = unit @ unit.T
for i, text in enumerate(texts[1:], start=1):
    print(f"{similar[0, i]:.2f}  {texts[0]!r} vs {text!r}")
