# %% [markdown]
# # Lab 2.1 — Tokens, cost and temperature
# Tokenise maintenance write-ups, estimate cost for a mini vs
# a large model, and compare temperatures.

# %%
import sys
from pathlib import Path

import pandas as pd
import tiktoken

HERE = Path(__file__) if "__file__" in globals() else None
ROOT = (HERE.resolve().parents[2] if HERE
        else Path.cwd().parents[1])
sys.path.insert(0, str(ROOT))
from aeroguard import llm  # noqa: E402
from aeroguard.config import get_settings  # noqa: E402

logs = pd.read_csv(ROOT / "data" / "maintenance_logs.csv")
enc = tiktoken.get_encoding("o200k_base")  # recent OpenAI models

sample = logs["description"].iloc[0]
tokens = enc.encode(sample)
pieces = [enc.decode([t]) for t in tokens]
print(f"{sample!r}\n -> {len(tokens)} tokens: {pieces}")

# %% Cost for summarising 1,000 write-ups
# prompt ≈ system prompt + write-up; answer ≈ 60 tokens
n_tokens = logs["description"].map(lambda s: len(enc.encode(s)))
avg_in = 150 + n_tokens.mean()
avg_out = 60
# USD per 1M tokens (input, output); check current prices
prices = {"gpt-4.1-mini": (0.40, 1.60), "gpt-4.1": (2.00, 8.00)}
for model, (p_in, p_out) in prices.items():
    cost = 1000 * (avg_in * p_in + avg_out * p_out) / 1_000_000
    print(f"{model:13s} ≈ ${cost:.3f} per 1,000 write-ups")

# %% Temperature: same prompt, three runs at 0 and at 1
question = ("In one short sentence, name a likely cause of "
            "engine N1 vibration.")
prompt = [{"role": "user", "content": question}]
model = get_settings().chat_model
for temp in (0.0, 1.0):
    answers = {llm.chat(prompt, model=model, temperature=temp)
               for _ in range(3)}
    print(f"temperature={temp}: "
          f"{len(answers)} different answer(s)")
    for a in answers:
        print("   -", a.strip()[:120])

# %% top-p: at temperature 1, a low top_p keeps
# only the most likely tokens
for top_p in (0.1, 1.0):
    answers = {llm.chat(prompt, model=model, temperature=1.0,
                        top_p=top_p) for _ in range(3)}
    print(f"temperature=1.0 top_p={top_p}: "
          f"{len(answers)} different answer(s)")
print("Tip: change temperature OR top_p, not both. "
      "For maintenance text use temperature 0.")

# %% Context window: how much of our data fits in one prompt?
all_logs = sum(len(enc.encode(s)) for s in logs["description"])
docs = sum(len(enc.encode(p.read_text()))
           for p in (ROOT / "data" / "docs").glob("*.md"))
# Course data: 20 aircraft, ~1 year. A real operator: ~300
# aircraft, 10 years of logs and a 30,000-page manual (AMM).
real_fleet = all_logs * (300 / 20) * 10 + 30_000 * 600
needs = {"our logs": all_logs,
         "our logs + 12 documents": all_logs + docs,
         "real operator (estimate)": real_fleet}
for label, need in needs.items():
    fit = {w: f"{min(1.0, size / need):.0%}"
           for w, size in {"128k": 128_000, "8k": 8_192}.items()}
    print(f"{label:25s} {need:>12,.0f} tokens   "
          f"fits in 128k: {fit['128k']:>4}   "
          f"in 8k: {fit['8k']:>4}")
print("Whatever does not fit must be selected first: "
      "that is what RAG does on Day 4.")

# %% Model selection: latency of large vs mini on the same task
import time  # noqa: E402

s = get_settings()
task = [{"role": "user",
         "content": f"Summarise in one sentence: {sample}"}]
for label, name in {"large": s.chat_model,
                    "mini": s.chat_model_mini}.items():
    start = time.perf_counter()
    llm.chat(task, model=name, temperature=0)
    secs = time.perf_counter() - start
    print(f"{label:5s} {name:15s} {secs:5.1f} s")
if s.chat_model == s.chat_model_mini:
    print("Note: both names point to the same model here "
          f"({s.provider}). Compare on OpenAI "
          "to see a difference.")
print("Pick the smallest model that passes your quality checks: "
      "cheaper and usually faster.")
