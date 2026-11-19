# %% [markdown]
# # Lab 4.3 — RAG with LangChain: loader -> splitter -> retriever -> chain
# Every answer must cite its sources; when the documents do not contain the answer, the assistant declines.

# %%
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if "__file__" in globals() else Path.cwd().parents[1]
sys.path.insert(0, str(ROOT))
from aeroguard.config import DOCS_DIR  # noqa: E402
from aeroguard.rag.chain import PROMPT, HybridRetriever, build_rag_chain  # noqa: E402
from aeroguard.rag.ingest import load_directory, split  # noqa: E402
from aeroguard.rag.qa import answer  # noqa: E402
from aeroguard.rag.store import build  # noqa: E402

# %% 1. Loader (LangChain TextLoader / PyPDFLoader) and splitter (RecursiveCharacterTextSplitter)
docs = load_directory(DOCS_DIR)
chunks = split(docs)
print(f"Loader: {len(docs)} documents   Splitter: {len(chunks)} chunks")

# %% 2. Retriever: a LangChain BaseRetriever over our hybrid search
kb = build()
retriever = HybridRetriever(kb=kb, k=3)
for d in retriever.invoke("What does AD 2026-TR-0102 require for bleed duct clamps?"):
    print("retrieved:", d.metadata["doc_id"], "|", d.page_content[:70].replace("\n", " "))

# %% 3. The chain: retriever -> sanitize + number sources -> prompt -> chat model
print(PROMPT.messages[0].prompt.template[:300], "...")
chain, _ = build_rag_chain(kb)
result = chain.invoke("What does AD 2026-TR-0102 require for bleed duct clamps?")
print("\nRaw chain answer:\n", result["answer"])
print("Sources offered:", [c["doc_id"] for c in result["citations"]])

# %% 4. With the policies on top: citations required, no-answer policy
QUESTIONS = [
    "What does AD 2026-TR-0102 require for bleed duct clamps?",         # answerable
    "How often must CFM56-7B fan blade roots be inspected?",            # answerable
    "What is the torque value for the A320 wing-to-body fairing bolts?",  # not in the documents
    "What is the capital of France?",                                    # off-topic
]
for q in QUESTIONS:
    r = answer(q, kb=kb)
    cited = ", ".join(f"[{c.source_id}] {c.doc_id}" for c in r.citations) or "-"
    print(f"\nQ: {q}\n   answered={r.answered}  citations: {cited}\n   {r.answer[:220]}")
