# %% [markdown]
# # Lab 1.2 — Intermediate Python on fleet data
# Comprehensions, *args/**kwargs, exceptions and file I/O
# on the training fleet.

# %%
import csv
import json
from pathlib import Path

HERE = Path(__file__) if "__file__" in globals() else None
ROOT = (HERE.resolve().parents[2] if HERE
        else Path.cwd().parents[1])
DATA = ROOT / "data"

# Quick refresher: variables, loops, lists, dicts
tails = ["N123AB", "N107BE"]
tails.append("N114CH")
aircraft = {"tail_number": "N123AB", "model": "737-800",
            "engines": 2}
for key, value in aircraft.items():
    print(key, "->", value)
print(len(tails), "tails:", tails)

# %% Read CSV files into lists of dicts
with open(DATA / "fleet.csv", newline="") as f:
    fleet = list(csv.DictReader(f))
with open(DATA / "maintenance_logs.csv", newline="") as f:
    logs = list(csv.DictReader(f))
print(len(fleet), "aircraft,", len(logs), "log entries")
first = fleet[0]
print(first["tail_number"], first["flight_hours"],
      type(first["flight_hours"]).__name__)

# %% Comprehensions: list, set, dict
critical = [r["log_id"] for r in logs
            if r["severity"] == "critical"]
print(len(critical), "critical write-ups, first:", critical[:3])

# The long way, for comparison: same result, four lines
critical_loop = []
for r in logs:
    if r["severity"] == "critical":
        critical_loop.append(r["log_id"])
assert critical_loop == critical

open_tails = sorted({r["tail_number"] for r in logs
                     if r["status"] == "open"})
print(len(open_tails), "aircraft with open defects:",
      open_tails[:4])

per_tail = {t: sum(1 for r in logs if r["tail_number"] == t)
            for t in open_tails[:3]}
print("Write-ups per aircraft:", per_tail)


# %% Functions: default arguments
def summarize(row, max_len=30):
    """One line per write-up. max_len has a default."""
    tail, ata = row["tail_number"], row["ata_chapter"]
    text = row["description"][:max_len]
    return f"{tail} ATA {ata}: {text}"


print(summarize(logs[0]))
print(summarize(logs[0], max_len=12))


# %% *args and **kwargs
def filter_defects(rows, *ata_chapters, **conditions):
    """Rows in any given ATA chapter matching every condition."""
    chapters = {str(c) for c in ata_chapters}
    return [
        r for r in rows
        if (not chapters or r["ata_chapter"] in chapters)
        and all(r.get(k) == v for k, v in conditions.items())
    ]


print(len(filter_defects(logs, 79)), "ATA 79 write-ups")
engine_critical = filter_defects(logs, 72, 79,
                                 severity="critical")
print(len(engine_critical), "critical engine / engine-oil")
n123 = filter_defects(logs, tail_number="N123AB", status="open")
print("N123AB open:", [r["log_id"] for r in n123])


# %% Exceptions: a custom exception for bad tail numbers
class InvalidTailNumber(ValueError):
    """Raised when a value is not a US registration."""


def parse_tail(value: str) -> str:
    value = value.strip().upper()
    ok = (value.startswith("N") and 2 <= len(value) <= 6
          and value[1].isdigit())
    if not ok:
        raise InvalidTailNumber(f"not a tail number: {value!r}")
    return value


checked = 0
for raw in ["n123ab", "XYZ", "N1234567"]:
    try:
        print("parsed", parse_tail(raw))
    except InvalidTailNumber as err:
        print("rejected:", err)
    finally:
        checked += 1  # runs on success and on failure
print("checked", checked, "values")

# %% Write JSON
out = ROOT / "storage" / "open_defects.json"
out.parent.mkdir(exist_ok=True)
payload = {"open_defect_aircraft": open_tails}
out.write_text(json.dumps(payload, indent=2))
print("Wrote", out.name)

# %% Read JSON back (round trip)
loaded = json.loads(out.read_text())
assert loaded["open_defect_aircraft"] == open_tails
print("Read back", len(loaded["open_defect_aircraft"]), "tails")

# %% Modules and packages: import, don't copy-paste
# aeroguard/ is a package (it has __init__.py);
# config.py is a module inside it.
import sys  # noqa: E402

sys.path.insert(0, str(ROOT))
from aeroguard import config  # noqa: E402

print("Imported:", config.__name__,
      "| data folder:", config.DATA_DIR.name)
