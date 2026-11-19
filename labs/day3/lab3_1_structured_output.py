# %% [markdown]
# # Lab 3.1 — Structured output: squawk -> DefectRecord
# Parse real write-ups, validate with Pydantic, retry on invalid JSON, and measure the success rate.

# %%
import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2] if "__file__" in globals() else Path.cwd().parents[1]
sys.path.insert(0, str(ROOT))
from aeroguard import tracing  # noqa: E402
from aeroguard.routers.defects import parse_defect  # noqa: E402
from aeroguard.schemas import DefectRecord  # noqa: E402

print(DefectRecord.model_json_schema()["properties"].keys())

# %% What happens on invalid output? Pydantic gives a precise error; chat_json sends it back to the LLM and retries.
from pydantic import ValidationError  # noqa: E402

bad = '{"ata_chapter": 320, "component": "brake", "severity": "urgent", "recommended_action": "fix"}'
try:
    DefectRecord.model_validate_json(bad)
except ValidationError as err:
    print(f"{err.error_count()} errors - this exact text is sent back to the model on retry:\n{err}")

# %%
logs = pd.read_csv(ROOT / "data" / "maintenance_logs.csv").sample(20, random_state=3)
tracing.reset_metrics()
ok, ata_match, start = 0, 0, time.perf_counter()
for _, row in logs.iterrows():
    text = f"{row['tail_number']} {row['description']}"
    try:
        rec = parse_defect(text)
        ok += 1
        ata_match += rec.ata_chapter == row["ata_chapter"]
        print(f"OK   ATA {rec.ata_chapter:>2} (truth {row['ata_chapter']}) {rec.severity:8s} {text}")
    except ValueError as err:
        print("FAIL", text, "->", err)
print(f"Valid records: {ok}/{len(logs)}, ATA correct: {ata_match}/{len(logs)}, "
      f"{(time.perf_counter() - start) / len(logs):.1f}s per record")
calls = tracing.metrics_summary()["llm_calls"]
print(f"Schema validation rate: {ok / len(logs):.0%}  |  LLM calls: {calls} for {len(logs)} records "
      f"-> {calls - len(logs)} retries needed")
