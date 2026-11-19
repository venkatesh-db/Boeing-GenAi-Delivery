# %% [markdown]
# # Lab 5.6 — Performance II: load test, latency percentiles, cache effect and cost per query
# Start the backend first:  uvicorn api.day5:app

# %%
import asyncio
import os
import statistics
import time

import httpx

API = os.getenv("API_URL", "http://localhost:8000")


async def hammer(path: str, payload: dict | None, n: int, concurrency: int) -> list[float]:
    sem = asyncio.Semaphore(concurrency)
    times: list[float] = []

    async def one(client: httpx.AsyncClient) -> None:
        async with sem:
            start = time.perf_counter()
            resp = await (client.post(path, json=payload) if payload else client.get(path))
            resp.raise_for_status()
            times.append((time.perf_counter() - start) * 1000)

    async with httpx.AsyncClient(base_url=API, timeout=600) as client:
        await asyncio.gather(*(one(client) for _ in range(n)))
    return sorted(times)


def report(label: str, times: list[float]) -> None:
    p95 = times[min(len(times) - 1, int(0.95 * len(times)))]
    print(f"{label:38s} n={len(times):3d}  p50={statistics.median(times):8.1f} ms  p95={p95:8.1f} ms")


# %% Load test of the deployed API
report("GET /health, 10 concurrent", asyncio.run(hammer("/health", None, 200, 10)))


def measure(label: str, path: str, payload: dict, n: int, concurrency: int) -> dict:
    """Latency from the client, tokens and cost from the server's /metrics (difference before/after)."""
    m0 = httpx.get(f"{API}/metrics").json()
    times = asyncio.run(hammer(path, payload, n, concurrency))
    m1 = httpx.get(f"{API}/metrics").json()
    report(label, times)
    return {"label": label, "p50_ms": statistics.median(times),
            "tokens_per_query": (m1["prompt_tokens"] + m1["completion_tokens"]
                                 - m0["prompt_tokens"] - m0["completion_tokens"]) / n,
            "cost_per_query": (m1["total_cost_usd"] - m0["total_cost_usd"]) / n,
            "cache_hits": m1["cache_hits"] - m0["cache_hits"]}


# %% Before / after: caching repeated answers (direct questions go to the mini model and are cached)
question = {"question": f"What does MEL stand for? (run {int(time.time())})", "role": "technician"}
rows = [measure("BEFORE: first call (no cache)", "/agent/run", question, 1, 1),
        measure("AFTER: same question x5 (cached)", "/agent/run", question, 5, 5)]

# %% Capstone query: full agent cost and latency per query
capstone = {"question": "Engine 2 on N123AB — is it at risk, and what should we do?", "role": "technician"}
rows.append(measure("Capstone query (4 tools + report)", "/agent/run", capstone, 1, 1))

# %% The table
print(f"\n{'scenario':36s}{'p50 ms':>10s}{'tokens/query':>14s}{'USD/query':>12s}{'cache hits':>12s}")
for r in rows:
    print(f"{r['label']:36s}{r['p50_ms']:>10.0f}{r['tokens_per_query']:>14.0f}{r['cost_per_query']:>12.5f}"
          f"{r['cache_hits']:>12d}")
print("Cost is $0 with a local model; with OpenAI the prices in aeroguard/tracing.py apply.")
print("Other levers used in the code: model routing (direct answers -> chat_model_mini), batched embeddings,")
print("trimmed context (only the top 3 chunks, 400 chars each, go to the report prompt).")

# %% Cost and latency summary from the server's tracing
print(httpx.get(f"{API}/metrics").json())
