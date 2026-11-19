# %% [markdown]
# # Lab 4.6 — Performance I: measure retrieval quality and speed, then tune
# recall@k: did the right document appear in the top k?  MRR: how high was it ranked?
#
# Measured on a Mac with the local llama3 model (LLM_PROVIDER=ollama):
#   vector recall@4 0.44-0.64, keyword 1.00, hybrid 0.76-0.92; index build 10.4s cold vs 0.11s cached.
# llama3 is a chat model, not an embedding model, so its vectors are weak. Re-run with OpenAI
# text-embedding-3-small and compare: the point of the lab is to measure, not to assume.
# Note: the first configuration's vector latency includes embedding the questions; later runs hit the cache.

# %%
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if "__file__" in globals() else Path.cwd().parents[1]
sys.path.insert(0, str(ROOT))
from aeroguard.rag.store import build  # noqa: E402

EVAL = [
    ("What must be done if N1 vibration exceeds 3.0 units on a 737-800?", "AD 2026-TR-0101"),
    ("How often must CFM56-7B fan blade roots be inspected?", "AD 2026-TR-0101"),
    ("Which clamps must be replaced on the 737 MAX bleed duct?", "AD 2026-TR-0102"),
    ("What to do after a duct overheat message on a 737 MAX 8?", "AD 2026-TR-0102"),
    ("How often is the 787 hydraulic case drain filter inspected?", "AD 2026-TR-0103"),
    ("What inspection is needed on 777-300ER main gear axles?", "AD 2026-TR-0104"),
    ("When must the oil pressure transmitter be replaced?", "AD 2026-TR-0105"),
    ("What must a maintenance record contain?", "14 CFR 43.9 (summary)"),
    ("Who is responsible for compliance with airworthiness directives at an air carrier?", "14 CFR 121.363-121.380 (summary)"),
    ("Engine vibration troubleshooting procedure and borescope inspection", "AMM 72-00-00 TS-801"),
    ("Nose gear shimmy damper and torque link check", "AMM 32-42-00 TS-802"),
    ("Hydraulic pressure fluctuates more than 300 psi", "AMM 29-11-00 TS-803"),
    ("Low oil pressure indication: how to check with a test gauge", "AMM 79-31-00 TS-804"),
    ("AD 2026-TR-0104", "AD 2026-TR-0104"),
    ("What is the unsafe condition behind the fan blade directive?", "AD 2026-TR-0101"),
    ("Replace any blade with a crack indication before further flight", "AD 2026-TR-0101"),
    ("Hot air leaks and loose V-band clamps", "AD 2026-TR-0102"),
    ("Metal particles found in the hydraulic pump filter", "AD 2026-TR-0103"),
    ("Corrosion under axle chrome plating", "AD 2026-TR-0104"),
    ("False low oil pressure indication causing an unnecessary engine shutdown", "AD 2026-TR-0105"),
    ("What must an inspection record include, such as total time in service?", "14 CFR 43.9 (summary)"),
    ("Continuing analysis and surveillance system for recurring defects", "14 CFR 121.363-121.380 (summary)"),
    ("Brake wear pin flush with the housing", "AMM 32-42-00 TS-802"),
    ("Engine ground run vibration limit for return to service", "AMM 72-00-00 TS-801"),
    ("Check hydraulic reservoir fluid level and pressurisation", "AMM 29-11-00 TS-803"),
]
assert len(EVAL) == 25


def evaluate(kb, mode: str, k: int = 4) -> dict:
    found, rr, times = 0, 0.0, []
    for question, expected in EVAL:
        start = time.perf_counter()
        ids = [h.doc.metadata["doc_id"] for h in kb.search(question, k=k, mode=mode)]
        times.append((time.perf_counter() - start) * 1000)
        if expected in ids:
            found += 1
            rr += 1 / (ids.index(expected) + 1)
    return {"recall@k": round(found / len(EVAL), 2), "MRR": round(rr / len(EVAL), 2),
            "p50_ms": round(statistics.median(times), 1)}


# %% Compare chunk sizes and retrieval modes
results = {}
for size, overlap in [(300, 50), (700, 100), (1200, 150)]:
    kb = build(chunk_size=size, chunk_overlap=overlap)
    print(f"\nchunk_size={size} overlap={overlap}: {len(kb.chunks)} chunks, index built in {kb.build_seconds:.1f}s")
    for mode in ("vector", "keyword", "hybrid"):
        results[(size, mode)] = evaluate(kb, mode)
        print(f"  {mode:8s}", results[(size, mode)])

# %% Before / after table (the lab's success criterion)
before = results[(700, "vector")]  # starting point: vector-only search, default chunks
best_size, best_mode = max(((s, m) for s, m in results if m == "hybrid"), key=lambda key: results[key]["MRR"])
after = results[(best_size, best_mode)]
print(f"\n{'':28s}{'recall@4':>9s}{'MRR':>7s}")
print(f"{'BEFORE vector, chunk 700':28s}{before['recall@k']:>9.2f}{before['MRR']:>7.2f}")
print(f"{f'AFTER  hybrid, chunk {best_size}':28s}{after['recall@k']:>9.2f}{after['MRR']:>7.2f}")
print(f"Improvement: recall +{after['recall@k'] - before['recall@k']:.2f}, MRR +{after['MRR'] - before['MRR']:.2f}")

# %% Caching: rebuild with and without the embedding cache
start = time.perf_counter()
build(use_cache=False)
cold = time.perf_counter() - start
start = time.perf_counter()
build(use_cache=True)
warm = time.perf_counter() - start
print(f"\nIndex build without cache {cold:.1f}s, with cache {warm:.2f}s")

# %% Query caching: the question's embedding is cached too, so a repeated question is cheaper
import uuid  # noqa: E402

kb = build(use_cache=True)
q = f"Brand-new question about bleed duct clamps on the MAX (run {uuid.uuid4().hex[:6]})"
for label in ("first time", "repeated"):
    start = time.perf_counter()
    kb.search(q, k=4, mode="vector")
    print(f"query {label:10s} {(time.perf_counter() - start) * 1000:7.1f} ms")
